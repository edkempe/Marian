import boto3
import json
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import re
from datetime import datetime, timedelta

# Gmail API dependencies
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Additional AWS dependencies
import os
import base64

# Potential AI dependencies
import anthropic

class TFlowPriority(Enum):
    """TFlow priority levels with distribution targets."""
    CRITICAL = 1     # ~1% of emails
    IMPORTANT = 2    # ~4-5% of emails
    RELEVANT = 3     # ~15-20% of emails
    ROUTINE = 4      # ~30% of emails
    LOW = 5          # ~45-50% of emails

@dataclass
class EmailSignals:
    """Structured representation of email priority signals."""
    sender_importance: float = 0.0
    subject_urgency: float = 0.0
    content_value: float = 0.0
    recipient_patterns: float = 0.0
    time_sensitivity: float = 0.0

class MarianEmailProcessor:
    def __init__(self, 
                 dynamodb_table_name: str = 'email_metadata', 
                 secrets_manager_id: str = 'gmail/oauth/tokens',
                 anthropic_secret_name: str = 'AntrhopicKey'):
        """
        Initialize MARIAN email processor with DynamoDB, Gmail, and Anthropic configuration.
        
        Args:
            dynamodb_table_name (str): Name of DynamoDB table for email metadata
            secrets_manager_id (str): AWS Secrets Manager ID for Gmail OAuth tokens
            anthropic_secret_name (str): AWS Secrets Manager ID for Anthropic API key
        """
        # AWS Resources
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(dynamodb_table_name)
        self.cloudwatch = boto3.client('cloudwatch')
        self.secrets_manager = boto3.client('secretsmanager')
        
        # Gmail Client
        self.gmail_service = self._initialize_gmail_client(secrets_manager_id)
        
        # Anthropic Client
        self.anthropic_client = self._initialize_anthropic_client(anthropic_secret_name)

    def _initialize_gmail_client(self, secrets_manager_id: str):
        """
        Initialize Gmail API client using OAuth tokens from AWS Secrets Manager.
        
        Args:
            secrets_manager_id (str): Secrets Manager identifier for Gmail tokens
        
        Returns:
            googleapiclient.discovery.Resource: Initialized Gmail service
        """
        try:
            # Retrieve OAuth credentials from AWS Secrets Manager
            secret_response = self.secrets_manager.get_secret_value(
                SecretId=secrets_manager_id
            )
            token_info = json.loads(secret_response['SecretString'])
            
            # Create credentials object
            credentials = Credentials(
                token=token_info['access_token'],
                refresh_token=token_info['refresh_token'],
                token_uri="https://oauth2.googleapis.com/token",
                client_id=token_info['client_id'],
                client_secret=token_info['client_secret']
            )
            
            # Refresh the token if it's expired
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                
                # Update the secret with new access token
                self.secrets_manager.update_secret(
                    SecretId=secrets_manager_id,
                    SecretString=json.dumps({
                        **token_info,
                        'access_token': credentials.token
                    })
                )
            
            # Build and return Gmail service
            return build('gmail', 'v1', credentials=credentials)
        
        except Exception as e:
            print(f"Error initializing Gmail client: {e}")
            raise

    def _initialize_anthropic_client(self, secret_name: str):
        """
        Initialize Anthropic client using API key from AWS Secrets Manager.
        
        Args:
            secret_name (str): Secrets Manager identifier for Anthropic API key
        
        Returns:
            anthropic.Anthropic: Initialized Anthropic client
        """
        try:
            # Retrieve API key from AWS Secrets Manager
            secret_response = self.secrets_manager.get_secret_value(
                SecretId=secret_name
            )
            secret = secret_response['SecretString']
            
            # Handle both JSON and plain text secrets
            try:
                api_key = json.loads(secret).get('api_key', secret)
            except json.JSONDecodeError:
                api_key = secret
            
            # Initialize and return Anthropic client
            return anthropic.Anthropic(api_key=api_key)
        
        except Exception as e:
            print(f"Error initializing Anthropic client: {e}")
            return None

    def list_gmail_labels(self) -> List[Dict[str, str]]:
        """
        List all Gmail labels for the authenticated user.
        
        Returns:
            List[Dict[str, str]]: List of label dictionaries with id and name
        """
        try:
            results = self.gmail_service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            return [{'id': label['id'], 'name': label['name']} for label in labels]
        except Exception as e:
            print(f"Error listing Gmail labels: {e}")
            return []

    def get_label_id(self, label_name: str) -> Optional[str]:
        """
        Get the label ID for a given label name.
        
        Args:
            label_name (str): Name of the Gmail label
        
        Returns:
            Optional[str]: Label ID if found, None otherwise
        """
        labels = self.list_gmail_labels()
        matching_labels = [label['id'] for label in labels if label['name'] == label_name]
        return matching_labels[0] if matching_labels else None

    def fetch_emails_by_label(self, 
                               label_id: str, 
                               max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch emails with a specific label ID.
        
        Args:
            label_id (str): Gmail label ID
            max_results (int, optional): Maximum number of emails to retrieve. Defaults to 100.
        
        Returns:
            List[Dict[str, Any]]: List of email metadata
        """
        try:
            # Fetch email threads with the specified label
            results = self.gmail_service.users().threads().list(
                userId='me', 
                labelIds=[label_id], 
                maxResults=max_results
            ).execute()
            
            emails = []
            for thread in results.get('threads', []):
                # Fetch full thread details
                thread_detail = self.gmail_service.users().threads().get(
                    userId='me', 
                    id=thread['id']
                ).execute()
                
                # Process each message in the thread
                for message in thread_detail['messages']:
                    email_data = self._parse_email_message(message)
                    emails.append(email_data)
                    
                    # Store email metadata in DynamoDB
                    self.store_email_metadata(email_data)
            
            return emails
        
        except Exception as e:
            print(f"Error fetching emails by label: {e}")
            return []

    def _parse_email_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a Gmail API message into a structured dictionary.
        
        Args:
            message (Dict[str, Any]): Raw Gmail API message
        
        Returns:
            Dict[str, Any]: Parsed email metadata
        """
        headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
        
        # Extract body content
        body = ''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in message['payload']:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        
        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': headers.get('Subject', ''),
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'date': headers.get('Date', ''),
            'body': body,
            'labels': message.get('labelIds', [])
        }

    def store_email_metadata(self, email_data: Dict[str, Any]) -> None:
        """
        Store processed email metadata in DynamoDB.
        
        Args:
            email_data (Dict[str, Any]): Processed email metadata
        """
        signals = self.extract_email_signals(email_data)
        priority = self.calculate_tflow_priority(signals)
        
        item = {
            'email_id': email_data.get('id'),
            'timestamp': datetime.utcnow().isoformat(),
            'priority': priority.value,
            'signals': asdict(signals),
            **email_data
        }
        
        self.table.put_item(Item=item)
        self._log_priority_metrics(priority)

    def calculate_tflow_priority(self, signals: EmailSignals) -> TFlowPriority:
        """
        Calculate email priority using weighted signals.
        
        Args:
            signals (EmailSignals): Extracted email priority signals
        
        Returns:
            TFlowPriority: Calculated priority level
        """
        total_score = (
            signals.sender_importance * 0.3 +
            signals.subject_urgency * 0.3 +
            signals.content_value * 0.2 +
            signals.recipient_patterns * 0.1 +
            signals.time_sensitivity * 0.1
        )
        
        # Mapping score to priority levels
        if total_score >= 0.9:
            return TFlowPriority.CRITICAL
        elif total_score >= 0.7:
            return TFlowPriority.IMPORTANT
        elif total_score >= 0.5:
            return TFlowPriority.RELEVANT
        elif total_score >= 0.3:
            return TFlowPriority.ROUTINE
        else:
            return TFlowPriority.LOW

    def extract_email_signals(self, email_data: Dict[str, Any]) -> EmailSignals:
        """
        Extract priority signals from email data.
        
        Args:
            email_data (Dict): Raw email metadata
        
        Returns:
            EmailSignals: Processed priority signals
        """
        return EmailSignals(
            sender_importance=self._calculate_sender_importance(email_data),
            subject_urgency=self._calculate_subject_urgency(email_data),
            content_value=self._calculate_content_value(email_data),
            recipient_patterns=self._calculate_recipient_patterns(email_data),
            time_sensitivity=self._calculate_time_sensitivity(email_data)
        )

    def process_email_with_ai(self, email_data: Dict[str, Any]) -> Optional[str]:
        """
        Process email using Anthropic AI to extract insights.
        
        Args:
            email_data (Dict[str, Any]): Email metadata
        
        Returns:
            Optional[str]: AI-generated insights or None if processing fails
        """
        if not self.anthropic_client:
            print("Anthropic client not initialized")
            return None

        try:
            # Construct prompt for AI analysis
            prompt = f"""
            Analyze the following email and provide key insights:

            Subject: {email_data.get('subject', 'N/A')}
            From: {email_data.get('from', 'N/A')}
            Date: {email_data.get('date', 'N/A')}

            Body:
            {email_data.get('body', 'No body content')}

            Please extract:
            1. Main purpose of the email
            2. Any action items
            3. Potential urgency or importance
            4. Recommended next steps
            """

            # Generate AI insights
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            print(f"Error processing email with AI: {e}")
            return None

    def _log_priority_metrics(self, priority: TFlowPriority) -> None:
        """
        Log priority distribution metrics to CloudWatch.
        
        Args:
            priority (TFlowPriority): Calculated email priority
        """
        self.cloudwatch.put_metric_data(
            Namespace='MARIAN/EmailPriorities',
            MetricData=[{
                'MetricName': 'PriorityDistribution',
                'Dimensions': [{'Name': 'Priority', 'Value': priority.name}],
                'Value': 1,
                'Unit': 'Count'
            }]
        )

    # Signal calculation methods (placeholder implementations)
    def _calculate_sender_importance(self, email_data: Dict) -> float:
        """
        Calculate sender importance based on email metadata.
        
        Args:
            email_data (Dict): Email metadata
        
        Returns:
            float: Sender importance score (0.0 to 1.0)
        """
        # Placeholder implementation
        sender = email_data.get('from', '').lower()
        
        # Example sender importance heuristics
        important_domains = ['@company.com', '@management.org', '@critical.net']
        for domain in important_domains:
            if domain in sender:
                return 1.0
        
        return 0.5

    def _calculate_subject_urgency(self, email_data: Dict) -> float:
        """
        Calculate subject urgency based on keywords.
        
        Args:
            email_data (Dict): Email metadata
        
        Returns:
            float: Subject urgency score (0.0 to 1.0)
        """
        subject = email_data.get('subject', '').lower()
        
        # Urgency keywords with different weights
        urgency_keywords = {
            'urgent': 1.0,
            'immediate': 0.9,
            'critical': 0.8,
            'asap': 0.7,
            'important': 0.6,
            'time-sensitive': 0.5
        }
        
        for keyword, weight in urgency_keywords.items():
            if keyword in subject:
                return weight
        
        return 0.1

    def _calculate_content_value(self, email_data: Dict) -> float:
        """
        Estimate content value based on email body.
        
        Args:
            email_data (Dict): Email metadata
        
        Returns:
            float: Content value score (0.0 to 1.0)
        """
        body = email_data.get('body', '').lower()
        
        # Content value indicators
        value_indicators = {
            'project update': 0.7,
            'proposal': 0.6,
            'contract': 0.8,
            'invoice': 0.5,
            'meeting minutes': 0.4
        }p