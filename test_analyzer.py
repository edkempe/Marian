#!/usr/bin/env python3
import json
import logging
from email_analyzer import EmailAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_edge_cases():
    analyzer = EmailAnalyzer()
    
    # Test cases with various edge cases
    test_cases = [
        {
            "name": "Invalid Arrays",
            "response": {
                "summary": "Test email",
                "category": "NOT_AN_ARRAY",  # Should become []
                "priority": {"score": "3", "reason": "test"},
                "action": {
                    "needed": True,
                    "type": {"invalid": "object"},  # Should become []
                    "deadline": ""
                },
                "key_points": None,  # Should become []
                "people_mentioned": "John, Jane",  # Should become []
                "links_found": 12345,  # Should become []
                "sentiment": "neutral",
                "confidence_score": 0.9
            }
        },
        {
            "name": "Invalid Numbers",
            "response": {
                "summary": "Test email",
                "category": [],
                "priority": {
                    "score": "10.5",  # Should become 5
                    "reason": "test"
                },
                "action": {
                    "needed": True,
                    "type": [],
                    "deadline": ""
                },
                "key_points": [],
                "people_mentioned": [],
                "links_found": [],
                "sentiment": "neutral",
                "confidence_score": "2.0"  # Should become 1.0
            }
        },
        {
            "name": "Invalid Sentiment",
            "response": {
                "summary": "Test email",
                "category": [],
                "priority": {"score": 3, "reason": "test"},
                "action": {
                    "needed": True,
                    "type": [],
                    "deadline": ""
                },
                "key_points": [],
                "people_mentioned": [],
                "links_found": [],
                "sentiment": "HAPPY",  # Should become neutral
                "confidence_score": 0.9
            }
        },
        {
            "name": "Missing Fields",
            "response": {
                "summary": "Test email",
                # Missing category
                "priority": {"score": 3},  # Missing reason
                # Missing action
                # Missing key_points
                # Missing people_mentioned
                # Missing links_found
                # Missing sentiment
                # Missing confidence_score
            }
        },
        {
            "name": "Malformed JSON in Arrays",
            "response": {
                "summary": "Test email",
                "category": ["valid"],
                "priority": {"score": 3, "reason": "test"},
                "action": {
                    "needed": True,
                    "type": ["{invalid"],  # Malformed JSON
                    "deadline": ""
                },
                "key_points": ["valid"],
                "people_mentioned": ["valid"],
                "links_found": ["https://example.com"],
                "sentiment": "neutral",
                "confidence_score": 0.9
            }
        }
    ]
    
    # Process each test case
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['name']}")
        try:
            # Create a mock email data
            email_data = {
                "id": f"test_{test_case['name'].lower().replace(' ', '_')}",
                "subject": "Test Subject",
                "sender": "test@example.com",
                "content": "Test content"
            }
            
            # Mock the API response
            class MockResponse:
                def __init__(self, content):
                    self.content = [type('Content', (), {'text': json.dumps(content)})]
            
            # Store the original client
            original_client = analyzer.client
            
            try:
                # Create a mock client
                class MockClient:
                    def __init__(self, response):
                        self.messages = type('Messages', (), {
                            'create': lambda **kwargs: response
                        })
                
                # Set up the mock
                analyzer.client = MockClient(MockResponse(test_case['response']))
                
                # Process the email
                result = analyzer.analyze_email(email_data)
                
                if result:
                    logger.info("Analysis successful!")
                    logger.info(f"Normalized result:")
                    logger.info(f"Priority Score: {result['priority']['score']}")
                    logger.info(f"Category: {result['category']}")
                    logger.info(f"Action Type: {result['action']['type']}")
                    logger.info(f"Sentiment: {result['sentiment']}")
                    logger.info(f"Confidence: {result['confidence_score']}")
                else:
                    logger.error("Analysis failed!")
                
            finally:
                # Restore the original client
                analyzer.client = original_client
                
        except Exception as e:
            logger.error(f"Test case failed: {str(e)}")
    
    analyzer.close()

if __name__ == "__main__":
    test_edge_cases()
