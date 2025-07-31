from typing import List
from langchain.tools import BaseTool
from .base_agent import BaseHRAgent


class RoleDefinitionAgent(BaseHRAgent):
    """Agent responsible for defining and scoping job roles."""
    
    def __init__(self, tools: List[BaseTool]):
        super().__init__(
            name="Role Definition Agent",
            description="Helps define job roles, responsibilities, and requirements",
            tools=tools,
            temperature=0.3  # Lower temperature for more focused outputs
        )
    
    def get_system_message(self) -> str:
        from .enhanced_prompts import EnhancedPrompts
        return EnhancedPrompts.role_definition_prompt()