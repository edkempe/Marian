#!/usr/bin/env python3
"""Utility for viewing and validating email analyses with configurable options."""

from database.config import get_analysis_session, get_email_session
from models.email_analysis import EmailAnalysis
from models.email import Email
from datetime import datetime, timedelta
import pytz
import argparse
import json
from typing import Optional, List

def get_time_filter(timeframe: str) -> datetime:
    """Get datetime filter based on timeframe."""
    now = datetime.now(pytz.UTC)
    if timeframe == 'hour':
        return now - timedelta(hours=1)
    elif timeframe == 'week':
        return now - timedelta(days=7)
    else:  # 'today'
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

def format_action_info(analysis: EmailAnalysis) -> List[str]:
    """Format action information from analysis."""
    lines = []
    if analysis.action_needed:
        lines.append(f"Action Needed: Yes")
        action_types = analysis.action_type if isinstance(analysis.action_type, list) else \
                      json.loads(analysis.action_type) if analysis.action_type else []
        if action_types:
            lines.append(f"Action Type: {', '.join(action_types)}")
        if analysis.action_deadline:
            lines.append(f"Deadline: {analysis.action_deadline}")
    else:
        lines.append("Action Needed: No")
    return lines

def format_categories(analysis: EmailAnalysis) -> str:
    """Format categories from analysis."""
    categories = analysis.category if isinstance(analysis.category, list) else \
                json.loads(analysis.category) if analysis.category else []
    return ', '.join(categories) if categories else 'None'

def view_analyses(timeframe: str = 'today', detail_level: str = 'normal', validate: bool = False):
    """View analyses with configurable timeframe and detail level.
    
    Args:
        timeframe: 'hour', 'today', or 'week'
        detail_level: 'basic', 'normal', or 'detailed'
        validate: Whether to perform validation checks
    """
    with get_analysis_session() as analysis_session:
        with get_email_session() as email_session:
            # Get analyses based on timeframe
            time_filter = get_time_filter(timeframe)
            analyses = analysis_session.query(EmailAnalysis)\
                .filter(EmailAnalysis.analysis_date >= time_filter)\
                .order_by(EmailAnalysis.analysis_date.desc())\
                .all()
            
            if not analyses:
                print(f"No analyses found for the last {timeframe}")
                return
            
            print(f"\nFound {len(analyses)} analyses from the last {timeframe}:")
            for analysis in analyses:
                print("\n-------------------")
                
                # Basic information (always shown)
                print(f"Email ID: {analysis.email_id}")
                print(f"Time: {analysis.analysis_date}")
                print(f"Summary: {analysis.summary}")
                
                # Normal detail level
                if detail_level in ['normal', 'detailed']:
                    print(f"Priority: {analysis.priority_score} - {analysis.priority_reason}")
                    for line in format_action_info(analysis):
                        print(line)
                    print(f"Categories: {format_categories(analysis)}")
                    print(f"Project: {analysis.project or 'None'}")
                    print(f"Topic: {analysis.topic or 'None'}")
                    print(f"Sentiment: {analysis.sentiment}")
                    print(f"Confidence: {analysis.confidence_score:.2f}")
                
                # Detailed information
                if detail_level == 'detailed':
                    email = email_session.query(Email).filter(Email.id == analysis.email_id).first()
                    if email:
                        print(f"\nEmail Details:")
                        print(f"From: {email.sender}")
                        print(f"Subject: {email.subject}")
                        print(f"Thread ID: {analysis.thread_id}")
                    
                    key_points = analysis.key_points if isinstance(analysis.key_points, list) else \
                                json.loads(analysis.key_points) if analysis.key_points else []
                    if key_points:
                        print("\nKey Points:")
                        for point in key_points:
                            print(f"- {point}")
                    
                    people = analysis.people_mentioned if isinstance(analysis.people_mentioned, list) else \
                            json.loads(analysis.people_mentioned) if analysis.people_mentioned else []
                    if people:
                        print("\nPeople Mentioned:")
                        for person in people:
                            print(f"- {person}")
                
                # Validation checks
                if validate:
                    print("\nValidation:")
                    if analysis.raw_analysis:
                        print("✓ Raw analysis stored")
                    else:
                        print("⚠ WARNING: No raw analysis stored")
                    
                    required_fields = ['summary', 'priority_score', 'priority_reason', 'sentiment']
                    missing = [field for field in required_fields if not getattr(analysis, field)]
                    if missing:
                        print(f"⚠ WARNING: Missing required fields: {', '.join(missing)}")
                    else:
                        print("✓ All required fields present")

def main():
    parser = argparse.ArgumentParser(description="View and validate email analyses")
    parser.add_argument('--timeframe', choices=['hour', 'today', 'week'], 
                       default='today', help="Time range to view")
    parser.add_argument('--detail', choices=['basic', 'normal', 'detailed'],
                       default='normal', help="Level of detail to show")
    parser.add_argument('--validate', action='store_true',
                       help="Perform validation checks")
    
    args = parser.parse_args()
    view_analyses(args.timeframe, args.detail, args.validate)

if __name__ == "__main__":
    main()
