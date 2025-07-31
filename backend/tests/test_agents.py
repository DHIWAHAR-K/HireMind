import pytest
from unittest.mock import Mock, patch
from src.agents import RoleDefinitionAgent, JDGeneratorAgent, InterviewPlannerAgent
from src.tools import get_all_tools


class TestAgents:
    """Test suite for HR agents."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tools = get_all_tools()
        self.role_agent = RoleDefinitionAgent(self.tools)
        self.jd_agent = JDGeneratorAgent(self.tools)
        self.interview_agent = InterviewPlannerAgent(self.tools)
    
    def test_role_definition_agent_initialization(self):
        """Test role definition agent initialization."""
        assert self.role_agent.name == "Role Definition Agent"
        assert self.role_agent.temperature == 0.3
        assert len(self.role_agent.tools) == len(self.tools)
    
    def test_jd_generator_agent_initialization(self):
        """Test JD generator agent initialization."""
        assert self.jd_agent.name == "JD Generator Agent"
        assert self.jd_agent.temperature == 0.7
        assert len(self.jd_agent.tools) == len(self.tools)
    
    def test_interview_planner_agent_initialization(self):
        """Test interview planner agent initialization."""
        assert self.interview_agent.name == "Interview Planner Agent"
        assert self.interview_agent.temperature == 0.4
        assert len(self.interview_agent.tools) == len(self.tools)
    
    @patch('src.agents.base_agent.ChatOpenAI')
    def test_role_definition_agent_run(self, mock_llm):
        """Test role definition agent execution."""
        # Mock the LLM response
        mock_executor = Mock()
        mock_executor.invoke.return_value = {
            "output": "Senior Software Engineer role defined with Python, AWS, and 5+ years experience."
        }
        
        with patch.object(self.role_agent, 'agent_executor', mock_executor):
            result = self.role_agent.run("Define a Senior Software Engineer role")
            
            assert result["success"] is True
            assert "Senior Software Engineer" in result["output"]
            assert result["agent"] == "Role Definition Agent"
    
    @patch('src.agents.base_agent.ChatOpenAI')
    def test_jd_generator_agent_run(self, mock_llm):
        """Test JD generator agent execution."""
        mock_executor = Mock()
        mock_executor.invoke.return_value = {
            "output": "# Senior Software Engineer\n\nWe are looking for an experienced Senior Software Engineer..."
        }
        
        with patch.object(self.jd_agent, 'agent_executor', mock_executor):
            result = self.jd_agent.run("Create JD for Senior Software Engineer")
            
            assert result["success"] is True
            assert "Senior Software Engineer" in result["output"]
            assert result["agent"] == "JD Generator Agent"
    
    @patch('src.agents.base_agent.ChatOpenAI')
    def test_interview_planner_agent_run(self, mock_llm):
        """Test interview planner agent execution."""
        mock_executor = Mock()
        mock_executor.invoke.return_value = {
            "output": "Interview Plan:\n1. Phone Screen (30 min)\n2. Technical Interview (60 min)\n3. Final Round (90 min)"
        }
        
        with patch.object(self.interview_agent, 'agent_executor', mock_executor):
            result = self.interview_agent.run("Plan interviews for Senior Software Engineer")
            
            assert result["success"] is True
            assert "Interview Plan" in result["output"]
            assert result["agent"] == "Interview Planner Agent"
    
    def test_agent_error_handling(self):
        """Test agent error handling."""
        with patch.object(self.role_agent.agent_executor, 'invoke', side_effect=Exception("Test error")):
            result = self.role_agent.run("Test input")
            
            assert result["success"] is False
            assert "Test error" in result["error"]
            assert result["agent"] == "Role Definition Agent"
    
    def test_agent_memory_management(self):
        """Test agent memory functionality."""
        # Test memory initialization
        assert self.role_agent.memory is not None
        assert self.role_agent.memory.k == 10  # Default window size
        
        # Test memory clearing
        self.role_agent.clear_memory()
        assert len(self.role_agent.memory.chat_memory.messages) == 0
    
    def test_system_messages(self):
        """Test agent system messages."""
        role_msg = self.role_agent.get_system_message()
        jd_msg = self.jd_agent.get_system_message()
        interview_msg = self.interview_agent.get_system_message()
        
        assert "role" in role_msg.lower()
        assert "job description" in jd_msg.lower()
        assert "interview" in interview_msg.lower()
        
        # Check for key concepts
        assert "responsibilities" in role_msg.lower()
        assert "compelling" in jd_msg.lower()
        assert "evaluation" in interview_msg.lower()


@pytest.mark.asyncio
class TestAsyncAgents:
    """Test async functionality of agents."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tools = get_all_tools()
        self.role_agent = RoleDefinitionAgent(self.tools)
    
    @patch('src.agents.base_agent.ChatOpenAI')
    async def test_async_agent_run(self, mock_llm):
        """Test async agent execution."""
        mock_executor = Mock()
        mock_executor.ainvoke.return_value = {
            "output": "Async role definition completed"
        }
        
        with patch.object(self.role_agent, 'agent_executor', mock_executor):
            result = await self.role_agent.arun("Define role async")
            
            assert result["success"] is True
            assert "Async role definition" in result["output"]
    
    @patch('src.agents.base_agent.ChatOpenAI')
    async def test_async_agent_error_handling(self, mock_llm):
        """Test async agent error handling."""
        with patch.object(self.role_agent.agent_executor, 'ainvoke', side_effect=Exception("Async error")):
            result = await self.role_agent.arun("Test async error")
            
            assert result["success"] is False
            assert "Async error" in result["error"]