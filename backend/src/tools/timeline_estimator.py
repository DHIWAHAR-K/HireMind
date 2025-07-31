from typing import Optional, Type, Dict
from pydantic import BaseModel, Field
from .base_tool import BaseHRTool
from datetime import datetime, timedelta
import json


class TimelineEstimatorInput(BaseModel):
    """Input schema for Timeline Estimator tool."""
    role_info: str = Field(description="Information about the role")
    interview_stages: str = Field(description="Number and type of interview stages")
    urgency: str = Field(default="normal", description="Hiring urgency: urgent, normal, or relaxed")
    team_availability: str = Field(default="normal", description="Team availability: high, normal, or low")


class TimelineEstimatorTool(BaseHRTool):
    """Tool for estimating hiring timeline."""
    
    name: str = "timeline_estimator"
    description: str = "Estimate the hiring timeline based on role complexity and interview stages"
    args_schema: Type[BaseModel] = TimelineEstimatorInput
    
    def _execute(
        self,
        role_info: str,
        interview_stages: str,
        urgency: str = "normal",
        team_availability: str = "normal"
    ) -> str:
        """Estimate hiring timeline."""
        
        # Parse interview stages
        stage_count = self._estimate_stage_count(interview_stages)
        
        # Base timelines (in days)
        timelines = {
            "job_posting": 3,
            "application_period": 14,
            "resume_screening": 3,
            "phone_screen": 5,
            "technical_interview": 7,
            "panel_interview": 7,
            "final_interview": 5,
            "reference_check": 3,
            "offer_negotiation": 5,
            "acceptance_period": 7
        }
        
        # Adjust based on urgency
        urgency_multipliers = {
            "urgent": 0.7,
            "normal": 1.0,
            "relaxed": 1.3
        }
        
        # Adjust based on team availability
        availability_multipliers = {
            "high": 0.8,
            "normal": 1.0,
            "low": 1.5
        }
        
        urgency_mult = urgency_multipliers.get(urgency.lower(), 1.0)
        availability_mult = availability_multipliers.get(team_availability.lower(), 1.0)
        
        # Calculate adjusted timelines
        total_days = 0
        timeline_breakdown = []
        start_date = datetime.now()
        
        for stage, days in timelines.items():
            if self._should_include_stage(stage, stage_count):
                adjusted_days = int(days * urgency_mult * availability_mult)
                end_date = start_date + timedelta(days=adjusted_days)
                
                timeline_breakdown.append({
                    "stage": stage.replace("_", " ").title(),
                    "duration": f"{adjusted_days} days",
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                })
                
                total_days += adjusted_days
                start_date = end_date
        
        # Format output
        result = f"""
# Hiring Timeline Estimation

## Summary
- **Total Duration**: {total_days} days (~{total_days // 7} weeks)
- **Expected Start Date**: {datetime.now().strftime("%Y-%m-%d")}
- **Expected Completion**: {(datetime.now() + timedelta(days=total_days)).strftime("%Y-%m-%d")}
- **Urgency Level**: {urgency.title()}
- **Team Availability**: {team_availability.title()}

## Timeline Breakdown
"""
        
        for item in timeline_breakdown:
            result += f"\n### {item['stage']}\n"
            result += f"- Duration: {item['duration']}\n"
            result += f"- Start: {item['start']}\n"
            result += f"- End: {item['end']}\n"
        
        result += "\n## Recommendations\n"
        if urgency == "urgent":
            result += "- Consider parallel processing of some stages\n"
            result += "- Pre-schedule interview slots in advance\n"
            result += "- Use automated screening tools\n"
        elif urgency == "relaxed":
            result += "- Take time to build a strong candidate pipeline\n"
            result += "- Consider multiple final candidates\n"
            result += "- Allow for thorough reference checks\n"
        
        return result.strip()
    
    def _estimate_stage_count(self, interview_stages: str) -> int:
        """Estimate the number of interview stages from description."""
        # Simple heuristic based on keywords
        keywords = ["phone", "technical", "panel", "final", "screen", "round", "interview"]
        count = sum(1 for keyword in keywords if keyword.lower() in interview_stages.lower())
        return max(count, 2)  # Minimum 2 stages
    
    def _should_include_stage(self, stage: str, stage_count: int) -> bool:
        """Determine if a stage should be included based on complexity."""
        always_include = ["job_posting", "application_period", "resume_screening", 
                         "offer_negotiation", "acceptance_period"]
        
        if stage in always_include:
            return True
        
        if stage_count >= 4:
            return True  # Include all stages for complex roles
        elif stage_count >= 3:
            return stage not in ["panel_interview"]  # Skip panel for medium complexity
        else:
            return stage in ["phone_screen", "technical_interview"]  # Only basic stages