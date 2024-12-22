#!/usr/bin/env python3
from database.config import get_analysis_session
from models.email_analysis import EmailAnalysis
from datetime import datetime, timezone

def check_recent_analyses():
    """Check analyses from today."""
    with get_analysis_session() as session:
        today = datetime.now(timezone.utc).date()
        analyses = session.query(EmailAnalysis).filter(
            EmailAnalysis.analysis_date >= today
        ).all()
        
        if not analyses:
            print("No analyses found today")
            return
            
        print("\nToday's analyses:")
        for analysis in analyses:
            print("\n-------------------")
            print(f"Email ID: {analysis.email_id}")
            print(f"Time: {analysis.analysis_date}")
            print(f"Summary: {analysis.summary}")
            print(f"Priority: {analysis.priority_score} - {analysis.priority_reason}")
            print(f"Action Needed: {analysis.action_needed}")
            if analysis.raw_analysis:
                print("Raw Analysis: Stored successfully")
            else:
                print("WARNING: No raw analysis stored")

if __name__ == "__main__":
    check_recent_analyses()
