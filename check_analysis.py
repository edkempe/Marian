#!/usr/bin/env python3
from database.config import get_analysis_session
from models.email_analysis import EmailAnalysis
from datetime import datetime, timedelta
import json

def check_recent_analyses():
    """Check analyses from the last hour."""
    with get_analysis_session() as session:
        # Get analyses from the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        analyses = session.query(EmailAnalysis).filter(
            EmailAnalysis.analysis_date >= one_hour_ago
        ).all()
        
        print(f"\nFound {len(analyses)} analyses from the last hour:")
        for analysis in analyses:
            print("\n-------------------")
            print(f"Email ID: {analysis.email_id}")
            print(f"Thread ID: {analysis.thread_id}")
            print(f"Analysis Date: {analysis.analysis_date}")
            print(f"Summary: {analysis.summary}")
            print(f"Priority: {analysis.priority_score} - {analysis.priority_reason}")
            print(f"Action Needed: {analysis.action_needed}")
            if analysis.raw_analysis:
                print("\nRaw Analysis stored successfully")
            else:
                print("\nWARNING: No raw analysis stored")

if __name__ == "__main__":
    check_recent_analyses()
