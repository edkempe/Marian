#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timezone
from typing import Dict, List
from database.config import get_email_session, get_analysis_session, EmailSession, AnalysisSession
from models.email_analysis import EmailAnalysis
from models.email import Email
import argparse
import sqlite3
from sqlalchemy import func, desc

class EmailAnalytics:
    """Analytics for email and analysis data."""
    
    def __init__(self, email_conn=None, analysis_conn=None):
        """Initialize analytics.
        
        Args:
            email_conn: Optional SQLite connection for email database
            analysis_conn: Optional SQLite connection for analysis database
        """
        self.email_conn = email_conn
        self.analysis_conn = analysis_conn

    def _get_email_session(self):
        """Get email database session."""
        if self.email_conn:
            return self.email_conn
        return get_email_session()

    def _get_analysis_session(self):
        """Get analysis database session."""
        if self.analysis_conn:
            return self.analysis_conn
        return get_analysis_session()

    def get_total_emails(self):
        """Get total number of emails in the database"""
        with self._get_email_session() as session:
            return session.query(Email).count()

    def _execute_sqlite_query(self, session, query: str, params: tuple = ()) -> List[str]:
        """Helper method to execute SQLite query and return email IDs."""
        cursor = session.cursor()
        cursor.execute(query, params)
        return [result[0] for result in cursor.fetchall()]

    def _get_analyses_from_ids(self, email_ids: List[str]) -> List[Dict]:
        """Helper method to get formatted analyses from a list of email IDs."""
        analyses = []
        for email_id in email_ids:
            analysis = self.get_detailed_analysis(email_id)
            if analysis:
                analyses.append(analysis)
        return analyses

    def get_top_senders(self, limit=10):
        """Get top email senders by volume"""
        with self._get_email_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("""
                    SELECT from_address, COUNT(*) as count 
                    FROM emails 
                    GROUP BY from_address 
                    ORDER BY count DESC 
                    LIMIT ?
                """, (limit,))
                return cursor.fetchall()
            else:
                results = session.query(Email.sender, Email.id).group_by(Email.sender).order_by(Email.id.desc()).limit(limit).all()
                return [(sender, count) for sender, count in results]

    def get_email_by_date(self):
        """Get email distribution by date"""
        with self._get_email_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("""
                    SELECT DATE(received_date) as date, COUNT(*) as count 
                    FROM emails 
                    GROUP BY DATE(received_date)
                    ORDER BY date DESC 
                    LIMIT 10
                """)
                return cursor.fetchall()
            else:
                results = session.query(func.date(Email.date).label('date'), 
                                     func.count(Email.id).label('count'))\
                                .group_by('date')\
                                .order_by(desc('date'))\
                                .limit(10).all()
                return [(str(date), count) for date, count in results]

    def get_label_distribution(self) -> Dict[str, int]:
        """Get distribution of email labels."""
        with self._get_email_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("SELECT labels FROM emails")
                labels = cursor.fetchall()
            else:
                labels = session.query(Email.labels).all()

        # Process labels
        label_counts = Counter()
        for label_list in labels:
            if label_list[0]:
                current_labels = label_list[0].split(',') if isinstance(label_list[0], str) else label_list[0]
                label_counts.update(current_labels)
        
        return dict(label_counts)

    def get_anthropic_analysis(self):
        """Get all Anthropic analysis results."""
        analyses = []
        
        with self._get_analysis_session() as analysis_session:
            if isinstance(analysis_session, sqlite3.Connection):
                cursor = analysis_session.cursor()
                cursor.execute("""
                    SELECT * FROM email_analysis 
                    ORDER BY analysis_date DESC
                """)
                columns = [description[0] for description in cursor.description]
                results = []
                for row in cursor.fetchall():
                    result = dict(zip(columns, row))
                    results.append(result)
            else:
                results = analysis_session.query(EmailAnalysis).order_by(EmailAnalysis.analysis_date.desc()).all()

            with self._get_email_session() as email_session:
                for result in results:
                    if isinstance(analysis_session, sqlite3.Connection):
                        email_id = result['email_id']
                        cursor = email_session.cursor()
                        cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
                        email_row = cursor.fetchone()
                        if email_row:
                            email_columns = [description[0] for description in cursor.description]
                            email = dict(zip(email_columns, email_row))
                            analysis = {
                                'email_id': result['email_id'],
                                'thread_id': result['thread_id'],
                                'analysis_date': result['analysis_date'],
                                'subject': email['subject'],
                                'sender': email['from_address'],
                                'summary': result['summary'],
                                'category': json.loads(result['category']) if result['category'] else [],
                                'priority': {
                                    'score': result['priority_score'],
                                    'reason': result['priority_reason']
                                },
                                'action': {
                                    'needed': bool(result['action_needed']),
                                    'type': json.loads(result['action_type']) if result['action_type'] else [],
                                    'deadline': result['action_deadline']
                                },
                                'key_points': json.loads(result['key_points']) if result['key_points'] else [],
                                'people_mentioned': json.loads(result['people_mentioned']) if result['people_mentioned'] else [],
                                'links': {
                                    'found': json.loads(result['links_found']) if result['links_found'] else [],
                                    'display': json.loads(result['links_display']) if result['links_display'] else []
                                },
                                'project': result['project'] or '',
                                'topic': result['topic'] or '',
                                'sentiment': result['sentiment'],
                                'confidence_score': result['confidence_score'],
                                'full_api_response': result['full_api_response']
                            }
                            analyses.append(analysis)
                    else:
                        email = email_session.query(Email).filter(Email.id == result.email_id).first()
                        if email:
                            analysis = {
                                'email_id': result.email_id,
                                'thread_id': result.thread_id,
                                'analysis_date': result.analysis_date,
                                'subject': email.subject,
                                'sender': email.sender,
                                'summary': result.summary,
                                'category': result.category if isinstance(result.category, list) else json.loads(result.category) if result.category else [],
                                'priority': {
                                    'score': result.priority_score,
                                    'reason': result.priority_reason
                                },
                                'action': {
                                    'needed': bool(result.action_needed),
                                    'type': result.action_type if isinstance(result.action_type, list) else json.loads(result.action_type) if result.action_type else [],
                                    'deadline': result.action_deadline.isoformat() if result.action_deadline else ''
                                },
                                'key_points': result.key_points if isinstance(result.key_points, list) else json.loads(result.key_points) if result.key_points else [],
                                'people_mentioned': result.people_mentioned if isinstance(result.people_mentioned, list) else json.loads(result.people_mentioned) if result.people_mentioned else [],
                                'links': {
                                    'found': result.links_found if isinstance(result.links_found, list) else json.loads(result.links_found) if result.links_found else [],
                                    'display': result.links_display if isinstance(result.links_display, list) else json.loads(result.links_display) if result.links_display else []
                                },
                                'project': result.project or '',
                                'topic': result.topic or '',
                                'sentiment': result.sentiment,
                                'confidence_score': result.confidence_score,
                                'full_api_response': result.full_api_response
                            }
                            analyses.append(analysis)
        
        return analyses

    def get_priority_distribution(self):
        """Get distribution of priority scores."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("""
                    SELECT priority_score, COUNT(*) as count 
                    FROM email_analysis 
                    WHERE priority_score IS NOT NULL 
                    GROUP BY priority_score
                """)
                results = cursor.fetchall()
            else:
                results = session.query(EmailAnalysis.priority_score).all()
                results = Counter(score[0] for score in results if score[0] is not None).items()

            priorities = {}
            for score, count in results:
                if score >= 3:
                    priorities['High (3)'] = priorities.get('High (3)', 0) + count
                elif score >= 2:
                    priorities['Medium (2)'] = priorities.get('Medium (2)', 0) + count
                else:
                    priorities['Low (1)'] = priorities.get('Low (1)', 0) + count
            return priorities

    def get_sentiment_distribution(self):
        """Get distribution of sentiment analysis."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("""
                    SELECT sentiment, COUNT(*) as count 
                    FROM email_analysis 
                    WHERE sentiment IS NOT NULL 
                    GROUP BY sentiment
                """)
                return dict(cursor.fetchall())
            else:
                results = session.query(EmailAnalysis.sentiment).all()
                return dict(Counter(s[0] for s in results if s[0]))

    def get_action_needed_distribution(self):
        """Get distribution of emails needing action."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("""
                    SELECT action_needed, COUNT(*) as count 
                    FROM email_analysis 
                    GROUP BY action_needed
                """)
                return dict((bool(k), v) for k, v in cursor.fetchall())
            else:
                results = session.query(EmailAnalysis.action_needed).all()
                return dict(Counter(bool(a[0]) for a in results))

    def get_project_distribution(self):
        """Get distribution of projects."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("""
                    SELECT project, COUNT(*) as count 
                    FROM email_analysis 
                    WHERE project IS NOT NULL AND project != ''
                    GROUP BY project
                """)
                return dict(cursor.fetchall())
            else:
                results = session.query(EmailAnalysis.project).filter(EmailAnalysis.project != None, EmailAnalysis.project != '').all()
                return dict(Counter(p[0] for p in results))

    def get_topic_distribution(self):
        """Get distribution of topics."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("""
                    SELECT topic, COUNT(*) as count 
                    FROM email_analysis 
                    WHERE topic IS NOT NULL AND topic != ''
                    GROUP BY topic
                """)
                return dict(cursor.fetchall())
            else:
                results = session.query(EmailAnalysis.topic).filter(EmailAnalysis.topic != None, EmailAnalysis.topic != '').all()
                return dict(Counter(t[0] for t in results))

    def get_category_distribution(self):
        """Get distribution of categories."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("SELECT category FROM email_analysis")
                results = cursor.fetchall()
            else:
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

    def get_confidence_distribution(self):
        """Get distribution of confidence scores."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("""
                    SELECT confidence_score, COUNT(*) as count 
                    FROM email_analysis 
                    WHERE confidence_score IS NOT NULL 
                    GROUP BY confidence_score
                """)
                results = cursor.fetchall()
            else:
                results = session.query(EmailAnalysis.confidence_score).all()
                results = Counter(score[0] for score in results if score[0] is not None).items()

            confidence_dist = []
            for score, count in results:
                if score >= 0.9:
                    confidence_dist.append(('0.9-1.0', count))
                elif score >= 0.8:
                    confidence_dist.append(('0.8-0.89', count))
                elif score >= 0.7:
                    confidence_dist.append(('0.7-0.79', count))
                elif score >= 0.6:
                    confidence_dist.append(('0.6-0.69', count))
                else:
                    confidence_dist.append(('<0.6', count))
            
            return confidence_dist

    def get_analysis_by_date(self):
        """Get analysis distribution by date."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("""
                    SELECT analysis_date, COUNT(*) as count 
                    FROM email_analysis 
                    GROUP BY analysis_date 
                    ORDER BY analysis_date DESC
                """)
                return cursor.fetchall()
            else:
                results = session.query(EmailAnalysis.analysis_date).all()
                date_counts = Counter(d[0].date() for d in results)
                return list(date_counts.items())

    def get_detailed_analysis(self, email_id):
        """Get detailed analysis for a specific email."""
        with self._get_analysis_session() as analysis_session:
            if isinstance(analysis_session, sqlite3.Connection):
                cursor = analysis_session.cursor()
                cursor.execute("""
                    SELECT * FROM email_analysis 
                    WHERE email_id = ?
                """, (email_id,))
                result = cursor.fetchone()
                if not result:
                    return None

                # Get email details
                email_cursor = self._get_email_session().cursor()
                email_cursor.execute("""
                    SELECT * FROM emails 
                    WHERE id = ?
                """, (email_id,))
                email = email_cursor.fetchone()
                if not email:
                    return None

                # Map column indices to names
                analysis_cols = [desc[0] for desc in cursor.description]
                email_cols = [desc[0] for desc in email_cursor.description]
                
                # Create result object with column names
                result_dict = dict(zip(analysis_cols, result))
                email_dict = dict(zip(email_cols, email))

                analysis = {
                    'email_id': result_dict['email_id'],
                    'thread_id': result_dict['thread_id'],
                    'analysis_date': result_dict['analysis_date'],
                    'subject': email_dict['subject'],
                    'sender': email_dict['from_address'],
                    'summary': result_dict['summary'],
                    'category': json.loads(result_dict['category']) if result_dict['category'] else [],
                    'priority': {
                        'score': result_dict['priority_score'],
                        'reason': result_dict['priority_reason']
                    },
                    'action': {
                        'needed': bool(result_dict['action_needed']),
                        'type': json.loads(result_dict['action_type']) if result_dict['action_type'] else [],
                        'deadline': result_dict['action_deadline']
                    },
                    'key_points': json.loads(result_dict['key_points']) if result_dict['key_points'] else [],
                    'people_mentioned': json.loads(result_dict['people_mentioned']) if result_dict['people_mentioned'] else [],
                    'links': {
                        'found': json.loads(result_dict['links_found']) if result_dict['links_found'] else [],
                        'display': json.loads(result_dict['links_display']) if result_dict['links_display'] else []
                    },
                    'project': result_dict['project'] or '',
                    'topic': result_dict['topic'] or '',
                    'sentiment': result_dict['sentiment'],
                    'confidence_score': result_dict['confidence_score'],
                    'full_api_response': result_dict['full_api_response']
                }
                return analysis
            else:
                # Handle SQLAlchemy session
                result = analysis_session.query(EmailAnalysis).filter(EmailAnalysis.email_id == email_id).first()
                if not result:
                    return None
                
                email = self._get_email_session().query(Email).filter(Email.id == email_id).first()
                if not email:
                    return None
                
                analysis = {
                    'email_id': result.email_id,
                    'thread_id': result.thread_id,
                    'analysis_date': result.analysis_date,
                    'subject': email.subject,
                    'sender': email.sender,
                    'summary': result.summary,
                    'category': result.category if isinstance(result.category, list) else json.loads(result.category) if result.category else [],
                    'priority': {
                        'score': result.priority_score,
                        'reason': result.priority_reason
                    },
                    'action': {
                        'needed': bool(result.action_needed),
                        'type': result.action_type if isinstance(result.action_type, list) else json.loads(result.action_type) if result.action_type else [],
                        'deadline': result.action_deadline.isoformat() if result.action_deadline else ''
                    },
                    'key_points': result.key_points if isinstance(result.key_points, list) else json.loads(result.key_points) if result.key_points else [],
                    'people_mentioned': result.people_mentioned if isinstance(result.people_mentioned, list) else json.loads(result.people_mentioned) if result.people_mentioned else [],
                    'links': {
                        'found': result.links_found if isinstance(result.links_found, list) else json.loads(result.links_found) if result.links_found else [],
                        'display': result.links_display if isinstance(result.links_display, list) else json.loads(result.links_display) if result.links_display else []
                    },
                    'project': result.project or '',
                    'topic': result.topic or '',
                    'sentiment': result.sentiment,
                    'confidence_score': result.confidence_score,
                    'full_api_response': result.full_api_response
                }
                return analysis

    def get_analysis_by_category(self, category):
        """Get all analyses with a specific category."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("SELECT email_id, category FROM email_analysis")
                results = cursor.fetchall()
                matching_ids = []
                for result in results:
                    email_id, category_str = result
                    categories = json.loads(category_str) if category_str else []
                    if category in categories:
                        matching_ids.append(email_id)
                return self._get_analyses_from_ids(matching_ids)
            else:
                results = session.query(EmailAnalysis).all()
                matching_ids = []
                for result in results:
                    categories = result.category if isinstance(result.category, list) else json.loads(result.category) if result.category else []
                    if category in categories:
                        matching_ids.append(result.email_id)
                return self._get_analyses_from_ids(matching_ids)

    def get_analysis_stats(self):
        """Get overall analysis statistics."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_analyzed,
                        ROUND(AVG(confidence_score), 2) as avg_confidence,
                        ROUND(AVG(priority_score), 2) as avg_priority,
                        COUNT(CASE WHEN action_needed = 1 THEN 1 END) as action_needed_count,
                        COUNT(CASE WHEN priority_score >= 3 THEN 1 END) as high_priority_count,
                        COUNT(CASE WHEN sentiment = 'positive' THEN 1 END) as positive_count,
                        COUNT(CASE WHEN sentiment = 'negative' THEN 1 END) as negative_count,
                        COUNT(CASE WHEN sentiment = 'neutral' THEN 1 END) as neutral_count,
                        COUNT(DISTINCT project) as total_projects,
                        COUNT(DISTINCT topic) as total_topics
                    FROM email_analysis
                    WHERE confidence_score IS NOT NULL
                """)
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    stats = dict(zip(columns, row))
                    # Add sentiment_counts dictionary
                    stats['sentiment_counts'] = {
                        'positive': stats.pop('positive_count', 0),
                        'negative': stats.pop('negative_count', 0),
                        'neutral': stats.pop('neutral_count', 0)
                    }
                else:
                    stats = {
                        'total_analyzed': 0,
                        'avg_confidence': 0,
                        'avg_priority': 0,
                        'action_needed_count': 0,
                        'high_priority_count': 0,
                        'total_projects': 0,
                        'total_topics': 0,
                        'sentiment_counts': {
                            'positive': 0,
                            'negative': 0,
                            'neutral': 0
                        }
                    }
            else:
                total_analyzed = session.query(EmailAnalysis).filter(EmailAnalysis.confidence_score.isnot(None)).count()
                avg_confidence = session.query(func.round(func.avg(EmailAnalysis.confidence_score), 2)).scalar() or 0
                avg_priority = session.query(func.round(func.avg(EmailAnalysis.priority_score), 2)).scalar() or 0
                action_needed_count = session.query(EmailAnalysis).filter(EmailAnalysis.action_needed == True).count()
                high_priority_count = session.query(EmailAnalysis).filter(EmailAnalysis.priority_score >= 3).count()
                positive_count = session.query(EmailAnalysis).filter(EmailAnalysis.sentiment == 'positive').count()
                negative_count = session.query(EmailAnalysis).filter(EmailAnalysis.sentiment == 'negative').count()
                neutral_count = session.query(EmailAnalysis).filter(EmailAnalysis.sentiment == 'neutral').count()
                total_projects = session.query(func.count(func.distinct(EmailAnalysis.project))).scalar()
                total_topics = session.query(func.count(func.distinct(EmailAnalysis.topic))).scalar()

                stats = {
                    'total_analyzed': total_analyzed,
                    'avg_confidence': float(avg_confidence),
                    'avg_priority': float(avg_priority),
                    'action_needed_count': action_needed_count,
                    'high_priority_count': high_priority_count,
                    'total_projects': total_projects,
                    'total_topics': total_topics,
                    'sentiment_counts': {
                        'positive': positive_count,
                        'negative': negative_count,
                        'neutral': neutral_count
                    }
                }

            return stats

    def get_analysis_with_action_needed(self) -> List[Dict]:
        """Get analyses that require action."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                email_ids = self._execute_sqlite_query(
                    session,
                    "SELECT email_id FROM email_analysis WHERE action_needed = 1"
                )
                return self._get_analyses_from_ids(email_ids)
            else:
                results = session.query(EmailAnalysis).filter(EmailAnalysis.action_needed == True).all()
                return [self._format_analysis(analysis) for analysis in results]

    def get_high_priority_analysis(self) -> List[Dict]:
        """Get high priority analyses (priority_score >= 3)."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                email_ids = self._execute_sqlite_query(
                    session,
                    "SELECT email_id FROM email_analysis WHERE priority_score >= 3"
                )
                return self._get_analyses_from_ids(email_ids)
            else:
                results = session.query(EmailAnalysis).filter(EmailAnalysis.priority_score >= 3).all()
                return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_sentiment(self, sentiment: str) -> List[Dict]:
        """Get analyses by sentiment (positive/negative/neutral)."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                email_ids = self._execute_sqlite_query(
                    session,
                    "SELECT email_id FROM email_analysis WHERE sentiment = ?",
                    (sentiment,)
                )
                return self._get_analyses_from_ids(email_ids)
            else:
                results = session.query(EmailAnalysis).filter(EmailAnalysis.sentiment == sentiment).all()
                return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_project(self, project: str) -> List[Dict]:
        """Get analyses by project."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                email_ids = self._execute_sqlite_query(
                    session,
                    "SELECT email_id FROM email_analysis WHERE project = ?",
                    (project,)
                )
                return self._get_analyses_from_ids(email_ids)
            else:
                results = session.query(EmailAnalysis).filter(EmailAnalysis.project == project).all()
                return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_topic(self, topic: str) -> List[Dict]:
        """Get analyses by topic."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                email_ids = self._execute_sqlite_query(
                    session,
                    "SELECT email_id FROM email_analysis WHERE topic = ?",
                    (topic,)
                )
                return self._get_analyses_from_ids(email_ids)
            else:
                results = session.query(EmailAnalysis).filter(EmailAnalysis.topic == topic).all()
                return [self._format_analysis(analysis) for analysis in results]

    def get_analysis_by_category(self, category: str) -> List[Dict]:
        """Get all analyses with a specific category."""
        with self._get_analysis_session() as session:
            if isinstance(session, sqlite3.Connection):
                cursor = session.cursor()
                cursor.execute("SELECT email_id, category FROM email_analysis")
                results = cursor.fetchall()
                matching_ids = []
                for result in results:
                    email_id, category_str = result
                    categories = json.loads(category_str) if category_str else []
                    if category in categories:
                        matching_ids.append(email_id)
                return self._get_analyses_from_ids(matching_ids)
            else:
                results = session.query(EmailAnalysis).all()
                matching_ids = []
                for result in results:
                    categories = result.category if isinstance(result.category, list) else json.loads(result.category) if result.category else []
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
            'email_id': analysis.email_id,
            'thread_id': analysis.thread_id,
            'date': analysis.analysis_date.isoformat(),
            'summary': analysis.summary,
            'category': analysis.category if isinstance(analysis.category, list) else json.loads(analysis.category) if analysis.category else [],
            'priority': {
                'score': analysis.priority_score,
                'reason': analysis.priority_reason
            },
            'action': {
                'needed': bool(analysis.action_needed),
                'type': analysis.action_type if isinstance(analysis.action_type, list) else json.loads(analysis.action_type) if analysis.action_type else [],
                'deadline': analysis.action_deadline.isoformat() if analysis.action_deadline else None
            },
            'key_points': analysis.key_points if isinstance(analysis.key_points, list) else json.loads(analysis.key_points) if analysis.key_points else [],
            'people_mentioned': analysis.people_mentioned if isinstance(analysis.people_mentioned, list) else json.loads(analysis.people_mentioned) if analysis.people_mentioned else [],
            'links': {
                'found': analysis.links_found if isinstance(analysis.links_found, list) else json.loads(analysis.links_found) if analysis.links_found else [],
                'display': analysis.links_display if isinstance(analysis.links_display, list) else json.loads(analysis.links_display) if analysis.links_display else []
            },
            'project': analysis.project or '',
            'topic': analysis.topic or '',
            'sentiment': analysis.sentiment,
            'confidence_score': analysis.confidence_score,
            'full_api_response': analysis.full_api_response
        }

    def generate_report(self):
        """Generate a summary report of email data.
        
        Returns:
            Dictionary containing report data
        """
        with self._get_email_session() as session:
            # Get total emails
            total_emails = self.get_total_emails()

            # Get date range
            date_range = session.query(
                func.min(Email.received_date).label('oldest'),
                func.max(Email.received_date).label('newest')
            ).first()

            # Get top senders
            top_senders = session.query(
                Email.from_address,
                func.count(Email.id).label('count')
            ).group_by(Email.from_address).order_by(desc('count')).limit(10).all()

            # Get top recipients
            top_recipients = session.query(
                Email.to_address,
                func.count(Email.id).label('count')
            ).group_by(Email.to_address).order_by(desc('count')).limit(10).all()

            report = {
                'total_emails': total_emails,
                'date_range': {
                    'oldest': date_range.oldest if date_range else None,
                    'newest': date_range.newest if date_range else None
                },
                'top_senders': [{'email': s[0], 'count': s[1]} for s in top_senders],
                'top_recipients': [{'email': r[0], 'count': r[1]} for r in top_recipients]
            }

            return report

    def print_analysis_report(self):
        """Print a comprehensive analysis report."""
        print("\n=== Email Analysis Report ===\n")
        
        # Get total analyzed emails
        total = self.get_total_emails()
        print(f"Total Analyzed Emails: {total}\n")
        
        # Priority Distribution
        print("\nPriority Distribution:")
        priorities = self.get_priority_distribution()
        for score, count in priorities.items():
            print(f"  {score}: {count} emails ({count/total*100:.1f}%)")
        
        # Action Types
        print("\nAction Type Distribution:")
        actions = self.get_action_needed_distribution()
        for action, count in actions.items():
            print(f"  {action}: {count} emails")
        
        # Categories
        print("\nTop Categories:")
        categories = self.get_category_distribution()
        for category, count in categories.items():
            print(f"  {category}: {count} emails")
        
        # Sentiment
        print("\nSentiment Distribution:")
        sentiments = self.get_sentiment_distribution()
        for sentiment, count in sentiments.items():
            print(f"  {sentiment}: {count} emails ({count/total*100:.1f}%)")
        
        # Topic Distribution
        print("\nTop Email Topics (AI Analysis):")
        topics = self.get_topic_distribution()
        if topics:
            print(tabulate(
                [[topic, count] for topic, count in topics.items()],
                headers=['Topic', 'Count'],
                tablefmt='pipe'
            ))
        print()
        
        # Project Distribution
        print("Project Distribution (AI Analysis):")
        projects = self.get_project_distribution()
        if projects:
            print(tabulate(
                [[project, count] for project, count in projects.items()],
                headers=['Project', 'Count'],
                tablefmt='pipe'
            ))
        print()
        
        # Confidence Distribution
        print("\nConfidence Distribution:")
        confidence_dist = self.get_confidence_distribution()
        print(tabulate(confidence_dist, headers=['Confidence Level', 'Count'], tablefmt='psql'))
        print()
        
        # Recent Analysis
        print("Recent Email Analysis:\n")
        analysis = self.get_anthropic_analysis()
        if analysis:
            for email in analysis:
                print(f"Email: {email['subject']}")
                print(f"From: {email['sender']}")
                print(f"Summary: {email['summary']}")
                if email.get('topics'):
                    print(f"Topics: {', '.join(email['topics'])}")
                if email.get('project'):
                    print(f"Project: {email['project']}")
                print(f"Sentiment: {email['sentiment']}")
                if email.get('action_items'):
                    action_items = email['action_items']
                    if action_items:
                        print(f"Action Items: {', '.join(action_items)}")
                print("-" * 80 + "\n")

    def show_basic_stats(self):
        """Show basic email statistics."""
        print("\nBasic Email Statistics:")
        print(f"Total Emails: {self.get_total_emails()}")
        print(f"Top Senders: {self.get_top_senders()}")
        print(f"Email Distribution by Date: {self.get_email_by_date()}")
        print(f"Label Distribution: {self.get_label_distribution()}")

    def show_top_senders(self):
        """Show top email senders."""
        print("\nTop Email Senders:")
        top_senders = self.get_top_senders()
        print(tabulate(top_senders, headers=['Sender', 'Count'], tablefmt='psql'))

    def show_email_distribution(self):
        """Show email distribution by date."""
        print("\nEmail Distribution by Date:")
        date_dist = self.get_email_by_date()
        print(tabulate(date_dist, headers=['Date', 'Count'], tablefmt='psql'))

    def show_label_distribution(self):
        """Show label distribution."""
        print("\nLabel Distribution:")
        label_dist = self.get_label_distribution()
        print(tabulate(label_dist.items(), headers=['Label', 'Count'], tablefmt='psql'))

    def show_ai_analysis_summary(self):
        """Show AI analysis summary."""
        print("\nAI Analysis Summary:")
        analysis_data = self.get_anthropic_analysis()
        if analysis_data:
            for analysis in analysis_data[:5]:
                print(f"\nEmail: {analysis['subject']}")
                print(f"From: {analysis['sender']}")
                print(f"Summary: {analysis['summary']}")
                print(f"Topics: {', '.join(analysis['topic'])}")
                print(f"Sentiment: {analysis['sentiment']}")
                if analysis['action']['needed']:
                    print(f"Action Needed: {analysis['action']['needed']}")
                    print(f"Action Type: {', '.join(analysis['action']['type'])}")
                    print(f"Action Deadline: {analysis['action']['deadline']}")
                print("-" * 80)

    def show_confidence_distribution(self):
        """Show confidence distribution."""
        print("\nConfidence Distribution:")
        confidence_dist = self.get_confidence_distribution()
        print(tabulate(confidence_dist, headers=['Confidence Level', 'Count'], tablefmt='psql'))

def sync_gmail_labels():
    """Sync Gmail labels with local database."""
    from lib_gmail import GmailAPI
    
    # Initialize Gmail API and sync labels
    gmail = GmailAPI()
    gmail.sync_labels()

def print_menu():
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
    if report_type == 'basic':
        print(f"\nTotal Emails: {analytics.get_total_emails()}")
    
    elif report_type == 'senders':
        print("\nTop Email Senders:")
        top_senders = analytics.get_top_senders()
        print(tabulate(top_senders, headers=['Sender', 'Count'], tablefmt='psql'))
    
    elif report_type == 'dates':
        print("\nEmail Distribution by Date:")
        date_dist = analytics.get_email_by_date()
        print(tabulate(date_dist, headers=['Date', 'Count'], tablefmt='psql'))
    
    elif report_type == 'labels':
        print("\nTop Email Labels:")
        label_dist = analytics.get_label_distribution()
        print(tabulate(label_dist.items(), headers=['Label', 'Count'], tablefmt='psql'))
    
    elif report_type == 'analysis':
        print("\nAI Analysis Summary:")
        analysis_data = analytics.get_anthropic_analysis()
        if analysis_data:
            for analysis in analysis_data[:5]:
                print(f"\nEmail: {analysis['subject']}")
                print(f"From: {analysis['sender']}")
                print(f"Summary: {analysis['summary']}")
                print(f"Topics: {', '.join(analysis['topic'])}")
                print(f"Sentiment: {analysis['sentiment']}")
                if analysis['action']['needed']:
                    print(f"Action Needed: {analysis['action']['needed']}")
                    print(f"Action Type: {', '.join(analysis['action']['type'])}")
                    print(f"Action Deadline: {analysis['action']['deadline']}")
                print("-" * 80)
    
    elif report_type == 'full':
        analytics.print_analysis_report()
    
    elif report_type == 'confidence':
        print("\nConfidence Distribution:")
        confidence_dist = analytics.get_confidence_distribution()
        print(tabulate(confidence_dist, headers=['Confidence Level', 'Count'], tablefmt='psql'))
    
    elif report_type == 'all':
        # Run all reports in sequence
        for report in ['basic', 'senders', 'dates', 'labels', 'analysis', 'confidence']:
            run_report(analytics, report)
            print("\n" + "="*80 + "\n")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Email Analytics Reports')
    parser.add_argument('--report', choices=['basic', 'senders', 'dates', 'labels', 'analysis', 'full', 'confidence', 'all'],
                      help='Type of report to run. If not specified, starts interactive menu.')
    args = parser.parse_args()
    
    # Sync labels first
    sync_gmail_labels()
    
    analytics = EmailAnalytics()
    
    try:
        if args.report:
            # Run specific report
            run_report(analytics, args.report)
        else:
            # Interactive menu
            while True:
                print_menu()
                choice = input("\nEnter your choice (1-8): ")
                
                if choice == '1':
                    run_report(analytics, 'basic')
                elif choice == '2':
                    run_report(analytics, 'senders')
                elif choice == '3':
                    run_report(analytics, 'dates')
                elif choice == '4':
                    run_report(analytics, 'labels')
                elif choice == '5':
                    run_report(analytics, 'analysis')
                elif choice == '6':
                    run_report(analytics, 'full')
                elif choice == '7':
                    run_report(analytics, 'confidence')
                elif choice == '8':
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
