from typing import List
from langchain.tools import BaseTool
from .base_agent import BaseHRAgent


class JDGeneratorAgent(BaseHRAgent):
    """Agent responsible for generating job descriptions."""
    
    def __init__(self, tools: List[BaseTool]):
        super().__init__(
            name="JD Generator Agent",
            description="Creates compelling and comprehensive job descriptions",
            tools=tools,
            temperature=0.7  # Balanced temperature for creativity and accuracy
        )
    
    def get_system_message(self) -> str:
        from .enhanced_prompts import EnhancedPrompts
        return EnhancedPrompts.jd_generator_prompt()