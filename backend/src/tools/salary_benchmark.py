from typing import Optional, Type, Dict
from pydantic import BaseModel, Field
from .base_tool import BaseHRTool
import random
import json


class SalaryBenchmarkInput(BaseModel):
    """Input schema for Salary Benchmark tool."""
    role_title: str = Field(description="The job title to benchmark")
    location: str = Field(default="United States", description="Geographic location")
    experience_level: str = Field(default="mid", description="Experience level: entry, mid, senior, lead")
    company_size: str = Field(default="startup", description="Company size: startup, small, medium, large")


class SalaryBenchmarkTool(BaseHRTool):
    """Tool for getting salary benchmarks."""
    
    name: str = "salary_benchmark"
    description: str = "Get salary benchmark data for a specific role and location"
    args_schema: Type[BaseModel] = SalaryBenchmarkInput
    
    def _execute(
        self,
        role_title: str,
        location: str = "United States",
        experience_level: str = "mid",
        company_size: str = "startup"
    ) -> str:
        """Get salary benchmark data."""
        
        # In a real implementation, this would call an API
        # For now, we'll use mock data with realistic ranges
        
        base_salaries = self._get_base_salaries()
        
        # Get base salary for role (with fallback)
        role_key = self._normalize_role_title(role_title)
        base_salary = base_salaries.get(role_key, self._estimate_base_salary(role_title))
        
        # Apply multipliers
        location_mult = self._get_location_multiplier(location)
        experience_mult = self._get_experience_multiplier(experience_level)
        company_mult = self._get_company_size_multiplier(company_size)
        
        # Calculate salary ranges
        adjusted_base = base_salary * location_mult * experience_mult * company_mult
        
        min_salary = int(adjusted_base * 0.85)
        max_salary = int(adjusted_base * 1.15)
        median_salary = int(adjusted_base)
        
        # Format ranges
        min_formatted = f"${min_salary:,}"
        max_formatted = f"${max_salary:,}"
        median_formatted = f"${median_salary:,}"
        
        # Calculate additional compensation
        equity_range = self._calculate_equity(company_size, experience_level)
        bonus_range = self._calculate_bonus(median_salary, company_size)
        
        result = f"""
# Salary Benchmark Report

## Role: {role_title}
- **Location**: {location}
- **Experience Level**: {experience_level.title()}
- **Company Size**: {company_size.title()}

## Base Salary Range
- **Minimum**: {min_formatted}
- **Median**: {median_formatted}
- **Maximum**: {max_formatted}

## Additional Compensation
### Annual Bonus
- **Target**: {bonus_range['target']}
- **Range**: {bonus_range['min']} - {bonus_range['max']}

### Equity Compensation
- **Equity Range**: {equity_range}
- **Vesting**: 4 years with 1-year cliff (standard)

## Total Compensation Estimate
- **Minimum TC**: ${int(min_salary + min_salary * 0.1):,}
- **Median TC**: ${int(median_salary + median_salary * 0.2):,}
- **Maximum TC**: ${int(max_salary + max_salary * 0.3):,}

## Market Insights
- This role is currently in {'high' if random.random() > 0.5 else 'moderate'} demand
- Average time to fill: {random.randint(30, 60)} days
- Candidate pool: {'Limited' if random.random() > 0.6 else 'Moderate'}

## Competitive Positioning
To attract top talent, consider:
- Offering at or above the median range
- Highlighting equity upside for startup roles
- Emphasizing unique benefits and culture
- Consider signing bonuses for urgent hires

*Note: This is mock data for demonstration. In production, this would use real-time market data.*
"""
        
        return result.strip()
    
    def _get_base_salaries(self) -> Dict[str, int]:
        """Get base salaries for common roles."""
        return {
            "software_engineer": 120000,
            "senior_software_engineer": 150000,
            "staff_software_engineer": 180000,
            "engineering_manager": 170000,
            "product_manager": 130000,
            "senior_product_manager": 160000,
            "data_scientist": 125000,
            "senior_data_scientist": 155000,
            "designer": 95000,
            "senior_designer": 120000,
            "marketing_manager": 90000,
            "sales_manager": 100000,
            "hr_manager": 85000,
            "finance_manager": 110000,
        }
    
    def _normalize_role_title(self, role_title: str) -> str:
        """Normalize role title for lookup."""
        return role_title.lower().replace(" ", "_").replace("-", "_")
    
    def _estimate_base_salary(self, role_title: str) -> int:
        """Estimate salary for unknown roles."""
        if "senior" in role_title.lower():
            return 140000
        elif "lead" in role_title.lower() or "principal" in role_title.lower():
            return 170000
        elif "manager" in role_title.lower():
            return 120000
        elif "director" in role_title.lower():
            return 180000
        else:
            return 100000
    
    def _get_location_multiplier(self, location: str) -> float:
        """Get location-based salary multiplier."""
        location_lower = location.lower()
        
        high_cost = ["san francisco", "new york", "seattle", "boston"]
        medium_cost = ["austin", "denver", "chicago", "los angeles"]
        
        if any(city in location_lower for city in high_cost):
            return 1.3
        elif any(city in location_lower for city in medium_cost):
            return 1.1
        elif "remote" in location_lower:
            return 1.0
        else:
            return 0.9
    
    def _get_experience_multiplier(self, level: str) -> float:
        """Get experience-based multiplier."""
        multipliers = {
            "entry": 0.7,
            "junior": 0.8,
            "mid": 1.0,
            "senior": 1.3,
            "lead": 1.5,
            "principal": 1.7,
            "staff": 1.6
        }
        return multipliers.get(level.lower(), 1.0)
    
    def _get_company_size_multiplier(self, size: str) -> float:
        """Get company size multiplier."""
        multipliers = {
            "startup": 0.9,  # Lower base, higher equity
            "small": 0.95,
            "medium": 1.0,
            "large": 1.1,
            "enterprise": 1.15
        }
        return multipliers.get(size.lower(), 1.0)
    
    def _calculate_equity(self, company_size: str, experience_level: str) -> str:
        """Calculate equity compensation range."""
        if company_size.lower() == "startup":
            if experience_level.lower() in ["senior", "lead", "principal"]:
                return "0.25% - 1.0%"
            else:
                return "0.1% - 0.5%"
        elif company_size.lower() in ["small", "medium"]:
            return "Stock options worth $20k - $100k"
        else:
            return "RSUs worth $30k - $200k annually"
    
    def _calculate_bonus(self, base_salary: int, company_size: str) -> Dict[str, str]:
        """Calculate bonus range."""
        if company_size.lower() == "startup":
            target_pct = 10
        elif company_size.lower() in ["small", "medium"]:
            target_pct = 15
        else:
            target_pct = 20
        
        target = int(base_salary * (target_pct / 100))
        
        return {
            "target": f"{target_pct}% (${target:,})",
            "min": f"${int(target * 0.5):,}",
            "max": f"${int(target * 1.5):,}"
        }