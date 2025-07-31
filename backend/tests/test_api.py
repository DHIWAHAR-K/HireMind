import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from api.main import app


class TestAPI:
    """Test suite for FastAPI endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "HireMind" in data["message"]
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
    
    @patch('api.main.workflow')
    def test_start_workflow_endpoint(self, mock_workflow):
        """Test workflow start endpoint."""
        # Mock workflow response
        mock_workflow.arun = AsyncMock(return_value={
            "success": True,
            "completed_stages": ["role_definition"],
            "role_definition": {"output": "Role defined"},
            "error": None
        })
        
        response = self.client.post(
            "/api/workflow/start",
            json={"description": "Senior Software Engineer role"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "role_definition" in data["completed_stages"]
    
    @patch('api.main.memory_store')
    def test_get_workflow_status_endpoint(self, mock_memory):
        """Test workflow status endpoint."""
        # Mock memory store response
        mock_memory.load_workflow_state.return_value = {
            "current_stage": "jd_generation",
            "completed_stages": ["role_definition"],
            "role_definition": {"output": "Role defined"}
        }
        
        response = self.client.get("/api/workflow/test-session-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_stage"] == "jd_generation"
        assert "role_definition" in data["completed_stages"]
    
    def test_get_workflow_status_not_found(self):
        """Test workflow status endpoint with non-existent session."""
        with patch('api.main.memory_store') as mock_memory:
            mock_memory.load_workflow_state.return_value = None
            
            response = self.client.get("/api/workflow/non-existent-session")
            
            assert response.status_code == 404
    
    @patch('api.main.agents')
    def test_run_agent_endpoint(self, mock_agents):
        """Test agent run endpoint."""
        # Mock agent response
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "success": True,
            "output": "Role definition completed"
        }
        mock_agents.__getitem__.return_value = mock_agent
        mock_agents.__contains__.return_value = True
        
        response = self.client.post(
            "/api/agent/run",
            json={
                "agent_type": "role_definition",
                "input_text": "Define a senior engineer role"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["agent"] == "role_definition"
        assert "Role definition completed" in data["output"]
    
    def test_run_agent_invalid_type(self):
        """Test agent run endpoint with invalid agent type."""
        response = self.client.post(
            "/api/agent/run",
            json={
                "agent_type": "invalid_agent",
                "input_text": "Test input"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid agent type" in data["detail"]
    
    @patch('api.main.memory_store')
    def test_list_profiles_endpoint(self, mock_memory):
        """Test profiles list endpoint."""
        # Mock memory store response
        mock_memory.list_recent_profiles.return_value = [
            {
                "session_id": "session1",
                "role_title": "Senior Engineer",
                "department": "Engineering",
                "status": "active"
            },
            {
                "session_id": "session2",
                "role_title": "Product Manager",
                "department": "Product",
                "status": "completed"
            }
        ]
        
        response = self.client.get("/api/profiles")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["profiles"]) == 2
        assert data["profiles"][0]["role_title"] == "Senior Engineer"
    
    @patch('api.main.memory_store')
    def test_get_profile_endpoint(self, mock_memory):
        """Test get profile endpoint."""
        # Mock memory store response
        mock_memory.load_hiring_profile.return_value = {
            "session_id": "test-session",
            "role_title": "Senior Engineer",
            "status": "active",
            "results": {
                "role_definition": {"output": "Role defined"},
                "job_description": "JD created"
            }
        }
        
        response = self.client.get("/api/profiles/test-session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session"
        assert data["role_title"] == "Senior Engineer"
    
    @patch('api.main.memory_store')
    def test_delete_profile_endpoint(self, mock_memory):
        """Test delete profile endpoint."""
        # Mock memory store response
        mock_memory.clear_session.return_value = True
        
        response = self.client.delete("/api/profiles/test-session")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]
    
    @patch('api.main.memory_store')
    def test_delete_profile_not_found(self, mock_memory):
        """Test delete profile endpoint with non-existent profile."""
        # Mock memory store response
        mock_memory.clear_session.return_value = False
        
        response = self.client.delete("/api/profiles/non-existent")
        
        assert response.status_code == 404


class TestAPIErrorHandling:
    """Test API error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
    
    def test_workflow_start_with_empty_description(self):
        """Test workflow start with empty description."""
        response = self.client.post(
            "/api/workflow/start",
            json={"description": ""}
        )
        
        # Should still accept empty description but workflow might fail
        assert response.status_code in [200, 422, 500]
    
    def test_agent_run_with_missing_fields(self):
        """Test agent run with missing required fields."""
        response = self.client.post(
            "/api/agent/run",
            json={"agent_type": "role_definition"}  # Missing input_text
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('api.main.workflow')
    def test_workflow_start_internal_error(self, mock_workflow):
        """Test workflow start with internal error."""
        # Mock workflow to raise exception
        mock_workflow.arun = AsyncMock(side_effect=Exception("Internal error"))
        
        response = self.client.post(
            "/api/workflow/start",
            json={"description": "Test role"}
        )
        
        assert response.status_code == 500
    
    def test_invalid_json_payload(self):
        """Test endpoints with invalid JSON."""
        response = self.client.post(
            "/api/workflow/start",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = self.client.options("/api/workflow/start")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers


class TestAPIValidation:
    """Test API request validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
    
    def test_workflow_request_validation(self):
        """Test workflow request validation."""
        # Valid request
        valid_response = self.client.post(
            "/api/workflow/start",
            json={
                "description": "Senior Software Engineer role",
                "session_id": "custom-session-id"
            }
        )
        
        # Should not raise validation error
        assert valid_response.status_code != 422
    
    def test_agent_request_validation(self):
        """Test agent request validation."""
        # Valid request
        valid_response = self.client.post(
            "/api/agent/run",
            json={
                "agent_type": "role_definition",
                "input_text": "Define a role",
                "session_id": "test-session"
            }
        )
        
        # Should not raise validation error for structure
        assert valid_response.status_code in [200, 400, 500]  # 400 for invalid agent type, 500 for other errors
    
    def test_profiles_query_parameters(self):
        """Test profiles endpoint query parameters."""
        # Test with limit parameter
        response = self.client.get("/api/profiles?limit=5")
        assert response.status_code == 200
        
        # Test with invalid limit
        response = self.client.get("/api/profiles?limit=invalid")
        assert response.status_code == 422