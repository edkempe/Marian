# MARIAN Anthropic Key Manager
# Project HAL: Intelligent Personal Assistant
# AWS Secrets Manager Integration for Anthropic API Key

import json

import boto3
from botocore.exceptions import ClientError


class AnthropicKeyManager:
    """
    Utility class for retrieving and managing Anthropic API key from AWS Secrets Manager.
    """

    def __init__(
        self, secret_name: str = "AntrhopicKey", region_name: str = "us-east-1"
    ):
        """
        Initialize the Anthropic Key Manager.

        Args:
            secret_name (str): Name of the secret in AWS Secrets Manager
            region_name (str): AWS region where the secret is stored
        """
        self.secret_name = secret_name
        self.region_name = region_name
        self._client = boto3.session.Session().client(
            service_name="secretsmanager", region_name=self.region_name
        )

    def get_anthropic_key(self) -> str:
        """
        Retrieve the Anthropic API key from AWS Secrets Manager.

        Returns:
            str: Anthropic API key

        Raises:
            ClientError: If there's an issue retrieving the secret
            ValueError: If the secret is empty or improperly formatted
        """
        try:
            get_secret_value_response = self._client.get_secret_value(
                SecretId=self.secret_name
            )
        except ClientError as e:
            print(f"Error retrieving Anthropic key: {e}")
            raise

        # Handle both JSON-encoded and plain text secrets
        secret = get_secret_value_response["SecretString"]

        try:
            # Try parsing as JSON in case the key is stored in a structured format
            secret_dict = json.loads(secret)
            # Common key names for API keys
            for key in ["api_key", "anthropic_key", "key", "token"]:
                if key in secret_dict:
                    return secret_dict[key]
        except json.JSONDecodeError:
            # If not JSON, assume it's a plain text key
            if secret and len(secret) > 10:  # Basic validation
                return secret

        raise ValueError("Unable to extract Anthropic API key from secret")

    @staticmethod
    def update_anthropic_key(
        new_key: str, secret_name: str = "AntrhopicKey", region_name: str = "us-east-1"
    ):
        """
        Update the Anthropic API key in AWS Secrets Manager.

        Args:
            new_key (str): New API key to store
            secret_name (str): Name of the secret in AWS Secrets Manager
            region_name (str): AWS region where the secret is stored
        """
        client = boto3.session.Session().client(
            service_name="secretsmanager", region_name=region_name
        )

        try:
            client.update_secret(
                SecretId=secret_name, SecretString=json.dumps({"api_key": new_key})
            )
            print(f"Successfully updated secret: {secret_name}")
        except ClientError as e:
            print(f"Error updating Anthropic key: {e}")
            raise


# Example usage
def main():
    """
    Demonstrate Anthropic key retrieval and management.
    """
    try:
        # Retrieve the Anthropic API key
        key_manager = AnthropicKeyManager()
        api_key = key_manager.get_anthropic_key()
        print("Successfully retrieved Anthropic API key")

        # Optional: Key rotation example
        # Uncomment and replace with a new key to test rotation
        # AnthropicKeyManager.update_anthropic_key("new_api_key_here")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
