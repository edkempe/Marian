#!/usr/bin/env python3
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy import and_, desc, func, text
from sqlalchemy.orm import Session
from tabulate import tabulate

from models.email import Email
from models.email_analysis import EmailAnalysis
from shared_lib import constants
from shared_lib.database_session_util import (
    AnalysisSession,
    EmailSession,
    get_analysis_session,
    get_email_session,
)
from shared_lib.gmail_lib import GmailAPI


class EmailAnalytics:
    """Analytics for email and analysis data."""

    def __init__(
        self,
        email_session: Optional[EmailSession] = None,
        analysis_session: Optional[AnalysisSession] = None,
        testing: bool = False,
    ):
        """Initialize analytics.

        Args:
            email_session: Optional SQLAlchemy session for email database
            analysis_session: Optional SQLAlchemy session for analysis database
            testing: If True, use in-memory SQLite database for testing
        """
        self.email_session = email_session
        self.analysis_session = analysis_session
        self.testing = testing

    def _get_email_session(self) -> EmailSession:
        """Get email database session."""
        if self.email_session:
            return self.email_session
        return get_email_session(
            constants.DATABASE_CONFIG["email"], testing=self.testing
        )

    def _get_analysis_session(self) -> AnalysisSession:
        """Get analysis database session."""
        if self.analysis_session:
            return self.analysis_session
        return get_analysis_session(
            constants.DATABASE_CONFIG["analysis"], testing=self.testing
        )

    def get_total_emails(self) -> int:
        """Get total number of emails in the database"""
        with self._get_email_session() as session:
            return session.query(Email).count()

    def _get_analyses_from_ids(self, email_ids: List[str]) -> List[Dict]:
        """Helper method to get formatted analyses from a list of email IDs."""
        analyses = []
        for email_id in email_ids:
            analysis = self.get_detailed_analysis(email_id)
            if analysis:
                analyses.append(analysis)
        return analyses

    def get_top_senders(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top email senders by volume"""
        with self._get_email_session() as session:
            results = (
                session.query(Email.from_, func.count(Email.id).label("count"))
                .group_by(Email.from_)
                .order_by(desc("count"))
                .limit(limit)
                .all()
            )
            return [(sender, count) for sender, count in results]

    def get_email_by_date(self) -> List[Tuple[str, int]]:
        """Get email distribution by date"""
        with self._get_email_session() as session:
            results = (
                session.query(
                    func.date(Email.received_date).label("date"),
                    func.count(Email.id).label("count"),
                )
                .group_by("date")
                .order_by(desc("date"))
                .limit(10)
                .all()
            )
            return [(str(date), count) for date, count in results]

    def get_label_distribution(self) -> Dict[str, int]:
        """Get distribution of email labels."""
        with self._get_email_session() as session:
            labels = session.query(Email.labels).all()

        # Process labels
        label_counts = Counter()
        for label_list in labels:
            if label_list[0]:
                current_labels = (
                    label_list[0].split(",")
                    if isinstance(label_list[0], str)
                    else label_list[0]
                )
                label_counts.update(current_labels)

        return dict(label_counts)

    def get_anthropic_analysis(self) -> List[Dict]:
        """Get all Anthropic analysis results."""
        analyses = []

        with self._get_analysis_session() as analysis_session:
            results = (
                analysis_session.query(EmailAnalysis)
                .order_by(EmailAnalysis.analysis_date.desc())
                .all()
            )

            with self._get_email_session() as email_session:
                for analysis in results:
                    email = (
                        email_session.query(Email)
                        .filter_by(id=analysis.email_id)
                        .first()
                    )
                    if email:
                        analysis_dict = self._format_analysis(analysis)
                        analysis_dict.update(
                            {
                                "subject": email.subject,
                                "from": email.from_,
                                "date": (
                                    email.received_date.isoformat()
                                    if email.received_date
                                    else None
                                ),
                            }
                        )
                        analyses.append(analysis_dict)

        return analyses

    def get_priority_distribution(self) -> List[Tuple[int, int]]:
        """Get distribution of priority scores."""
        with self._get_analysis_session() as session:
            results = (
                session.query(
                    EmailAnalysis.priority_score,
                    func.count(EmailAnalysis.email_id).label("count"),
                )
                .group_by(EmailAnalysis.priority_score)
                .order_by(EmailAnalysis.priority_score)
                .all()
            )
            priorities = []
            for score, count in results:
                if score >= 3:
                    priorities.append(("High (3)", count))
                elif score >= 2:
                    priorities.append(("Medium (2)", count))
                else:
                    priorities.append(("Low (1)", count))
            return priorities

    def get_sentiment_distribution(self) -> List[Tuple[str, int]]:
        """Get distribution of sentiment analysis."""
        with self._get_analysis_session() as session:
            results = (
                session.query(
                    EmailAnalysis.sentiment,
                    func.count(EmailAnalysis.email_id).label("count"),
                )
                .group_by(EmailAnalysis.sentiment)
                .all()
            )
            return [(sentiment, count) for sentiment, count in results]

    def get_action_needed_distribution(self) -> List[Tuple[bool, int]]:
        """Get distribution of emails needing action."""
        with self._get_analysis_session() as session:
            results = (
                session.query(
                    EmailAnalysis.action_needed,
                    func.count(EmailAnalysis.email_id).label("count"),
                )
                .group_by(EmailAnalysis.action_needed)
                .all()
            )
            return [(bool(action), count) for action, count in results]

    def get_project_distribution(self) -> List[Tuple[str, int]]:
        """Get distribution of projects."""
        with self._get_analysis_session() as session:
            results = (
                session.query(
                    EmailAnalysis.project,
                    func.count(EmailAnalysis.email_id).label("count"),
                )
                .filter(EmailAnalysis.project != None, EmailAnalysis.project != "")
                .group_by(EmailAnalysis.project)
                .all()
            )
            return [(project, count) for project, count in results]

    def get_topic_distribution(self) -> List[Tuple[str, int]]:
        """Get distribution of topics."""
        with self._get_analysis_session() as session:
            results = (
                session.query(
                    EmailAnalysis.topic,
                    func.count(EmailAnalysis.email_id).label("count"),
                )
                .filter(EmailAnalysis.topic != None, EmailAnalysis.topic != "")
                .group_by(EmailAnalysis.topic)
                .all()
            )
            return [(topic, count) for topic, count in results]

    def get_category_distribution(self) -> Dict[str, int]:
        """Get distribution of categories."""
        with self._get_analysis_session() as session:
            results = session.query(EmailAnalysis.category).all()

        category_counts = Counter()
        for result in results:
            categories = result[0]
            if categories:
                if isinstance(categories, list):
                    category_counts.update(categories)
                else:
                    try:
                        category_counts.update(json.loads(categories))
                    except json.JSONDecodeError:
                        continue

        return dict(category_counts)

    def get_confidence_distribution(self) -> List[Tuple[str, int]]:
        """Get distribution of confidence scores."""
        with self._get_analysis_session() as session:
            results = (
                session.query(
                    EmailAnalysis.confidence_score,
                    func.count(EmailAnalysis.email_id).label("count"),
                )
                .group_by(EmailAnalysis.confidence_score)
                .all()
            )
            confidence_dist = []
            for score, count in results:
                if score >= 0.9:
                    confidence_dist.append(("0.9-1.0", count))
                elif score >= 0.8:
                    confidence_dist.append(("0.8-0.89", count))
                elif score >= 0.7:
                    confidence_dist.append(("0.7-0.79", count))
                elif score >= 0.6:
                    confidence_dist.append(("0.6-0.69", count))
                else:
                    confidence_dist.append(("<0.6", count))

            return confidence_dist

    def get_analysis_by_date(self) -> List[Tuple[datetime, int]]:
        """Get analysis distribution by date."""
        with self._get_analysis_session() as session:
            results = (
                session.query(
                    EmailAnalysis.analysis_date,
                    func.count(EmailAnalysis.email_id).label("count"),
                )
                .group_by(EmailAnalysis.analysis_date)
                .order_by(EmailAnalysis.analysis_date.desc())
                .all()
            )
            return [(date, count) for date, count in results]

    def get_detailed_analysis(self, email_id: str) -> Dict:
        """Get detailed analysis for a specific email."""
        with self._get_analysis_session() as analysis_session:
            analysis = (
                analysis_session.query(EmailAnalysis)
                .filter_by(email_id=email_id)
                .first()
            )
            if not analysis:
                return None

            with self._get_email_session() as email_session:
                email = email_session.query(Email).filter_by(id=email_id).first()
                if not email:
                    return None

                analysis_dict = self._format_analysis(analysis)
                analysis_dict.update(
                    {
                        "subject": email.subject,
                        "from": email.from_,
                        "date": (
                            email.received_date.isoformat()
                            if email.received_date
                            else None
                        ),
                    }
                )
                return analysis_dict

    def get_analysis_by_category(self, category: str) -> List[Dict]:
        """Get all analyses with a specific category."""
        with self._get_analysis_session() as session:
            results = session.query(EmailAnalysis).all()
            matching_ids = []
            for result in results:
                categories = (
                    result.category
                    if isinstance(result.category, list)
                    else json.loads(result.category) if result.category else []
                )
                if category in categories:
                    matching_ids.append(result.email_id)
            return self._get_analyses_from_ids(matching_ids)

    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get overall analysis statistics."""
        with self._get_analysis_session() as session:
            total_analyzed = (
                session.query(EmailAnalysis)
                .filter(EmailAnalysis.confidence_score.isnot(None))
                .count()
            )
            avg_confidence = (
                session.query(
                    func.round(func.avg(EmailAnalysis.confidence_score), 2)
                ).scalar()
                or 0
            )
            avg_priority = (
                session.query(
                    func.round(func.avg(EmailAnalysis.priority_score), 2)
                ).scalar()
                or 0
            )
            action_needed_count = (
                session.query(EmailAnalysis)
                .filter(EmailAnalysis.action_needed == True)
                .count()
            )
            high_priority_count = (
                session.query(EmailAnalysis)
                .filter(EmailAnalysis.priority_score >= 3)
                .count()
            )
            positive_count = (
                session.query(EmailAnalysis)
                .filter(EmailAnalysis.sentiment == "positive")
                .count()
            )
            negative_count = (
                session.query(EmailAnalysis)
                .filter(EmailAnalysis.sentiment == "negative")
                .count()
            )
            neutral_count = (
                session.query(EmailAnalysis)
                .filter(EmailAnalysis.sentiment == "neutral")
                .count()
            )
            total_projects = session.query(
                func.count(func.distinct(EmailAnalysis.project))
            ).scalar()
            total_topics = session.query(
                func.count(func.distinct(EmailAnalysis.topic))
            ).scalar()

            stats = {
                "total_analyzed": total_analyzed,
                "avg_confidence": float(avg_confidence),
                "avg_priority": float(avg_priority),
                "action_needed_count": action_needed_count,
                "high_priority_count": high_priority_count,
                "total_projects": total_projects,
                "total_topics": total_topics,
                "sentiment_counts": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                },
            }

            return stats

    def get_analysis_with_action_needed(self) -> List[Dict]:
        """Get analyses that require action."""
        with self._get_analysis_session() as session:
            results = (
                session.query(EmailAnalysis)
                .filter(EmailAnalysis.action_needed == True)
                .all()
            )
            return [self._format_analysis(analysis) for analysis in results]

    def get_high_priority_analysis(self) -> List[Dict]:
        """Get high priority analyses (priority_score >= 3)."""
        with self._get_analysis_session() as session:
            results = (
                session.query(EmailAnalysis)
                .filter(EmailAnalysis.priority_score >= 3)
                .all()
            )
            return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_sentiment(self, sentiment: str) -> List[Dict]:
        """Get analyses by sentiment (positive/negative/neutral)."""
        with self._get_analysis_session() as session:
            results = (
                session.query(EmailAnalysis)
                .filter(EmailAnalysis.sentiment == sentiment)
                .all()
            )
            return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_project(self, project: str) -> List[Dict]:
        """Get analyses by project."""
        with self._get_analysis_session() as session:
            results = (
                session.query(EmailAnalysis)
                .filter(EmailAnalysis.project == project)
                .all()
            )
            return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_topic(self, topic: str) -> List[Dict]:
        """Get analyses by topic."""
        with self._get_analysis_session() as session:
            results = (
                session.query(EmailAnalysis).filter(EmailAnalysis.topic == topic).all()
            )
            return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_category(self, category: str) -> List[Dict]:
        """Get all analyses with a specific category."""
        with self._get_analysis_session() as session:
            results = session.query(EmailAnalysis).all()
            matching_ids = []
            for result in results:
                categories = (
                    result.category
                    if isinstance(result.category, list)
                    else json.loads(result.category) if result.category else []
                )
                if category in categories:
                    matching_ids.append(result.email_id)
            return self._get_analyses_from_ids(matching_ids)

    def _format_analysis(self, analysis: EmailAnalysis) -> Dict:
        """Format an EmailAnalysis object into a dictionary.

        Args:
            analysis: EmailAnalysis object to format

        Returns:
            Dictionary containing formatted analysis data
        """
        return {
            "email_id": analysis.email_id,
            "threadId": analysis.threadId,
            "date": analysis.analysis_date.isoformat(),
            "summary": analysis.summary,
            "category": (
                analysis.category
                if isinstance(analysis.category, list)
                else json.loads(analysis.category) if analysis.category else []
            ),
            "priority": {
                "score": analysis.priority_score,
                "reason": analysis.priority_reason,
            },
            "action": {
                "needed": bool(analysis.action_needed),
                "type": (
                    analysis.action_type
                    if isinstance(analysis.action_type, list)
                    else (
                        json.loads(analysis.action_type) if analysis.action_type else []
                    )
                ),
                "deadline": (
                    analysis.action_deadline.isoformat()
                    if analysis.action_deadline
                    else None
                ),
            },
            "key_points": (
                analysis.key_points
                if isinstance(analysis.key_points, list)
                else json.loads(analysis.key_points) if analysis.key_points else []
            ),
            "people_mentioned": (
                analysis.people_mentioned
                if isinstance(analysis.people_mentioned, list)
                else (
                    json.loads(analysis.people_mentioned)
                    if analysis.people_mentioned
                    else []
                )
            ),
            "links": {
                "found": (
                    analysis.links_found
                    if isinstance(analysis.links_found, list)
                    else (
                        json.loads(analysis.links_found) if analysis.links_found else []
                    )
                ),
                "display": (
                    analysis.links_display
                    if isinstance(analysis.links_display, list)
                    else (
                        json.loads(analysis.links_display)
                        if analysis.links_display
                        else []
                    )
                ),
            },
            "project": analysis.project or "",
            "topic": analysis.topic or "",
            "sentiment": analysis.sentiment,
            "confidence_score": analysis.confidence_score,
            "full_api_response": analysis.full_api_response,
        }

    def generate_report(self) -> Dict:
        """Generate a summary report of email data.

        Returns:
            Dictionary containing report data
        """
        with self._get_email_session() as session:
            # Get total emails
            total_emails = self.get_total_emails()

            # Get date range
            date_range = session.query(
                func.min(Email.received_date).label("oldest"),
                func.max(Email.received_date).label("newest"),
            ).first()

            # Get top senders
            top_senders = (
                session.query(Email.from_, func.count(Email.id).label("count"))
                .group_by(Email.from_)
                .order_by(desc("count"))
                .limit(10)
                .all()
            )

            # Get top recipients
            top_recipients = (
                session.query(Email.to, func.count(Email.id).label("count"))
                .group_by(Email.to)
                .order_by(desc("count"))
                .limit(10)
                .all()
            )

            report = {
                "total_emails": total_emails,
                "date_range": {
                    "oldest": date_range.oldest if date_range else None,
                    "newest": date_range.newest if date_range else None,
                },
                "top_senders": [{"email": s[0], "count": s[1]} for s in top_senders],
                "top_recipients": [
                    {"email": r[0], "count": r[1]} for r in top_recipients
                ],
            }

            return report

    def print_analysis_report(self) -> None:
        """Print a comprehensive analysis report."""
        print("\n=== Email Analysis Report ===\n")

        # Get total analyzed emails
        total = self.get_total_emails()
        print(f"Total Analyzed Emails: {total}\n")

        # Priority Distribution
        print("\nPriority Distribution:")
        priorities = self.get_priority_distribution()
        for score, count in priorities:
            print(f"  {score}: {count} emails ({count/total*100:.1f}%)")

        # Action Types
        print("\nAction Type Distribution:")
        actions = self.get_action_needed_distribution()
        for action, count in actions:
            print(f"  {action}: {count} emails")

        # Categories
        print("\nTop Categories:")
        categories = self.get_category_distribution()
        for category, count in categories.items():
            print(f"  {category}: {count} emails")

        # Sentiment
        print("\nSentiment Distribution:")
        sentiments = self.get_sentiment_distribution()
        for sentiment, count in sentiments:
            print(f"  {sentiment}: {count} emails ({count/total*100:.1f}%)")

        # Topic Distribution
        print("\nTop Email Topics (AI Analysis):")
        topics = self.get_topic_distribution()
        if topics:
            print(
                tabulate(
                    [[topic, count] for topic, count in topics],
                    headers=["Topic", "Count"],
                    tablefmt="pipe",
                )
            )
        print()

        # Project Distribution
        print("Project Distribution (AI Analysis):")
        projects = self.get_project_distribution()
        if projects:
            print(
                tabulate(
                    [[project, count] for project, count in projects],
                    headers=["Project", "Count"],
                    tablefmt="pipe",
                )
            )
        print()

        # Confidence Distribution
        print("\nConfidence Distribution:")
        confidence_dist = self.get_confidence_distribution()
        print(
            tabulate(
                confidence_dist, headers=["Confidence Level", "Count"], tablefmt="psql"
            )
        )
        print()

        # Recent Analysis
        print("Recent Email Analysis:\n")
        analysis = self.get_anthropic_analysis()
        if analysis:
            for email in analysis:
                print(f"Email: {email['subject']}")
                print(f"From: {email['from']}")
                print(f"Summary: {email['summary']}")
                if email.get("topics"):
                    print(f"Topics: {', '.join(email['topics'])}")
                if email.get("project"):
                    print(f"Project: {email['project']}")
                print(f"Sentiment: {email['sentiment']}")
                if email.get("action_items"):
                    action_items = email["action_items"]
                    if action_items:
                        print(f"Action Items: {', '.join(action_items)}")
                print("-" * 80 + "\n")

    def show_basic_stats(self) -> None:
        """Show basic email statistics."""
        print("\nBasic Email Statistics:")
        print(f"Total Emails: {self.get_total_emails()}")
        print(f"Top Senders: {self.get_top_senders()}")
        print(f"Email Distribution by Date: {self.get_email_by_date()}")
        print(f"Label Distribution: {self.get_label_distribution()}")

    def show_top_senders(self) -> None:
        """Show top email senders."""
        print("\nTop Email Senders:")
        top_senders = self.get_top_senders()
        print(tabulate(top_senders, headers=["Sender", "Count"], tablefmt="psql"))

    def show_email_distribution(self) -> None:
        """Show email distribution by date."""
        print("\nEmail Distribution by Date:")
        date_dist = self.get_email_by_date()
        print(tabulate(date_dist, headers=["Date", "Count"], tablefmt="psql"))

    def show_label_distribution(self) -> None:
        """Show label distribution."""
        print("\nLabel Distribution:")
        label_dist = self.get_label_distribution()
        print(tabulate(label_dist.items(), headers=["Label", "Count"], tablefmt="psql"))

    def show_ai_analysis_summary(self) -> None:
        """Show AI analysis summary."""
        print("\nAI Analysis Summary:")
        analysis_data = self.get_anthropic_analysis()
        if analysis_data:
            for analysis in analysis_data[:5]:
                print(f"\nEmail: {analysis['subject']}")
                print(f"From: {analysis['from']}")
                print(f"Summary: {analysis['summary']}")
                print(f"Topics: {', '.join(analysis['topic'])}")
                print(f"Sentiment: {analysis['sentiment']}")
                if analysis["action"]["needed"]:
                    print(f"Action Needed: {analysis['action']['needed']}")
                    print(f"Action Type: {', '.join(analysis['action']['type'])}")
                    print(f"Action Deadline: {analysis['action']['deadline']}")
                print("-" * 80)

    def show_confidence_distribution(self) -> None:
        """Show confidence distribution."""
        print("\nConfidence Distribution:")
        confidence_dist = self.get_confidence_distribution()
        print(
            tabulate(
                confidence_dist, headers=["Confidence Level", "Count"], tablefmt="psql"
            )
        )


