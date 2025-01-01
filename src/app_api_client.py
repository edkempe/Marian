"""API client for making requests to the Anthropic API."""

import json
import os

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from shared_lib.constants import DEFAULT_MODEL, API_CONFIG


class APIClient:
    """Client for making API requests."""

    def __init__(self):
        """Initialize the API client."""
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(API_CONFIG["max_retries"]),
        wait=wait_exponential(multiplier=API_CONFIG["timeout"]),
    )
    def echo_test(self):
        """Test the API connection with a simple echo request."""
        try:
            # Try to create a simple message to test the connection
            response = self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=10,
                messages=[{"role": "user", "content": "Echo test"}],
            )
            return {"success": True, "response": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
