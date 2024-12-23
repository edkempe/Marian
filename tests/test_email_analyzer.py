"""Tests for the email analyzer module."""
import json
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from typing import Dict, Any

from models.email_analysis import EmailAnalysisResponse, EmailAnalysis
from models.email import Email
from app_email_analyzer import EmailAnalyzer

@pytest.fixture
def valid_api_response():
    """Valid API response data"""
    return {
        "summary": "test summary",
        "category": ["test"],
        "priority_score": 3,
        "priority_reason": "test",
        "action_needed": True,
        "action_type": ["test"],
        "action_deadline": "2024-01-01",
        "key_points": ["test"],
        "people_mentioned": ["test"],
        "links_found": ["http://test.com"],
        "links_display": ["http://test.com"],
        "project": "test",
        "topic": "test",
        "sentiment": "positive",
        "confidence_score": 0.9
    }

@pytest.fixture
def mock_anthropic(valid_api_response):
    """Mock Anthropic client"""
    with patch('anthropic.Anthropic') as mock:
        mock_instance = Mock()
        mock_content = Mock()
        mock_content.text = json.dumps(valid_api_response)
        mock_instance.messages.create.return_value = Mock(content=[mock_content])
        mock.return_value = mock_instance
        yield mock

@pytest.fixture
def mock_metrics():
    """Mock metrics server"""
    with patch('prometheus_client.start_http_server', return_value=None):
        yield

@pytest.fixture
def mock_db():
    """Mock database sessions"""
    with patch('app_email_analyzer.get_analysis_session') as mock_analysis_session, \
         patch('app_email_analyzer.get_email_session') as mock_email_session:
        # Create mock session with context manager methods
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=None)
        
        # Configure session mocks
        mock_analysis_session.return_value = mock_session
        mock_email_session.return_value = mock_session
        
        yield mock_session

@pytest.fixture
def analyzer(mock_anthropic, mock_metrics, mock_db):
    """Email analyzer fixture"""
    analyzer = EmailAnalyzer(metrics_port=0)  
    analyzer.client = mock_anthropic.return_value
    return analyzer

@pytest.fixture
def valid_email_data():
    """Valid email data fixture."""
    return {
        'id': 'test_id',
        'subject': 'Test Subject',
        'sender': 'test@example.com',
        'date': datetime.now().isoformat(),
        'content': 'Test content',
        'thread_id': 'thread1',
        'labels': ['INBOX']
    }

def test_email_analysis_response_validation(valid_api_response):
    """Test EmailAnalysisResponse validation."""
    response = EmailAnalysisResponse.model_validate(valid_api_response)
    assert response.summary == "test summary"
    assert response.priority_score == 3
    assert response.priority_reason == "test"
    assert response.action_needed is True
    assert response.sentiment == "positive"
    assert 0 <= response.confidence_score <= 1

def test_email_analysis_response_validation_errors():
    """Test EmailAnalysisResponse validation errors with various invalid inputs."""
    from pydantic import ValidationError
    
    test_cases = [
        {
            "name": "empty_summary",
            "data": {
                "summary": "",  # Invalid: empty summary
                "category": ["test"],
                "priority_score": 3,
                "priority_reason": "test",
                "action_needed": True,
                "action_type": ["test"],
                "action_deadline": "2024-01-01",
                "key_points": ["test"],
                "people_mentioned": ["test"],
                "links_found": ["http://test.com"],
                "links_display": ["http://test.com"],
                "project": "test",
                "topic": "test",
                "sentiment": "positive",
                "confidence_score": 0.9
            },
            "expected_error": "String should have at least 1 character"
        },
        {
            "name": "invalid_category_type",
            "data": {
                "summary": "test",
                "category": "not_a_list",  # Invalid: should be a list
                "priority_score": 3,
                "priority_reason": "test",
                "action_needed": True,
                "action_type": ["test"],
                "action_deadline": "2024-01-01",
                "key_points": ["test"],
                "people_mentioned": ["test"],
                "links_found": ["http://test.com"],
                "links_display": ["http://test.com"],
                "project": "test",
                "topic": "test",
                "sentiment": "positive",
                "confidence_score": 0.9
            },
            "expected_error": "Input should be a valid list"
        },
        {
            "name": "invalid_priority_score",
            "data": {
                "summary": "test",
                "category": ["test"],
                "priority_score": 6,  # Invalid: score > 5
                "priority_reason": "test",
                "action_needed": True,
                "action_type": ["test"],
                "action_deadline": "2024-01-01",
                "key_points": ["test"],
                "people_mentioned": ["test"],
                "links_found": ["http://test.com"],
                "links_display": ["http://test.com"],
                "project": "test",
                "topic": "test",
                "sentiment": "positive",
                "confidence_score": 0.9
            },
            "expected_error": "Input should be less than or equal to 5"
        },
        {
            "name": "invalid_sentiment",
            "data": {
                "summary": "test",
                "category": ["test"],
                "priority_score": 3,
                "priority_reason": "test",
                "action_needed": True,
                "action_type": ["test"],
                "action_deadline": "2024-01-01",
                "key_points": ["test"],
                "people_mentioned": ["test"],
                "links_found": ["http://test.com"],
                "links_display": ["http://test.com"],
                "project": "test",
                "topic": "test",
                "sentiment": "invalid",  # Invalid: not in allowed values
                "confidence_score": 0.9
            },
            "expected_error": "String should match pattern '^(positive|negative|neutral)$'"
        }
    ]
    
    for case in test_cases:
        with pytest.raises(ValidationError) as exc_info:
            EmailAnalysisResponse.model_validate(case["data"])
        error_message = str(exc_info.value)
        assert case["expected_error"] in error_message, \
            f"Failed for case {case['name']}\nExpected: {case['expected_error']}\nGot: {error_message}"

