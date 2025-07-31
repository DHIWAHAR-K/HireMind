import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.workflows import HiringWorkflow, HiringState
from langchain_core.messages import HumanMessage, AIMessage


class TestHiringWorkflow:
    """Test suite for hiring workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.workflow = HiringWorkflow()
    
    def test_workflow_initialization(self):
        """Test workflow initialization."""
        assert self.workflow.role_agent is not None
        assert self.workflow.jd_agent is not None
        assert self.workflow.interview_agent is not None
        assert self.workflow.tools is not None
        assert len(self.workflow.tools) >= 4
    
    @patch('src.workflows.hiring_workflow.RoleDefinitionAgent')
    @patch('src.workflows.hiring_workflow.JDGeneratorAgent')
    @patch('src.workflows.hiring_workflow.InterviewPlannerAgent')
    def test_workflow_build(self, mock_interview, mock_jd, mock_role):
        """Test workflow graph building."""
        # Mock the agents
        mock_role_instance = Mock()
        mock_jd_instance = Mock()
        mock_interview_instance = Mock()
        
        mock_role.return_value = mock_role_instance
        mock_jd.return_value = mock_jd_instance
        mock_interview.return_value = mock_interview_instance
        
        workflow = HiringWorkflow()
        
        # Verify agents were created
        mock_role.assert_called_once()
        mock_jd.assert_called_once()
        mock_interview.assert_called_once()
    
    def test_hiring_state_structure(self):
        """Test hiring state type definition."""
        # Test that HiringState has required fields
        state = {
            "messages": [HumanMessage(content="test")],
            "current_stage": "role_definition",
            "role_definition": None,
            "job_description": None,
            "interview_plan": None,
            "timeline": None,
            "salary_benchmark": None,
            "offer_letter": None,
            "error": None,
            "completed_stages": []
        }
        
        # Should not raise type errors
        assert state["messages"][0].content == "test"
        assert state["current_stage"] == "role_definition"
        assert state["completed_stages"] == []
    
    @patch('src.workflows.hiring_workflow.HiringWorkflow._role_definition_node')
    def test_role_definition_node(self, mock_node):
        """Test role definition node execution."""
        # Mock the node method
        mock_node.return_value = {
            "messages": [AIMessage(content="Role defined")],
            "current_stage": "jd_generation",
            "role_definition": {"output": "Senior Engineer role"},
            "completed_stages": ["role_definition"],
            "error": None
        }
        
        # Create initial state
        state = {
            "messages": [HumanMessage(content="Define senior engineer role")],
            "current_stage": "role_definition",
            "completed_stages": [],
            "role_definition": None,
            "error": None
        }
        
        # This would be called by the workflow
        result = mock_node(state)
        
        assert result["current_stage"] == "jd_generation"
        assert "role_definition" in result["completed_stages"]
        assert result["role_definition"]["output"] == "Senior Engineer role"
    
    def test_workflow_state_progression(self):
        """Test workflow state progression logic."""
        workflow = HiringWorkflow()
        
        # Test initial state
        initial_state = {
            "messages": [HumanMessage(content="test")],
            "current_stage": "role_definition",
            "completed_stages": [],
            "role_definition": None,
            "job_description": None,
            "interview_plan": None,
            "timeline": None,
            "salary_benchmark": None,
            "offer_letter": None,
            "error": None
        }
        
        # Mock successful role definition
        with patch.object(workflow.role_agent, 'run') as mock_run:
            mock_run.return_value = {
                "success": True,
                "output": "Role defined successfully"
            }
            
            result = workflow._role_definition_node(initial_state)
            
            assert result["current_stage"] == "jd_generation"
            assert "role_definition" in result["completed_stages"]
            assert result["role_definition"]["output"] == "Role defined successfully"
    
    def test_workflow_error_handling(self):
        """Test workflow error handling."""
        workflow = HiringWorkflow()
        
        initial_state = {
            "messages": [HumanMessage(content="test")],
            "current_stage": "role_definition",
            "completed_stages": [],
            "role_definition": None,
            "error": None
        }
        
        # Mock failed role definition
        with patch.object(workflow.role_agent, 'run') as mock_run:
            mock_run.return_value = {
                "success": False,
                "error": "Failed to define role"
            }
            
            result = workflow._role_definition_node(initial_state)
            
            assert result["error"] == "Failed to define role"
    
    def test_format_result(self):
        """Test result formatting."""
        workflow = HiringWorkflow()
        
        state = {
            "error": None,
            "completed_stages": ["role_definition", "jd_generation"],
            "role_definition": {"output": "Role defined"},
            "job_description": "JD created",
            "messages": [
                HumanMessage(content="input"),
                AIMessage(content="output")
            ]
        }
        
        result = workflow._format_result(state)
        
        assert result["success"] is True
        assert len(result["completed_stages"]) == 2
        assert result["role_definition"]["output"] == "Role defined"
        assert result["job_description"] == "JD created"
        assert len(result["messages"]) == 2


@pytest.mark.asyncio
class TestAsyncWorkflow:
    """Test async workflow functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.workflow = HiringWorkflow()
    
    @patch('src.workflows.hiring_workflow.HiringWorkflow.workflow')
    async def test_async_workflow_run(self, mock_workflow_graph):
        """Test async workflow execution."""
        # Mock the compiled workflow
        mock_workflow_graph.ainvoke = AsyncMock(return_value={
            "error": None,
            "completed_stages": ["role_definition"],
            "role_definition": {"output": "Role defined"},
            "messages": [AIMessage(content="Role defined")]
        })
        
        result = await self.workflow.arun("Define a software engineer role")
        
        assert result["success"] is True
        assert len(result["completed_stages"]) == 1
        mock_workflow_graph.ainvoke.assert_called_once()
    
    @patch('src.workflows.hiring_workflow.HiringWorkflow.workflow')
    def test_sync_workflow_run(self, mock_workflow_graph):
        """Test sync workflow execution."""
        # Mock the compiled workflow
        mock_workflow_graph.invoke = Mock(return_value={
            "error": None,
            "completed_stages": ["role_definition", "jd_generation"],
            "role_definition": {"output": "Role defined"},
            "job_description": "JD created",
            "messages": [AIMessage(content="Workflow completed")]
        })
        
        result = self.workflow.run("Define and create JD for engineer role")
        
        assert result["success"] is True
        assert len(result["completed_stages"]) == 2
        mock_workflow_graph.invoke.assert_called_once()
    
    @patch('src.workflows.hiring_workflow.TimelineEstimatorTool')
    def test_timeline_estimation_node(self, mock_tool_class):
        """Test timeline estimation node."""
        workflow = HiringWorkflow()
        
        # Mock the tool
        mock_tool = Mock()
        mock_tool._run.return_value = "Timeline: 45 days total"
        mock_tool_class.return_value = mock_tool
        
        state = {
            "role_definition": {"output": "Senior Engineer"},
            "interview_plan": {"output": "3 rounds of interviews"},
            "current_stage": "timeline_estimation",
            "completed_stages": [],
            "timeline": None,
            "messages": [],
            "error": None
        }
        
        result = workflow._timeline_estimation_node(state)
        
        assert result["current_stage"] == "salary_benchmarking"
        assert "timeline_estimation" in result["completed_stages"]
        assert result["timeline"]["output"] == "Timeline: 45 days total"
    
    @patch('src.workflows.hiring_workflow.SalaryBenchmarkTool')
    def test_salary_benchmarking_node(self, mock_tool_class):
        """Test salary benchmarking node."""
        workflow = HiringWorkflow()
        
        # Mock the tool
        mock_tool = Mock()
        mock_tool._run.return_value = "Salary range: $120k - $150k"
        mock_tool_class.return_value = mock_tool
        
        state = {
            "role_definition": {"output": "Senior Engineer"},
            "current_stage": "salary_benchmarking",
            "completed_stages": [],
            "salary_benchmark": None,
            "messages": [],
            "error": None
        }
        
        result = workflow._salary_benchmarking_node(state)
        
        assert result["current_stage"] == "offer_generation"
        assert "salary_benchmarking" in result["completed_stages"]
        assert result["salary_benchmark"]["output"] == "Salary range: $120k - $150k"
    
    @patch('src.workflows.hiring_workflow.OfferLetterGeneratorTool')
    def test_offer_generation_node(self, mock_tool_class):
        """Test offer letter generation node."""
        workflow = HiringWorkflow()
        
        # Mock the tool
        mock_tool = Mock()
        mock_tool._run.return_value = "Offer letter template generated"
        mock_tool_class.return_value = mock_tool
        
        state = {
            "role_definition": {"output": "Senior Engineer"},
            "salary_benchmark": {"output": "Salary: $135k"},
            "current_stage": "offer_generation",
            "completed_stages": [],
            "offer_letter": None,
            "messages": [],
            "error": None
        }
        
        result = workflow._offer_generation_node(state)
        
        assert result["current_stage"] == "completed"
        assert "offer_generation" in result["completed_stages"]
        assert result["offer_letter"] == "Offer letter template generated"