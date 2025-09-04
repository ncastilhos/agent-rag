# AgentRAGServer Tests

This directory contains comprehensive tests for the AgentRAGServer FastAPI application.

## Test Files

- `test_agent_rag_server.py` - Main test file with comprehensive test coverage
- `run_tests.py` - Simple test runner script
- `pytest.ini` - Pytest configuration file

## Test Coverage

The test suite covers all FastAPI routes and includes:

### Core Route Tests
- **GET /** - Root endpoint
- **POST /AgentInvoke** - Main chat endpoint with session management
- **GET /conversation/{session_id}** - Retrieve conversation history
- **DELETE /conversation/{session_id}** - Clear conversation history

### Test Categories

1. **Basic Functionality Tests** (`TestAgentRAGServer`)
   - Root endpoint response
   - AgentInvoke with and without session IDs
   - Conversation persistence across requests
   - Pydantic model validation

2. **Integration Tests** (`TestAgentRAGServerIntegration`)
   - Server health checks
   - Async endpoint behavior
   - Concurrent request handling

3. **Edge Case Tests** (`TestAgentRAGServerEdgeCases`)
   - Empty questions
   - Very long questions
   - Special characters and Unicode
   - Malformed JSON requests
   - Large conversation histories
   - Invalid session ID formats

## Running Tests

### Using pytest directly:
```bash
py -m pytest test_agent_rag_server.py -v
```

### Using the test runner:
```bash
python run_tests.py
```

### Running specific test classes:
```bash
py -m pytest test_agent_rag_server.py::TestAgentRAGServer -v
py -m pytest test_agent_rag_server.py::TestAgentRAGServerEdgeCases -v
```

## Test Dependencies

The tests require the following packages (already installed):
- `pytest` - Testing framework
- `httpx` - HTTP client for testing
- `pytest-asyncio` - Async test support

## Mocking Strategy

The tests use `unittest.mock` to mock external dependencies:
- The LangGraph `graph.invoke()` method is mocked to avoid actual LLM calls
- This allows tests to run quickly without requiring API keys or external services

## Test Data

Tests use:
- UUIDs for session IDs
- Mock message objects for conversation history
- Various edge cases for input validation

## Coverage

The test suite provides comprehensive coverage of:
- ✅ All HTTP endpoints
- ✅ Request/response validation
- ✅ Error handling
- ✅ Session management
- ✅ Edge cases and boundary conditions
- ✅ Concurrent request handling
- ✅ Unicode and special character handling

## Notes

- Tests clear the `conversation_sessions` dictionary before each test to ensure isolation
- Mock objects are used to simulate the LangGraph workflow without actual LLM calls
- The tests verify both successful operations and error conditions
- All tests are designed to run independently and in any order