def test_analyze_email_success(analyzer, valid_email_data, valid_api_response, mock_db):
    """Test successful email analysis with detailed assertions."""
    mock_content = Mock()
    mock_content.text = json.dumps(valid_api_response)
    analyzer.client.messages.create.return_value = Mock(content=[mock_content])

    # Call analyze_email
    result = analyzer.analyze_email(valid_email_data)

    # Basic assertions
    assert result is not None
    assert isinstance(result, EmailAnalysis)

    # Verify API response was processed correctly
    assert result.summary == valid_api_response["summary"]
    assert result.category == valid_api_response["category"]
    assert result.priority_score == valid_api_response["priority_score"]
    assert result.action_needed == valid_api_response["action_needed"]
    assert result.action_type == valid_api_response["action_type"]
    assert result.sentiment == valid_api_response["sentiment"]
    assert result.confidence_score == valid_api_response["confidence_score"]

def test_analyze_email_with_empty_fields(analyzer, valid_email_data, mock_anthropic, mock_db):
    """Test email analysis with empty optional fields."""
    minimal_response = {
        "summary": "Minimal summary",
        "category": ["test"],
        "priority_score": 1,
        "priority_reason": "low priority",
        "action_needed": False,
        "action_type": [],
        "action_deadline": None,
        "key_points": [],
        "people_mentioned": [],
        "links_found": [],
        "links_display": [],
        "project": "",
        "topic": "",
        "sentiment": "neutral",
        "confidence_score": 0.5
    }

    mock_content = Mock()
    mock_content.text = json.dumps(minimal_response)
    analyzer.client.messages.create.return_value = Mock(content=[mock_content])

    result = analyzer.analyze_email(valid_email_data)

    assert result is not None
    assert isinstance(result, EmailAnalysis)
    assert result.summary == minimal_response["summary"]
    assert result.category == minimal_response["category"]
    assert result.priority_score == minimal_response["priority_score"]
    assert result.action_needed == minimal_response["action_needed"]
    assert result.action_type == minimal_response["action_type"]
    assert result.sentiment == minimal_response["sentiment"]
    assert result.confidence_score == minimal_response["confidence_score"]

def test_analyze_email_api_error(analyzer, mock_anthropic, valid_email_data):
    """Test various API error scenarios."""
    # Mock error classes
    class MockAPIError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(message)

    class MockAPIConnectionError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(message)

    class MockInternalServerError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(message)

    error_cases = [
        (Exception("API Error"), "Generic API error"),
        (MockAPIError("Rate limit exceeded"), "Rate limit error"),
        (MockAPIConnectionError("Connection failed"), "Connection error"),
        (MockInternalServerError("Server error"), "Server error")
    ]
    
    for error, description in error_cases:
        mock_anthropic.return_value.messages.create.side_effect = error
        
        with patch('app_email_analyzer.get_analysis_session'):
            result = analyzer.analyze_email(valid_email_data)
        
        assert result is None, f"Failed for {description}"
        mock_anthropic.return_value.messages.create.reset_mock()

