import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import redis
from redis.exceptions import RedisError
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class RedisMemoryStore:
    """Redis-based memory storage for conversation history and state."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        key_prefix: str = "hiremind",
        ttl: int = 86400  # 24 hours default TTL
    ):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.ttl = ttl
        self._connect()
    
    def _connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Fallback to in-memory storage
            self.redis_client = None
    
    def _get_key(self, session_id: str, key_type: str) -> str:
        """Generate Redis key."""
        return f"{self.key_prefix}:{session_id}:{key_type}"
    
    def save_conversation(
        self,
        session_id: str,
        messages: List[BaseMessage]
    ) -> bool:
        """Save conversation history."""
        if not self.redis_client:
            return False
        
        try:
            key = self._get_key(session_id, "conversation")
            
            # Convert messages to JSON-serializable format
            messages_data = []
            for msg in messages:
                messages_data.append({
                    "type": msg.__class__.__name__,
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                })
            
            self.redis_client.setex(
                key,
                self.ttl,
                json.dumps(messages_data)
            )
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return False
    
    def load_conversation(self, session_id: str) -> List[BaseMessage]:
        """Load conversation history."""
        if not self.redis_client:
            return []
        
        try:
            key = self._get_key(session_id, "conversation")
            data = self.redis_client.get(key)
            
            if not data:
                return []
            
            messages_data = json.loads(data)
            messages = []
            
            for msg_data in messages_data:
                if msg_data["type"] == "HumanMessage":
                    messages.append(HumanMessage(content=msg_data["content"]))
                elif msg_data["type"] == "AIMessage":
                    messages.append(AIMessage(content=msg_data["content"]))
            
            return messages
            
        except Exception as e:
            logger.error(f"Error loading conversation: {e}")
            return []
    
    def save_workflow_state(
        self,
        session_id: str,
        state: Dict[str, Any]
    ) -> bool:
        """Save workflow state."""
        if not self.redis_client:
            return False
        
        try:
            key = self._get_key(session_id, "workflow_state")
            
            # Convert state to JSON-serializable format
            state_data = {
                "current_stage": state.get("current_stage"),
                "completed_stages": state.get("completed_stages", []),
                "role_definition": state.get("role_definition"),
                "job_description": state.get("job_description"),
                "interview_plan": state.get("interview_plan"),
                "timeline": state.get("timeline"),
                "salary_benchmark": state.get("salary_benchmark"),
                "offer_letter": state.get("offer_letter"),
                "timestamp": datetime.now().isoformat()
            }
            
            self.redis_client.setex(
                key,
                self.ttl,
                json.dumps(state_data)
            )
            return True
            
        except Exception as e:
            logger.error(f"Error saving workflow state: {e}")
            return False
    
    def load_workflow_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state."""
        if not self.redis_client:
            return None
        
        try:
            key = self._get_key(session_id, "workflow_state")
            data = self.redis_client.get(key)
            
            if not data:
                return None
            
            return json.loads(data)
            
        except Exception as e:
            logger.error(f"Error loading workflow state: {e}")
            return None
    
    def save_hiring_profile(
        self,
        session_id: str,
        profile: Dict[str, Any]
    ) -> bool:
        """Save complete hiring profile."""
        if not self.redis_client:
            return False
        
        try:
            key = self._get_key(session_id, "hiring_profile")
            
            profile_data = {
                **profile,
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Store in Redis with longer TTL for profiles
            self.redis_client.setex(
                key,
                self.ttl * 30,  # 30 days for profiles
                json.dumps(profile_data)
            )
            
            # Also add to profiles list
            list_key = f"{self.key_prefix}:profiles"
            self.redis_client.lpush(list_key, session_id)
            self.redis_client.ltrim(list_key, 0, 99)  # Keep last 100 profiles
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving hiring profile: {e}")
            return False
    
    def load_hiring_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load hiring profile."""
        if not self.redis_client:
            return None
        
        try:
            key = self._get_key(session_id, "hiring_profile")
            data = self.redis_client.get(key)
            
            if not data:
                return None
            
            return json.loads(data)
            
        except Exception as e:
            logger.error(f"Error loading hiring profile: {e}")
            return None
    
    def list_recent_profiles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent hiring profiles."""
        if not self.redis_client:
            return []
        
        try:
            list_key = f"{self.key_prefix}:profiles"
            session_ids = self.redis_client.lrange(list_key, 0, limit - 1)
            
            profiles = []
            for session_id in session_ids:
                profile = self.load_hiring_profile(session_id)
                if profile:
                    profiles.append({
                        "session_id": session_id,
                        "role_title": profile.get("role_title", "Unknown"),
                        "department": profile.get("department", "Unknown"),
                        "created_at": profile.get("created_at"),
                        "status": profile.get("status", "In Progress")
                    })
            
            return profiles
            
        except Exception as e:
            logger.error(f"Error listing profiles: {e}")
            return []
    
    def clear_session(self, session_id: str) -> bool:
        """Clear all data for a session."""
        if not self.redis_client:
            return False
        
        try:
            keys = [
                self._get_key(session_id, "conversation"),
                self._get_key(session_id, "workflow_state"),
                self._get_key(session_id, "hiring_profile")
            ]
            
            for key in keys:
                self.redis_client.delete(key)
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            return False


class EnhancedConversationMemory(ConversationSummaryBufferMemory):
    """Enhanced conversation memory with Redis persistence."""
    
    def __init__(
        self,
        llm: ChatOpenAI,
        redis_store: Optional[RedisMemoryStore] = None,
        session_id: Optional[str] = None,
        max_token_limit: int = 2000,
        **kwargs
    ):
        super().__init__(
            llm=llm,
            max_token_limit=max_token_limit,
            **kwargs
        )
        self.redis_store = redis_store
        self.session_id = session_id
        
        # Load existing conversation if available
        if redis_store and session_id:
            messages = redis_store.load_conversation(session_id)
            if messages:
                for msg in messages:
                    self.chat_memory.add_message(msg)
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context to memory and Redis."""
        super().save_context(inputs, outputs)
        
        # Persist to Redis
        if self.redis_store and self.session_id:
            self.redis_store.save_conversation(
                self.session_id,
                self.chat_memory.messages
            )
    
    def clear(self) -> None:
        """Clear memory and Redis storage."""
        super().clear()
        
        if self.redis_store and self.session_id:
            self.redis_store.clear_session(self.session_id)