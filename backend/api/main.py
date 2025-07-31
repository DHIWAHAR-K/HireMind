from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import os
from datetime import datetime
import logging

from src.workflows import HiringWorkflow
from src.memory import RedisMemoryStore
from src.models import HiringProfile
from src.agents import RoleDefinitionAgent, JDGeneratorAgent, InterviewPlannerAgent
from src.tools import get_all_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HireMind API",
    description="AI-powered HR hiring process planning API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis memory store
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
memory_store = RedisMemoryStore(redis_url=redis_url)

# Initialize workflow
workflow = HiringWorkflow()

# Initialize individual agents
tools = get_all_tools()
agents = {
    "role_definition": RoleDefinitionAgent(tools),
    "jd_generator": JDGeneratorAgent(tools),
    "interview_planner": InterviewPlannerAgent(tools),
}


# Request/Response Models
class WorkflowStartRequest(BaseModel):
    description: str
    company_name: str = "[Company Name]"
    department: Optional[str] = None
    session_id: Optional[str] = None


class WorkflowResponse(BaseModel):
    session_id: str
    status: str
    current_stage: str
    completed_stages: List[str]
    results: Dict[str, Any]
    error: Optional[str] = None


class AgentRequest(BaseModel):
    agent_type: str
    input_text: str
    session_id: Optional[str] = None


class AgentResponse(BaseModel):
    success: bool
    output: str
    agent: str
    session_id: str
    error: Optional[str] = None


class ProfileListResponse(BaseModel):
    profiles: List[Dict[str, Any]]
    total: int


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to HireMind API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/workflow/start", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowStartRequest, background_tasks: BackgroundTasks):
    """Start a new hiring workflow."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Set up workflow for progress tracking
        workflow.redis_memory = memory_store
        workflow.current_session_id = session_id
        
        # Run workflow
        result = await workflow.arun(
            user_input=request.description,
            company_name=request.company_name,
            department=request.department,
            thread_id=session_id
        )
        
        # Save to Redis
        if result["success"]:
            memory_store.save_workflow_state(session_id, result)
            
            # Create hiring profile
            profile = {
                "role_title": "Extracted from description",  # TODO: Extract from result
                "department": "Unknown",
                "status": "active",
                **result
            }
            memory_store.save_hiring_profile(session_id, profile)
        
        return WorkflowResponse(
            session_id=session_id,
            status="completed" if result["success"] else "failed",
            current_stage="completed" if result["success"] else "error",
            completed_stages=result.get("completed_stages", []),
            results=result,
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflow/{session_id}", response_model=WorkflowResponse)
async def get_workflow_status(session_id: str):
    """Get workflow status and results."""
    try:
        # Load from Redis
        state = memory_store.load_workflow_state(session_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return WorkflowResponse(
            session_id=session_id,
            status="completed" if state.get("completed_stages") and len(state.get("completed_stages", [])) >= 6 else "processing",
            current_stage=state.get("current_stage") or "role_definition",
            completed_stages=state.get("completed_stages", []),
            results=state,
            error=state.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """Run a specific agent."""
    try:
        # Validate agent type
        if request.agent_type not in agents:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent type. Must be one of: {list(agents.keys())}"
            )
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get agent
        agent = agents[request.agent_type]
        
        # Run agent
        result = agent.run(request.input_text)
        
        # Save conversation if successful
        if result["success"] and memory_store:
            # Save to conversation history
            from langchain_core.messages import HumanMessage, AIMessage
            messages = [
                HumanMessage(content=request.input_text),
                AIMessage(content=result["output"])
            ]
            memory_store.save_conversation(session_id, messages)
        
        return AgentResponse(
            success=result["success"],
            output=result.get("output", ""),
            agent=request.agent_type,
            session_id=session_id,
            error=result.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profiles", response_model=ProfileListResponse)
async def list_profiles(limit: int = 10):
    """List recent hiring profiles."""
    try:
        profiles = memory_store.list_recent_profiles(limit=limit)
        
        return ProfileListResponse(
            profiles=profiles,
            total=len(profiles)
        )
        
    except Exception as e:
        logger.error(f"Error listing profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profiles/{session_id}")
async def get_profile(session_id: str):
    """Get a specific hiring profile."""
    try:
        profile = memory_store.load_hiring_profile(session_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/profiles/{session_id}")
async def delete_profile(session_id: str):
    """Delete a hiring profile."""
    try:
        success = memory_store.clear_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return {"message": "Profile deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check Redis connection
        redis_status = "connected" if memory_store.redis_client else "disconnected"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "running",
                "redis": redis_status
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)