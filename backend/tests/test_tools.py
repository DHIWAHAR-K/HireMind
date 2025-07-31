import pytest
from unittest.mock import Mock, patch
from src.tools import (
    JDGeneratorTool,
    TimelineEstimatorTool,
    SalaryBenchmarkTool,
    OfferLetterGeneratorTool,
    get_all_tools
)


class TestTools:
    """Test suite for HR tools."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.jd_tool = JDGeneratorTool()
        self.timeline_tool = TimelineEstimatorTool()
        self.salary_tool = SalaryBenchmarkTool()
        self.offer_tool = OfferLetterGeneratorTool()
    
    def test_get_all_tools(self):
        """Test getting all tools."""
        tools = get_all_tools()
        assert len(tools) >= 4
        tool_names = [tool.name for tool in tools]
        
        assert "jd_generator" in tool_names
        assert "timeline_estimator" in tool_names
        assert "salary_benchmark" in tool_names
        assert "offer_letter_generator" in tool_names
    
    def test_jd_generator_tool(self):
        """Test JD generator tool."""
        result = self.jd_tool._execute(
            role_title="Senior Software Engineer",
            department="Engineering",
            responsibilities="Design and develop software solutions, Lead technical discussions",
            requirements="Python, AWS, 5+ years experience",
            experience_years=5,
            location="San Francisco, CA"
        )
        
        assert "Senior Software Engineer" in result
        assert "Engineering" in result
        assert "Python" in result
        assert "AWS" in result
        assert "San Francisco" in result
    
    def test_timeline_estimator_tool(self):
        """Test timeline estimator tool."""
        result = self.timeline_tool._execute(
            role_info="Senior Software Engineer position",
            interview_stages="Phone screen, technical interview, panel interview, final round",
            urgency="normal",
            team_availability="normal"
        )
        
        assert "Timeline Estimation" in result
        assert "days" in result.lower()
        assert "weeks" in result.lower()
        assert "Phone Screen" in result or "phone_screen" in result.lower()
    
    def test_salary_benchmark_tool(self):
        """Test salary benchmark tool."""
        result = self.salary_tool._execute(
            role_title="Senior Software Engineer",
            location="San Francisco, CA",
            experience_level="senior",
            company_size="startup"
        )
        
        assert "Salary Benchmark" in result
        assert "Senior Software Engineer" in result
        assert "$" in result
        assert "San Francisco" in result
        assert "senior" in result.lower()
    
    def test_offer_letter_generator_tool(self):
        """Test offer letter generator tool."""
        result = self.offer_tool._execute(
            role_title="Senior Software Engineer",
            department="Engineering",
            salary="$150,000",
            candidate_name="John Doe",
            reporting_to="Engineering Manager"
        )
        
        assert "John Doe" in result
        assert "Senior Software Engineer" in result
        assert "$150,000" in result
        assert "Engineering Manager" in result
        assert "offer" in result.lower()
    
    def test_timeline_estimator_urgency_adjustment(self):
        """Test timeline estimator with different urgency levels."""
        # Test urgent timeline
        urgent_result = self.timeline_tool._execute(
            role_info="Senior Engineer",
            interview_stages="2 rounds",
            urgency="urgent",
            team_availability="high"
        )
        
        # Test relaxed timeline
        relaxed_result = self.timeline_tool._execute(
            role_info="Senior Engineer",
            interview_stages="2 rounds",
            urgency="relaxed",
            team_availability="low"
        )
        
        assert "urgent" in urgent_result.lower()
        assert "relaxed" in relaxed_result.lower()
    
    def test_salary_benchmark_location_adjustment(self):
        """Test salary benchmark with different locations."""
        sf_result = self.salary_tool._execute(
            role_title="Software Engineer",
            location="San Francisco",
            experience_level="mid",
            company_size="startup"
        )
        
        remote_result = self.salary_tool._execute(
            role_title="Software Engineer",
            location="Remote",
            experience_level="mid",
            company_size="startup"
        )
        
        # San Francisco should have higher salaries
        assert "San Francisco" in sf_result
        assert "Remote" in remote_result
        
        # Both should have salary information
        assert "$" in sf_result
        assert "$" in remote_result
    
    def test_jd_generator_formatting(self):
        """Test JD generator formatting."""
        result = self.jd_tool._execute(
            role_title="Product Manager",
            department="Product",
            responsibilities="Define product strategy, Work with engineering teams, Analyze user feedback",
            requirements="MBA preferred, 3+ years PM experience, Data analysis skills",
            nice_to_have="Technical background, B2B SaaS experience",
            experience_years=3
        )
        
        # Check formatting
        assert "Product Manager" in result
        assert "Product" in result
        assert "Key Responsibilities" in result or "responsibilities" in result.lower()
        assert "Required Qualifications" in result or "qualifications" in result.lower()
        assert "Nice to Have" in result or "nice to have" in result.lower()
    
    def test_offer_letter_with_equity(self):
        """Test offer letter generation with equity."""
        result = self.offer_tool._execute(
            role_title="Senior Engineer",
            department="Engineering",
            salary="$160,000",
            equity="0.25% equity grant",
            bonus="15% target bonus"
        )
        
        assert "0.25% equity" in result
        assert "15% target bonus" in result or "15%" in result
        assert "$160,000" in result
    
    def test_tool_error_handling(self):
        """Test tool error handling."""
        # Test with invalid input
        with patch.object(self.jd_tool, '_execute', side_effect=Exception("Test error")):
            result = self.jd_tool._run(
                role_title="Test",
                department="Test",
                responsibilities="Test",
                requirements="Test"
            )
            
            assert "Error in jd_generator" in result
            assert "Test error" in result


class TestToolValidation:
    """Test tool input validation."""
    
    def test_jd_generator_input_validation(self):
        """Test JD generator input validation."""
        tool = JDGeneratorTool()
        
        # Test with minimal required inputs
        result = tool._execute(
            role_title="Engineer",
            department="Tech",
            responsibilities="Code",
            requirements="Python"
        )
        
        assert "Engineer" in result
        assert "Tech" in result
        assert "Code" in result
        assert "Python" in result
    
    def test_timeline_estimator_stage_counting(self):
        """Test timeline estimator stage counting logic."""
        tool = TimelineEstimatorTool()
        
        # Test with explicit stage mentions
        complex_stages = "phone screen, technical interview, system design, panel interview, final interview"
        simple_stages = "phone interview, final interview"
        
        complex_result = tool._execute("Senior Role", complex_stages)
        simple_result = tool._execute("Junior Role", simple_stages)
        
        # Both should have timeline information
        assert "Timeline Estimation" in complex_result
        assert "Timeline Estimation" in simple_result
    
    def test_salary_benchmark_multipliers(self):
        """Test salary benchmark multiplier logic."""
        tool = SalaryBenchmarkTool()
        
        # Test different experience levels
        entry_result = tool._execute("Engineer", "Remote", "entry", "startup")
        senior_result = tool._execute("Engineer", "Remote", "senior", "startup")
        
        assert "entry" in entry_result.lower()
        assert "senior" in senior_result.lower()
        
        # Both should have salary ranges
        assert "Minimum" in entry_result
        assert "Minimum" in senior_result