def test_analyze_email_validation_error(analyzer, mock_anthropic, valid_email_data):
    """Test error handling during response validation."""
    invalid_responses = [
        {
            "name": "missing_required_fields",
            "response": {"summary": "Test"},
            "description": "Missing required fields"
        },
        {
            "name": "invalid_types",
            "response": {
                "summary": "",
                "category": "not_a_list",  # Invalid: should be a list
                "priority_score": 6,
                "priority_reason": "",
                "action_needed": "not_bool",
                "action_type": [],
                "key_points": None,
                "people_mentioned": {},
                "links_found": ["invalid_url"],
                "links_display": None,
                "project": "",
                "topic": "",
                "sentiment": "invalid",
                "confidence_score": 2.0
            },
            "description": "Invalid field types"
        },
        {
            "name": "malformed_json",
            "response": "not_json",
            "description": "Malformed JSON"
        }
    ]
    
    for case in invalid_responses:
        mock_content = Mock()
        mock_content.text = case["response"] if isinstance(case["response"], str) else json.dumps(case["response"])
        mock_anthropic.return_value.messages.create.return_value = Mock(content=[mock_content])

        with patch('app_email_analyzer.get_analysis_session'):
            result = analyzer.analyze_email(valid_email_data)

        assert result is None, f"Failed for {case['description']}"
        mock_anthropic.return_value.messages.create.reset_mock()

def test_process_emails_batch_handling(analyzer, valid_email_data):
    """Test email batch processing with different batch sizes and scenarios."""
    # Create test data
    test_emails = [
        {**valid_email_data, 'id': f'test_id_{i}', 'subject': f'Test {i}'}
        for i in range(5)
    ]

    # Mock API response
    mock_response = {
        'summary': 'Test summary',
        'category': ['test'],
        'priority_score': 3,
        'priority_reason': 'test',
        'action_needed': True,
        'action_type': ['review'],
        'action_deadline': '2024-12-20',
        'key_points': ['point1'],
        'people_mentioned': ['person1'],
        'links_found': ['http://test.com'],
        'links_display': ['test.com'],
        'project': 'test',
        'topic': 'test',
        'sentiment': 'neutral',
        'confidence_score': 0.9
    }

    test_cases = [
        {"batch_size": 1, "expected_calls": 5},
        {"batch_size": 2, "expected_calls": 5},  # Each email requires one API call
        {"batch_size": 5, "expected_calls": 5},
        {"batch_size": 10, "expected_calls": 5}
    ]

    for case in test_cases:
        # Setup mock session
        mock_session = Mock()
        mock_session.execute.return_value.fetchall.return_value = test_emails
        analyzer.client.messages.create.return_value = Mock(content=[Mock(text=json.dumps(mock_response))])

        # Process emails
        analyzer.process_emails(batch_size=case["batch_size"])

        # Verify number of API calls
        assert analyzer.client.messages.create.call_count == case["expected_calls"], \
            f"Failed for batch_size={case['batch_size']}"

        # Verify API call configuration
        calls = analyzer.client.messages.create.call_args_list
        for call_args in calls:
            args, kwargs = call_args
            
            # Check model version
            assert kwargs.get('model') == 'test_model', \
                f"Incorrect model version. Expected test_model, got {kwargs.get('model')}"
            
            # Check required fields are present and non-empty
            for field in ['content', 'messages']:
                assert kwargs.get(field) is not None, f"Missing required field: {field}"
                
            # Check messages structure
            messages = kwargs.get('messages', [])
            assert len(messages) > 0, "No messages provided to API"
            assert all('role' in msg and 'content' in msg for msg in messages), \
                "Messages missing required fields (role or content)"

        # Reset mock for next test case
        analyzer.client.messages.create.reset_mock()

def test_process_emails_error_handling(analyzer, valid_email_data, mock_anthropic, valid_api_response):
    """Test error handling during batch processing."""
    test_emails = [valid_email_data.copy() for _ in range(3)]
    
    with patch('app_email_analyzer.get_email_session') as mock_session, \
         patch('app_email_analyzer.get_analysis_session'):
        # Setup mock to raise an exception on second email
        def side_effect(*args, **kwargs):
            if mock_anthropic.return_value.messages.create.call_count == 2:
                raise Exception("API Error")
            mock_content = Mock()
            mock_content.text = json.dumps(valid_api_response)
            return Mock(content=[mock_content])
        
        mock_anthropic.return_value.messages.create.side_effect = side_effect
        mock_session.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = test_emails
        
        # Process emails
        analyzer.process_emails(batch_size=1)
        
        # Verify that processing continued after error
        assert mock_anthropic.return_value.messages.create.call_count == 3
