from typing import List
from langchain.tools import BaseTool
from .base_agent import BaseHRAgent


class InterviewPlannerAgent(BaseHRAgent):
    """Agent responsible for planning interview stages and processes."""
    
    def __init__(self, tools: List[BaseTool]):
        super().__init__(
            name="Interview Planner Agent",
            description="Designs comprehensive interview processes and evaluation criteria",
            tools=tools,
            temperature=0.4  # Lower temperature for structured planning
        )
    
    def get_system_message(self) -> str:
        from .enhanced_prompts import EnhancedPrompts
        return EnhancedPrompts.interview_planner_prompt()