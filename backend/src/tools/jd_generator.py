from typing import Optional, Type
from pydantic import BaseModel, Field
from .base_tool import BaseHRTool
import json


class JDGeneratorInput(BaseModel):
    """Input schema for JD Generator tool."""
    role_title: str = Field(description="The job title/role name")
    department: str = Field(description="The department or team")
    responsibilities: str = Field(description="Key responsibilities for the role")
    requirements: str = Field(description="Required skills and qualifications")
    nice_to_have: Optional[str] = Field(default="", description="Nice-to-have skills")
    experience_years: Optional[int] = Field(default=3, description="Years of experience required")
    location: Optional[str] = Field(default="Remote", description="Job location")
    salary_range: Optional[str] = Field(default="", description="Salary range if available")


class JDGeneratorTool(BaseHRTool):
    """Tool for generating job descriptions."""
    
    name: str = "jd_generator"
    description: str = "Generate a comprehensive job description based on role requirements"
    args_schema: Type[BaseModel] = JDGeneratorInput
    
    def _execute(
        self,
        role_title: str,
        department: str,
        responsibilities: str,
        requirements: str,
        nice_to_have: str = "",
        experience_years: int = 3,
        location: str = "Remote",
        salary_range: str = ""
    ) -> str:
        """Generate a job description."""
        
        # Load template if available
        template = self._get_template()
        
        jd = f"""
# {role_title} - {department}

## About the Role
We are seeking an experienced {role_title} to join our {department} team. This is an exciting opportunity to make a significant impact in a fast-growing startup environment.

## Location
{location}

## Key Responsibilities
{self._format_list(responsibilities)}

## Required Qualifications
{self._format_list(requirements)}
- {experience_years}+ years of relevant experience

{self._format_nice_to_have(nice_to_have)}

## What We Offer
- Competitive compensation {self._format_salary(salary_range)}
- Comprehensive health, dental, and vision insurance
- Generous PTO and flexible work arrangements
- Professional development opportunities
- Stock options
- Collaborative and inclusive work environment

## How to Apply
Please submit your resume and a brief cover letter explaining why you're excited about this role and how your experience aligns with our needs.

We are an equal opportunity employer committed to building a diverse and inclusive team.
"""
        
        return jd.strip()
    
    def _format_list(self, items: str) -> str:
        """Format a string of items into a bullet list."""
        if not items:
            return ""
        
        # Split by common delimiters
        item_list = [item.strip() for item in items.replace(";", ",").split(",") if item.strip()]
        return "\n".join([f"- {item}" for item in item_list])
    
    def _format_nice_to_have(self, nice_to_have: str) -> str:
        """Format nice-to-have requirements."""
        if not nice_to_have:
            return ""
        
        return f"\n## Nice to Have\n{self._format_list(nice_to_have)}"
    
    def _format_salary(self, salary_range: str) -> str:
        """Format salary information."""
        if salary_range:
            return f"({salary_range})"
        return ""
    
    def _get_template(self) -> dict:
        """Load JD template from data directory."""
        try:
            with open("data/job_templates.json", "r") as f:
                return json.load(f)
        except:
            return {}