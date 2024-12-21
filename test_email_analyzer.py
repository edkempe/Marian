"""Tests for email analyzer functionality."""
import pytest
from unittest.mock import Mock, patch, call
import json
from datetime import datetime, timedelta
import anthropic
from app_email_analyzer import EmailAnalyzer
from model_email_analysis import EmailAnalysisResponse, EmailAnalysis

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
def analyzer(mock_anthropic):
    """Email analyzer fixture"""
    with patch('email_analyzer.start_metrics_server'):
        analyzer = EmailAnalyzer()
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

def test_analyze_email_success(analyzer, valid_email_data, valid_api_response):
    """Test successful email analysis with detailed assertions."""
    with patch('email_analyzer.get_analysis_session'), \
         patch.object(analyzer.client.messages, 'create') as mock_create:
        # Mock API response
        mock_create.return_value = Mock(content=json.dumps(valid_api_response))
        
        # Call analyze_email
        result = analyzer.analyze_email(valid_email_data)

    # Basic assertions
    assert result is not None
    assert isinstance(result, EmailAnalysis)
    
    # Email metadata assertions
    assert result.email_id == valid_email_data['id']
    assert isinstance(result.analysis_date, datetime)
    assert (datetime.utcnow() - result.analysis_date).total_seconds() < 60  # Within last minute
    
    # Content assertions
    assert result.summary == valid_api_response['summary']
    assert result.category == valid_api_response['category']
    assert result.priority_score == valid_api_response['priority_score']
    assert result.priority_reason == valid_api_response['priority_reason']
    
    # Action assertions
    assert result.action_needed == valid_api_response['action_needed']
    assert result.action_type == valid_api_response['action_type']
    assert result.action_deadline == valid_api_response['action_deadline']
    
    # Lists assertions
    assert result.key_points == valid_api_response['key_points']
    assert result.people_mentioned == valid_api_response['people_mentioned']
    assert result.links_found == valid_api_response['links_found']
    assert result.links_display == valid_api_response['links_display']
    
    # Context assertions
    assert result.project == valid_api_response['project']
    assert result.topic == valid_api_response['topic']
    
    # Analysis assertions
    assert result.sentiment == valid_api_response['sentiment']
    assert result.confidence_score == valid_api_response['confidence_score']
    assert isinstance(result.raw_analysis, dict)
    assert result.raw_analysis == valid_api_response

def test_analyze_email_with_empty_fields(analyzer, valid_email_data, mock_anthropic):
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
    mock_anthropic.return_value.messages.create.return_value = Mock(content=[mock_content])

    with patch('email_analyzer.get_analysis_session'):
        result = analyzer.analyze_email(valid_email_data)

    assert result is not None
    assert result.key_points == []
    assert result.people_mentioned == []
    assert result.links_found == []
    assert result.action_needed == False
    assert result.project == ""
    assert result.topic == ""

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
        
        with patch('email_analyzer.get_analysis_session'):
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
                "category": "not_a_list",
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

        with patch('email_analyzer.get_analysis_session'):
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
        with patch('email_analyzer.get_email_session') as mock_session, \
             patch('email_analyzer.get_analysis_session'), \
             patch.object(analyzer.client.messages, 'create') as mock_create:
            
            # Setup mocks
            mock_session.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = test_emails
            mock_create.return_value = Mock(content=[Mock(text=json.dumps(mock_response))])
            
            # Process emails
            analyzer.process_emails(batch_size=case["batch_size"])
            
            # Verify API calls
            assert mock_create.call_count == case["expected_calls"], \
                f"Failed for batch_size={case['batch_size']}"
            
            # Verify API call arguments
            calls = mock_create.call_args_list
            for call_args in calls:
                args, kwargs = call_args
                assert kwargs.get('model') == 'claude-3-haiku-20240307'  # Updated model version
                assert kwargs.get('max_tokens') is not None
                assert 'messages' in str(kwargs)

def test_process_emails_error_handling(analyzer, valid_email_data, mock_anthropic, valid_api_response):
    """Test error handling during batch processing."""
    test_emails = [valid_email_data.copy() for _ in range(3)]
    
    with patch('email_analyzer.get_email_session') as mock_session, \
         patch('email_analyzer.get_analysis_session'):
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
