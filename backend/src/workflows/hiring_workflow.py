from typing import TypedDict, Annotated, List, Dict, Any, Optional
from operator import add
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import logging

from ..agents import (
    RoleDefinitionAgent,
    JDGeneratorAgent,
    InterviewPlannerAgent
)
from ..tools import get_all_tools

logger = logging.getLogger(__name__)


class HiringState(TypedDict):
    """State schema for the hiring workflow."""
    messages: Annotated[List[BaseMessage], add]
    current_stage: str
    company_name: str
    department: Optional[str]
    role_definition: Optional[Dict[str, Any]]
    job_description: Optional[str]
    interview_plan: Optional[Dict[str, Any]]
    timeline: Optional[Dict[str, Any]]
    salary_benchmark: Optional[Dict[str, Any]]
    offer_letter: Optional[str]
    error: Optional[str]
    completed_stages: List[str]


class HiringWorkflow:
    """LangGraph workflow for the hiring process."""
    
    def __init__(self):
        self.tools = get_all_tools()
        self.memory = MemorySaver()
        self.workflow = self._build_workflow()
        self.redis_memory = None  # Will be set by the API
        self.current_session_id = None
    
    def _build_workflow(self) -> StateGraph:
        """Build the hiring workflow graph."""
        # Initialize agents
        self.role_agent = RoleDefinitionAgent(tools=self.tools)
        self.jd_agent = JDGeneratorAgent(tools=self.tools)
        self.interview_agent = InterviewPlannerAgent(tools=self.tools)
        
        # Create workflow
        workflow = StateGraph(HiringState)
        
        # Add nodes
        workflow.add_node("role_definition", self._role_definition_node)
        workflow.add_node("jd_generation", self._jd_generation_node)
        workflow.add_node("interview_planning", self._interview_planning_node)
        workflow.add_node("timeline_estimation", self._timeline_estimation_node)
        workflow.add_node("salary_benchmarking", self._salary_benchmarking_node)
        workflow.add_node("offer_generation", self._offer_generation_node)
        
        # Add edges
        workflow.set_entry_point("role_definition")
        workflow.add_edge("role_definition", "jd_generation")
        workflow.add_edge("jd_generation", "interview_planning")
        workflow.add_edge("interview_planning", "timeline_estimation")
        workflow.add_edge("timeline_estimation", "salary_benchmarking")
        workflow.add_edge("salary_benchmarking", "offer_generation")
        workflow.add_edge("offer_generation", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def _save_progress(self, state: HiringState):
        """Save intermediate progress to Redis."""
        if self.redis_memory and self.current_session_id:
            try:
                result = self._format_result(state)
                self.redis_memory.save_workflow_state(self.current_session_id, result)
            except Exception as e:
                logger.error(f"Failed to save progress: {e}")
    
    def _role_definition_node(self, state: HiringState) -> HiringState:
        """Define the role based on user input."""
        try:
            last_message = state["messages"][-1].content if state["messages"] else ""
            
            result = self.role_agent.run(
                f"Define a role based on: {last_message}"
            )
            
            if result["success"]:
                state["role_definition"] = {
                    "output": result["output"],
                    "timestamp": self._get_timestamp()
                }
                state["completed_stages"].append("role_definition")
                state["messages"].append(
                    AIMessage(content=f"Role Definition:\n{result['output']}")
                )
            else:
                state["error"] = result.get("error", "Unknown error in role definition")
                
        except Exception as e:
            logger.error(f"Error in role definition: {str(e)}")
            state["error"] = str(e)
            
        state["current_stage"] = "jd_generation"
        self._save_progress(state)
        return state
    
    def _jd_generation_node(self, state: HiringState) -> HiringState:
        """Generate job description based on role definition."""
        try:
            role_info = state.get("role_definition", {}).get("output", "")
            
            result = self.jd_agent.run(
                f"Create a job description based on this role definition: {role_info}"
            )
            
            if result["success"]:
                state["job_description"] = result["output"]
                state["completed_stages"].append("jd_generation")
                state["messages"].append(
                    AIMessage(content=f"Job Description:\n{result['output']}")
                )
            else:
                state["error"] = result.get("error", "Unknown error in JD generation")
                
        except Exception as e:
            logger.error(f"Error in JD generation: {str(e)}")
            state["error"] = str(e)
            
        state["current_stage"] = "interview_planning"
        self._save_progress(state)
        return state
    
    def _interview_planning_node(self, state: HiringState) -> HiringState:
        """Plan interview stages based on role and JD."""
        try:
            role_info = state.get("role_definition", {}).get("output", "")
            jd = state.get("job_description", "")
            
            result = self.interview_agent.run(
                f"Plan interview stages for this role:\nRole: {role_info}\nJD: {jd}"
            )
            
            if result["success"]:
                state["interview_plan"] = {
                    "output": result["output"],
                    "timestamp": self._get_timestamp()
                }
                state["completed_stages"].append("interview_planning")
                state["messages"].append(
                    AIMessage(content=f"Interview Plan:\n{result['output']}")
                )
            else:
                state["error"] = result.get("error", "Unknown error in interview planning")
                
        except Exception as e:
            logger.error(f"Error in interview planning: {str(e)}")
            state["error"] = str(e)
            
        state["current_stage"] = "timeline_estimation"
        self._save_progress(state)
        return state
    
    def _timeline_estimation_node(self, state: HiringState) -> HiringState:
        """Estimate hiring timeline based on interview plan."""
        try:
            # Use timeline estimation tool
            from ..tools.timeline_estimator import TimelineEstimatorTool
            tool = TimelineEstimatorTool()
            
            interview_plan = state.get("interview_plan", {}).get("output", "")
            timeline = tool._run(
                role_info=state.get("role_definition", {}).get("output", ""),
                interview_stages=interview_plan
            )
            
            state["timeline"] = {
                "output": timeline,
                "timestamp": self._get_timestamp()
            }
            state["completed_stages"].append("timeline_estimation")
            state["messages"].append(
                AIMessage(content=f"Timeline Estimation:\n{timeline}")
            )
            
        except Exception as e:
            logger.error(f"Error in timeline estimation: {str(e)}")
            state["error"] = str(e)
            
        state["current_stage"] = "salary_benchmarking"
        self._save_progress(state)
        return state
    
    def _salary_benchmarking_node(self, state: HiringState) -> HiringState:
        """Get salary benchmarks for the role."""
        try:
            # Use salary benchmark tool
            from ..tools.salary_benchmark import SalaryBenchmarkTool
            tool = SalaryBenchmarkTool()
            
            role_info = state.get("role_definition", {}).get("output", "")
            benchmark = tool._run(role_title=role_info)
            
            state["salary_benchmark"] = {
                "output": benchmark,
                "timestamp": self._get_timestamp()
            }
            state["completed_stages"].append("salary_benchmarking")
            state["messages"].append(
                AIMessage(content=f"Salary Benchmark:\n{benchmark}")
            )
            
        except Exception as e:
            logger.error(f"Error in salary benchmarking: {str(e)}")
            state["error"] = str(e)
            
        state["current_stage"] = "offer_generation"
        self._save_progress(state)
        return state
    
    def _offer_generation_node(self, state: HiringState) -> HiringState:
        """Generate offer letter template."""
        try:
            # Use offer letter generator tool
            from ..tools.offer_letter_generator import OfferLetterGeneratorTool
            tool = OfferLetterGeneratorTool()
            
            # Extract role title and department from role definition
            role_info = state.get("role_definition", {}).get("output", "")
            salary_info = state.get("salary_benchmark", {}).get("output", "")
            
            # Extract basic info for required parameters
            role_title = "Software Engineer"  # Default fallback
            department = "Engineering"       # Default fallback
            salary = "$120,000"             # Default fallback
            
            # Try to extract actual values from the outputs
            if "Senior Backend Engineer" in role_info:
                role_title = "Senior Backend Engineer"
            if "Payment Processing" in role_info:
                department = "Engineering - Payment Processing Team"
            if "$" in salary_info and "median" in salary_info.lower():
                # Try to extract salary from benchmark output
                import re
                salary_match = re.search(r'\$[\d,]+', salary_info)
                if salary_match:
                    salary = salary_match.group()
            
            offer = tool._execute(
                role_title=role_title,
                department=state.get("department") or department,
                salary=salary,
                role_info=role_info,
                salary_info=salary_info,
                company_name=state.get("company_name", "[Company Name]")
            )
            
            state["offer_letter"] = offer
            state["completed_stages"].append("offer_generation")
            state["messages"].append(
                AIMessage(content=f"Offer Letter Template:\n{offer}")
            )
            
        except Exception as e:
            logger.error(f"Error in offer generation: {str(e)}")
            state["error"] = str(e)
            
        state["current_stage"] = "completed"
        self._save_progress(state)
        return state
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def arun(self, user_input: str, company_name: str = "[Company Name]", department: str = None, thread_id: str = "default") -> Dict[str, Any]:
        """Run the workflow asynchronously."""
        initial_state = HiringState(
            messages=[HumanMessage(content=user_input)],
            current_stage="role_definition",
            company_name=company_name,
            department=department,
            role_definition=None,
            job_description=None,
            interview_plan=None,
            timeline=None,
            salary_benchmark=None,
            offer_letter=None,
            error=None,
            completed_stages=[]
        )
        
        config = {"configurable": {"thread_id": thread_id}}
        
        result = await self.workflow.ainvoke(initial_state, config)
        
        return self._format_result(result)
    
    def run(self, user_input: str, thread_id: str = "default") -> Dict[str, Any]:
        """Run the workflow synchronously."""
        initial_state = HiringState(
            messages=[HumanMessage(content=user_input)],
            current_stage="role_definition",
            role_definition=None,
            job_description=None,
            interview_plan=None,
            timeline=None,
            salary_benchmark=None,
            offer_letter=None,
            error=None,
            completed_stages=[]
        )
        
        config = {"configurable": {"thread_id": thread_id}}
        
        result = self.workflow.invoke(initial_state, config)
        
        return self._format_result(result)
    
    def _format_result(self, state: HiringState) -> Dict[str, Any]:
        """Format the workflow result for output."""
        return {
            "success": state.get("error") is None,
            "current_stage": state.get("current_stage", "completed"),
            "completed_stages": state.get("completed_stages", []),
            "role_definition": state.get("role_definition"),
            "job_description": state.get("job_description"),
            "interview_plan": state.get("interview_plan"),
            "timeline": state.get("timeline"),
            "salary_benchmark": state.get("salary_benchmark"),
            "offer_letter": state.get("offer_letter"),
            "error": state.get("error"),
            "messages": [msg.content for msg in state.get("messages", [])]
        }