def sync_gmail_labels() -> None:
    """Sync Gmail labels with local database."""
    from shared_lib.gmail_lib import GmailAPI

    # Initialize Gmail API and sync labels
    gmail = GmailAPI()
    gmail.sync_labels()


def print_menu() -> None:
    print("\n=== Email Analytics Menu ===")
    print("1. Show Basic Stats")
    print("2. Show Top Senders")
    print("3. Show Email Distribution by Date")
    print("4. Show Label Distribution")
    print("5. Show AI Analysis Summary")
    print("6. Show Full Report")
    print("7. Show Confidence Distribution")
    print("8. Exit")


def run_report(analytics: EmailAnalytics, report_type: str) -> None:
    """Run a specific report."""
    if report_type == "basic":
        print(f"\nTotal Emails: {analytics.get_total_emails()}")

    elif report_type == "senders":
        print("\nTop Email Senders:")
        top_senders = analytics.get_top_senders()
        print(tabulate(top_senders, headers=["Sender", "Count"], tablefmt="psql"))

    elif report_type == "dates":
        print("\nEmail Distribution by Date:")
        date_dist = analytics.get_email_by_date()
        print(tabulate(date_dist, headers=["Date", "Count"], tablefmt="psql"))

    elif report_type == "labels":
        print("\nTop Email Labels:")
        label_dist = analytics.get_label_distribution()
        print(tabulate(label_dist.items(), headers=["Label", "Count"], tablefmt="psql"))

    elif report_type == "analysis":
        print("\nAI Analysis Summary:")
        analysis_data = analytics.get_anthropic_analysis()
        if analysis_data:
            for analysis in analysis_data[:5]:
                print(f"\nEmail: {analysis['subject']}")
                print(f"From: {analysis['from']}")
                print(f"Summary: {analysis['summary']}")
                print(f"Topics: {', '.join(analysis['topic'])}")
                print(f"Sentiment: {analysis['sentiment']}")
                if analysis["action"]["needed"]:
                    print(f"Action Needed: {analysis['action']['needed']}")
                    print(f"Action Type: {', '.join(analysis['action']['type'])}")
                    print(f"Action Deadline: {analysis['action']['deadline']}")
                print("-" * 80)

    elif report_type == "full":
        analytics.print_analysis_report()

    elif report_type == "confidence":
        print("\nConfidence Distribution:")
        confidence_dist = analytics.get_confidence_distribution()
        print(
            tabulate(
                confidence_dist, headers=["Confidence Level", "Count"], tablefmt="psql"
            )
        )

    elif report_type == "all":
        # Run all reports in sequence
        for report in ["basic", "senders", "dates", "labels", "analysis", "confidence"]:
            run_report(analytics, report)
            print("\n" + "=" * 80 + "\n")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Email Analytics Reports")
    parser.add_argument(
        "--report",
        choices=[
            "basic",
            "senders",
            "dates",
            "labels",
            "analysis",
            "full",
            "confidence",
            "all",
        ],
        help="Type of report to run. If not specified, starts interactive menu.",
    )
    parser.add_argument(
        "--testing",
        action="store_true",
        help="Use in-memory SQLite database for testing",
    )
    args = parser.parse_args()

    # Sync labels first
    sync_gmail_labels()

    analytics = EmailAnalytics(testing=args.testing)

    try:
        if args.report:
            # Run specific report
            run_report(analytics, args.report)
        else:
            # Interactive menu
            while True:
                print_menu()
                choice = input("\nEnter your choice (1-8): ")

                if choice == "1":
                    run_report(analytics, "basic")
                elif choice == "2":
                    run_report(analytics, "senders")
                elif choice == "3":
                    run_report(analytics, "dates")
                elif choice == "4":
                    run_report(analytics, "labels")
                elif choice == "5":
                    run_report(analytics, "analysis")
                elif choice == "6":
                    run_report(analytics, "full")
                elif choice == "7":
                    run_report(analytics, "confidence")
                elif choice == "8":
                    print("\nGoodbye!")
                    break
                else:
                    print("\nInvalid choice. Please try again.")

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        pass


if __name__ == "__main__":
    main()
