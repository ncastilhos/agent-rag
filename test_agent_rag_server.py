import pytest
import httpx
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from AgentRAGServer import app, conversation_sessions, ChatRequest, ChatResponse
import uuid

# Test client for FastAPI
client = TestClient(app)

class TestAgentRAGServer:
    """Test suite for AgentRAGServer FastAPI routes"""
    
    def setup_method(self):
        """Setup method to clear conversation sessions before each test"""
        conversation_sessions.clear()
    
    def test_root_endpoint(self):
        """Test the root endpoint GET /"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == '"HTTP Endpoint for AgentRAG DGT with Memory"'
    
    @patch('AgentRAGServer.graph')
    def test_agent_invoke_without_session_id(self, mock_graph):
        """Test POST /AgentInvoke without providing session_id"""
        # Mock the graph response
        mock_response = {
            "answer": "Test answer",
            "conversation_history": [
                Mock(__class__=Mock(__name__="HumanMessage"), content="Test question"),
                Mock(__class__=Mock(__name__="AIMessage"), content="Test answer")
            ]
        }
        mock_graph.invoke.return_value = mock_response
        
        # Test data
        test_data = {
            "question": "Test question"
        }
        
        response = client.post("/AgentInvoke", json=test_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "session_id" in data
        assert "conversation_history" in data
        assert data["answer"] == "Test answer"
        assert isinstance(data["session_id"], str)
        assert len(data["conversation_history"]) == 2
    
    @patch('AgentRAGServer.graph')
    def test_agent_invoke_with_session_id(self, mock_graph):
        """Test POST /AgentInvoke with existing session_id"""
        # Mock the graph response
        mock_response = {
            "answer": "Test answer",
            "conversation_history": [
                Mock(__class__=Mock(__name__="HumanMessage"), content="Previous question"),
                Mock(__class__=Mock(__name__="AIMessage"), content="Previous answer"),
                Mock(__class__=Mock(__name__="HumanMessage"), content="Test question"),
                Mock(__class__=Mock(__name__="AIMessage"), content="Test answer")
            ]
        }
        mock_graph.invoke.return_value = mock_response
        
        # Create a session first
        session_id = str(uuid.uuid4())
        conversation_sessions[session_id] = [
            Mock(__class__=Mock(__name__="HumanMessage"), content="Previous question"),
            Mock(__class__=Mock(__name__="AIMessage"), content="Previous answer")
        ]
        
        # Test data
        test_data = {
            "question": "Test question",
            "session_id": session_id
        }
        
        response = client.post("/AgentInvoke", json=test_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["answer"] == "Test answer"
        assert len(data["conversation_history"]) == 4
    
    def test_agent_invoke_invalid_request(self):
        """Test POST /AgentInvoke with invalid request data"""
        # Test with missing question
        test_data = {}
        response = client.post("/AgentInvoke", json=test_data)
        assert response.status_code == 422  # Validation error
        
        # Test with invalid data types (Pydantic will reject non-string types)
        test_data = {"question": 123}
        response = client.post("/AgentInvoke", json=test_data)
        assert response.status_code == 422  # Pydantic validation error
    
    def test_get_conversation_existing_session(self):
        """Test GET /conversation/{session_id} with existing session"""
        session_id = str(uuid.uuid4())
        mock_messages = [
            Mock(__class__=Mock(__name__="HumanMessage"), content="Question 1"),
            Mock(__class__=Mock(__name__="AIMessage"), content="Answer 1"),
            Mock(__class__=Mock(__name__="HumanMessage"), content="Question 2"),
            Mock(__class__=Mock(__name__="AIMessage"), content="Answer 2")
        ]
        conversation_sessions[session_id] = mock_messages
        
        response = client.get(f"/conversation/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "conversation_history" in data
        assert len(data["conversation_history"]) == 4
        
        # Check message structure
        for msg in data["conversation_history"]:
            assert "type" in msg
            assert "content" in msg
            assert msg["type"] in ["HumanMessage", "AIMessage"]
    
    def test_get_conversation_nonexistent_session(self):
        """Test GET /conversation/{session_id} with non-existent session"""
        session_id = str(uuid.uuid4())
        
        response = client.get(f"/conversation/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Session not found"
    
    def test_clear_conversation_existing_session(self):
        """Test DELETE /conversation/{session_id} with existing session"""
        session_id = str(uuid.uuid4())
        mock_messages = [
            Mock(__class__=Mock(__name__="HumanMessage"), content="Question 1"),
            Mock(__class__=Mock(__name__="AIMessage"), content="Answer 1")
        ]
        conversation_sessions[session_id] = mock_messages
        
        # Verify session exists
        assert session_id in conversation_sessions
        
        response = client.delete(f"/conversation/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Conversation {session_id} cleared" in data["message"]
        
        # Verify session was deleted
        assert session_id not in conversation_sessions
    
    def test_clear_conversation_nonexistent_session(self):
        """Test DELETE /conversation/{session_id} with non-existent session"""
        session_id = str(uuid.uuid4())
        
        response = client.delete(f"/conversation/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Session not found"
    
    def test_conversation_persistence(self):
        """Test that conversation history persists across multiple requests"""
        session_id = str(uuid.uuid4())
        
        # First request
        with patch('AgentRAGServer.graph') as mock_graph:
            mock_graph.invoke.return_value = {
                "answer": "First answer",
                "conversation_history": [
                    Mock(__class__=Mock(__name__="HumanMessage"), content="First question"),
                    Mock(__class__=Mock(__name__="AIMessage"), content="First answer")
                ]
            }
            
            response1 = client.post("/AgentInvoke", json={
                "question": "First question",
                "session_id": session_id
            })
            assert response1.status_code == 200
        
        # Second request with same session
        with patch('AgentRAGServer.graph') as mock_graph:
            mock_graph.invoke.return_value = {
                "answer": "Second answer",
                "conversation_history": [
                    Mock(__class__=Mock(__name__="HumanMessage"), content="First question"),
                    Mock(__class__=Mock(__name__="AIMessage"), content="First answer"),
                    Mock(__class__=Mock(__name__="HumanMessage"), content="Second question"),
                    Mock(__class__=Mock(__name__="AIMessage"), content="Second answer")
                ]
            }
            
            response2 = client.post("/AgentInvoke", json={
                "question": "Second question",
                "session_id": session_id
            })
            assert response2.status_code == 200
        
        # Verify conversation history was maintained
        response3 = client.get(f"/conversation/{session_id}")
        assert response3.status_code == 200
        data = response3.json()
        assert len(data["conversation_history"]) == 4
    
    def test_chat_request_model_validation(self):
        """Test ChatRequest Pydantic model validation"""
        # Valid request
        valid_request = ChatRequest(question="Test question")
        assert valid_request.question == "Test question"
        assert valid_request.session_id is None
        
        # Valid request with session_id
        valid_request_with_session = ChatRequest(
            question="Test question",
            session_id="test-session-id"
        )
        assert valid_request_with_session.question == "Test question"
        assert valid_request_with_session.session_id == "test-session-id"
    
    def test_chat_response_model_validation(self):
        """Test ChatResponse Pydantic model validation"""
        response = ChatResponse(
            answer="Test answer",
            session_id="test-session-id",
            conversation_history=[
                {"type": "HumanMessage", "content": "Test question"},
                {"type": "AIMessage", "content": "Test answer"}
            ]
        )
        assert response.answer == "Test answer"
        assert response.session_id == "test-session-id"
        assert len(response.conversation_history) == 2

# Integration tests that require actual server running
class TestAgentRAGServerIntegration:
    """Integration tests for AgentRAGServer (requires server to be running)"""
    
    def test_server_health_check(self):
        """Test that the server is responding"""
        response = client.get("/")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_async_endpoints(self):
        """Test async behavior of endpoints"""
        # This test ensures the async endpoints work correctly
        response = client.get("/")
        assert response.status_code == 200
        
        # Test that the app can handle concurrent requests
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/")
            results.append(response.status_code)
        
        # Create multiple threads to test concurrency
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5

# Additional edge case tests
class TestAgentRAGServerEdgeCases:
    """Edge case tests for AgentRAGServer"""
    
    def setup_method(self):
        """Setup method to clear conversation sessions before each test"""
        conversation_sessions.clear()
    
    def test_empty_question(self):
        """Test POST /AgentInvoke with empty question"""
        test_data = {"question": ""}
        response = client.post("/AgentInvoke", json=test_data)
        # Should still work but might return empty answer
        assert response.status_code == 200
    
    def test_very_long_question(self):
        """Test POST /AgentInvoke with very long question"""
        long_question = "What is the meaning of life? " * 1000  # Very long question
        test_data = {"question": long_question}
        
        with patch('AgentRAGServer.graph') as mock_graph:
            mock_graph.invoke.return_value = {
                "answer": "Test answer",
                "conversation_history": [
                    Mock(__class__=Mock(__name__="HumanMessage"), content=long_question),
                    Mock(__class__=Mock(__name__="AIMessage"), content="Test answer")
                ]
            }
            
            response = client.post("/AgentInvoke", json=test_data)
            assert response.status_code == 200
    
    def test_special_characters_in_question(self):
        """Test POST /AgentInvoke with special characters"""
        special_question = "What about émojis 🚀 and spëcial chars? @#$%^&*()"
        test_data = {"question": special_question}
        
        with patch('AgentRAGServer.graph') as mock_graph:
            mock_graph.invoke.return_value = {
                "answer": "Test answer",
                "conversation_history": [
                    Mock(__class__=Mock(__name__="HumanMessage"), content=special_question),
                    Mock(__class__=Mock(__name__="AIMessage"), content="Test answer")
                ]
            }
            
            response = client.post("/AgentInvoke", json=test_data)
            assert response.status_code == 200
    
    def test_invalid_session_id_format(self):
        """Test with invalid session ID format"""
        test_data = {
            "question": "Test question",
            "session_id": "invalid-session-id-format"
        }
        
        with patch('AgentRAGServer.graph') as mock_graph:
            mock_graph.invoke.return_value = {
                "answer": "Test answer",
                "conversation_history": [
                    Mock(__class__=Mock(__name__="HumanMessage"), content="Test question"),
                    Mock(__class__=Mock(__name__="AIMessage"), content="Test answer")
                ]
            }
            
            response = client.post("/AgentInvoke", json=test_data)
            assert response.status_code == 200
            # Should create a new session or use the provided one
    
    def test_conversation_history_overflow(self):
        """Test conversation history with many messages"""
        session_id = str(uuid.uuid4())
        
        # Create a conversation with many messages
        many_messages = []
        for i in range(100):  # 100 message pairs
            many_messages.extend([
                Mock(__class__=Mock(__name__="HumanMessage"), content=f"Question {i}"),
                Mock(__class__=Mock(__name__="AIMessage"), content=f"Answer {i}")
            ])
        
        conversation_sessions[session_id] = many_messages
        
        response = client.get(f"/conversation/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["conversation_history"]) == 200
    
    def test_malformed_json_request(self):
        """Test with malformed JSON"""
        # This should be handled by FastAPI and return 422
        response = client.post("/AgentInvoke", 
                             data="invalid json", 
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422
    
    def test_missing_content_type_header(self):
        """Test request without Content-Type header"""
        response = client.post("/AgentInvoke", 
                             data='{"question": "test"}')
        # FastAPI should still process it
        assert response.status_code in [200, 422]
    
    def test_unicode_in_session_id(self):
        """Test with unicode characters in session ID"""
        unicode_session_id = "sëssion-ïd-🚀"
        
        with patch('AgentRAGServer.graph') as mock_graph:
            mock_graph.invoke.return_value = {
                "answer": "Test answer",
                "conversation_history": [
                    Mock(__class__=Mock(__name__="HumanMessage"), content="Test question"),
                    Mock(__class__=Mock(__name__="AIMessage"), content="Test answer")
                ]
            }
            
            test_data = {
                "question": "Test question",
                "session_id": unicode_session_id
            }
            
            response = client.post("/AgentInvoke", json=test_data)
            assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
