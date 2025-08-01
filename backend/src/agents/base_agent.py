from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import BaseTool
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class BaseHRAgent(ABC):
    """Base class for all HR hiring process agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        tools: List[BaseTool],
        llm: Optional[ChatOpenAI] = None,
        memory_window_size: int = 10,
        temperature: float = 0.7,
    ):
        self.name = name
        self.description = description
        self.tools = tools
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = llm or ChatOpenAI(
            temperature=temperature,
            model="gpt-3.5-turbo"
        )
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=memory_window_size,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Create the agent
        self.agent_executor = self._create_agent()
    
    @abstractmethod
    def get_system_message(self) -> str:
        """Get the system message for this agent."""
        pass
    
    def _create_agent(self) -> AgentExecutor:
        """Create the agent executor with tools and memory."""
        system_message = self.get_system_message()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    async def arun(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """Asynchronously run the agent with the given input."""
        try:
            result = await self.agent_executor.ainvoke(
                {"input": input_text},
                **kwargs
            )
            return {
                "success": True,
                "output": result.get("output", ""),
                "agent": self.name
            }
        except Exception as e:
            logger.error(f"Error in {self.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def run(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """Synchronously run the agent with the given input."""
        try:
            result = self.agent_executor.invoke(
                {"input": input_text},
                **kwargs
            )
            return {
                "success": True,
                "output": result.get("output", ""),
                "agent": self.name
            }
        except Exception as e:
            logger.error(f"Error in {self.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def clear_memory(self):
        """Clear the agent's conversation memory."""
        self.memory.clear()