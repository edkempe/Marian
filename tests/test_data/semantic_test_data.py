"""Test data for semantic search functionality."""

from typing import List, Tuple

from models.catalog import CatalogEntry


def get_test_items() -> List[CatalogEntry]:
    """Get test catalog entries for semantic search."""
    return [
        CatalogEntry(
            title="Python Programming Tutorial",
            description="A comprehensive guide to Python programming for beginners",
            tags=["python", "programming", "tutorial"],
            extra_metadata={"difficulty": "beginner"}
        ),
        CatalogEntry(
            title="Advanced Machine Learning",
            description="Deep dive into machine learning algorithms and techniques",
            tags=["machine-learning", "ai", "advanced"],
            extra_metadata={"difficulty": "advanced"}
        ),
        CatalogEntry(
            title="Data Science with Python",
            description="Using Python for data analysis and visualization",
            tags=["python", "data-science", "analysis"],
            extra_metadata={"difficulty": "intermediate"}
        ),
        CatalogEntry(
            title="Web Development Basics",
            description="Introduction to HTML, CSS, and JavaScript",
            tags=["web", "html", "css", "javascript"],
            extra_metadata={"difficulty": "beginner"}
        ),
        CatalogEntry(
            title="Database Design",
            description="Principles of relational database design and SQL",
            tags=["database", "sql", "design"],
            extra_metadata={"difficulty": "intermediate"}
        )
    ]


def get_similar_titles() -> List[Tuple[str, List[str]]]:
    """Get pairs of similar titles for testing semantic similarity."""
    return [
        (
            "Python Programming Tutorial",
            [
                "Python for Beginners",
                "Getting Started with Python",
                "Python Basics Guide"
            ]
        ),
        (
            "Advanced Machine Learning",
            [
                "Deep Learning Techniques",
                "AI and Machine Learning",
                "Machine Learning Advanced Topics"
            ]
        ),
        (
            "Data Science with Python",
            [
                "Python Data Analysis",
                "Data Analytics using Python",
                "Python for Data Scientists"
            ]
        ),
        (
            "Web Development Basics",
            [
                "Frontend Development 101",
                "Web Development Fundamentals",
                "HTML and CSS Basics"
            ]
        ),
        (
            "Database Design",
            [
                "SQL Database Design",
                "Relational Database Principles",
                "Database Architecture"
            ]
        )
    ]
