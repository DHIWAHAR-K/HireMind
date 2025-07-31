from typing import Optional, Type, Dict
from pydantic import BaseModel, Field
from .base_tool import BaseHRTool
from datetime import datetime, timedelta


class OfferLetterInput(BaseModel):
    """Input schema for Offer Letter Generator tool."""
    candidate_name: str = Field(default="[Candidate Name]", description="Name of the candidate")
    role_title: str = Field(description="Job title being offered")
    department: str = Field(description="Department or team")
    salary: str = Field(description="Annual salary")
    company_name: str = Field(default="[Company Name]", description="Name of the company")
    start_date: Optional[str] = Field(default="", description="Proposed start date")
    reporting_to: str = Field(default="[Manager Name]", description="Direct manager")
    equity: Optional[str] = Field(default="", description="Equity compensation details")
    bonus: Optional[str] = Field(default="", description="Bonus structure")
    benefits_summary: Optional[str] = Field(default="", description="Additional benefits")


class OfferLetterGeneratorTool(BaseHRTool):
    """Tool for generating offer letters."""
    
    name: str = "offer_letter_generator"
    description: str = "Generate a professional offer letter template"
    args_schema: Type[BaseModel] = OfferLetterInput
    
    def _execute(
        self,
        role_title: str,
        department: str,
        salary: str,
        candidate_name: str = "[Candidate Name]",
        company_name: str = "[Company Name]",
        start_date: str = "",
        reporting_to: str = "[Manager Name]",
        equity: str = "",
        bonus: str = "",
        benefits_summary: str = "",
        **kwargs
    ) -> str:
        """Generate an offer letter template."""
        
        # Handle optional role_info and salary_info from workflow
        if "role_info" in kwargs:
            # Extract role details from role_info if provided
            role_title = self._extract_role_title(kwargs.get("role_info", "")) or role_title
        
        if "salary_info" in kwargs:
            # Extract salary from salary_info if provided
            salary = self._extract_salary(kwargs.get("salary_info", "")) or salary
        
        # Set default start date if not provided
        if not start_date:
            start_date = (datetime.now() + timedelta(days=14)).strftime("%B %d, %Y")
        
        # Company details
        company_address = "[Company Address]"
        
        letter = f"""
{company_name}
{company_address}

{datetime.now().strftime("%B %d, %Y")}

{candidate_name}
[Candidate Address]

Dear {candidate_name},

We are delighted to extend an offer for you to join {company_name} as a {role_title} in our {department} team. We were impressed by your experience and believe you will be a valuable addition to our organization.

**Position Details:**
- **Job Title**: {role_title}
- **Department**: {department}
- **Reports To**: {reporting_to}
- **Start Date**: {start_date}
- **Location**: [Office Location / Remote]
- **Employment Type**: Full-time

**Compensation:**
- **Base Salary**: {salary} per year, paid bi-weekly
{self._format_bonus(bonus)}
{self._format_equity(equity)}

**Benefits:**
Your compensation package includes:
- Comprehensive health, dental, and vision insurance (100% coverage for employee)
- 401(k) retirement plan with company matching
- Unlimited PTO policy
- Professional development budget of $2,000 annually
- Latest equipment and tools needed for your role
- Flexible work arrangements
{self._format_additional_benefits(benefits_summary)}

**Conditions of Employment:**
This offer is contingent upon:
- Successful completion of reference checks
- Verification of your eligibility to work in the United States
- Signing our standard employment agreement and confidentiality agreement

**Next Steps:**
Please indicate your acceptance of this offer by signing and returning this letter by [Date - 1 week from today]. We would also appreciate a confirmation email to [HR Email].

If you have any questions about this offer or would like to discuss any aspects of it, please don't hesitate to contact me at [HR Phone] or [HR Email].

We are excited about the possibility of you joining our team and look forward to the contributions you will make to {company_name}.

Sincerely,

[HR Manager Name]
[Title]
{company_name}
[Email]
[Phone]

---

**Acceptance:**

I, {candidate_name}, accept the position of {role_title} with {company_name} under the terms outlined in this letter.

Signature: _________________________ Date: _____________

Print Name: _________________________
"""
        
        return letter.strip()
    
    def _format_bonus(self, bonus: str) -> str:
        """Format bonus information."""
        if bonus:
            return f"- **Annual Bonus**: {bonus}"
        return ""
    
    def _format_equity(self, equity: str) -> str:
        """Format equity information."""
        if equity:
            return f"- **Equity**: {equity}"
        return ""
    
    def _format_additional_benefits(self, benefits: str) -> str:
        """Format additional benefits."""
        if benefits:
            benefit_lines = [f"- {b.strip()}" for b in benefits.split(",") if b.strip()]
            return "\n".join(benefit_lines)
        return ""
    
    def _extract_role_title(self, role_info: str) -> str:
        """Extract role title from role definition output."""
        # Simple extraction - in practice would use better parsing
        lines = role_info.split("\n")
        for line in lines:
            if "title" in line.lower() or "role" in line.lower():
                # Extract the role title
                parts = line.split(":")
                if len(parts) > 1:
                    return parts[1].strip()
        return ""
    
    def _extract_salary(self, salary_info: str) -> str:
        """Extract salary from benchmark output."""
        # Look for median salary in the output
        lines = salary_info.split("\n")
        for line in lines:
            if "median" in line.lower() and "$" in line:
                # Extract the salary amount
                import re
                salary_match = re.search(r'\$[\d,]+', line)
                if salary_match:
                    return salary_match.group()
        return "$100,000"  # Default fallback