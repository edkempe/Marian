"""Test data for semantic search testing."""

from typing import List, Tuple

from models.catalog import CatalogItem

# Real-world programming Q&A pairs from Stack Exchange
# Format: (title, content, [similar_titles])
PROGRAMMING_QA: List[Tuple[str, str, List[str]]] = [
    (
        "How to read a file line by line in Python",
        "I need to read a text file line by line in Python. What's the most efficient way?",
        ["Reading files in Python", "Python file handling basics"],
    ),
    (
        "Reading files in Python",
        "What are the different methods to read files in Python? Looking for both line-by-line and bulk reading approaches.",
        ["How to read a file line by line in Python", "Python file I/O tutorial"],
    ),
    (
        "Understanding Python decorators",
        "Can someone explain how decorators work in Python? Looking for a clear explanation with examples.",
        ["Python decorator patterns", "Advanced Python decorators"],
    ),
    (
        "Python decorator patterns",
        "What are some common patterns and use cases for Python decorators? Including property, classmethod, etc.",
        ["Understanding Python decorators", "Advanced Python decorators"],
    ),
    (
        "Git merge vs rebase",
        "What's the difference between git merge and git rebase? When should I use each one?",
        ["Git branching strategies", "Understanding Git workflow"],
    ),
    (
        "Git branching strategies",
        "What are the best practices for branching in Git? Including feature branches, release branches, etc.",
        ["Git merge vs rebase", "Git workflow best practices"],
    ),
    (
        "Data Structures for Efficient Memory Usage",
        "How to choose and implement data structures for optimal memory efficiency in Python",
        ["Python Memory Management", "Optimizing Data Storage"],
    ),
    (
        "Database Memory Optimization",
        "Techniques for efficient memory usage in database systems, including caching and indexing",
        ["Data Structures for Efficient Memory Usage", "Database Performance Tuning"],
    ),
    (
        "Python OOP Guide",
        "Comprehensive guide to Object-Oriented Programming in Python with practical examples",
        ["Python Class Tutorial", "Object-Oriented Python"],
    ),
    (
        "Python Beginner's Class",
        "A beginner-friendly introduction to Python programming language",
        ["Python Tutorial for Beginners", "Getting Started with Python"],
    ),
    (
        "Modern Python File Handling",
        "File handling in Python 3.8+ including async/await patterns and context managers",
        ["Async File Operations", "Python 3 I/O Guide"],
    ),
    (
        "Legacy Python File Operations",
        "File handling in Python 2.7 and migration guide to Python 3",
        ["Python 2 to 3 Migration", "Classic Python Guide"],
    ),
    (
        "Video: Python Decorator Workshop",
        "Video tutorial explaining Python decorators with live coding examples",
        ["Python Decorator Tutorial", "Learn Decorators by Example"],
    ),
    (
        "Interactive Python Guide",
        "Interactive notebook with Python programming exercises and examples",
        ["Hands-on Python Tutorial", "Python Practice Guide"],
    ),
    (
        "Python Anti-Patterns",
        "Common Python anti-patterns and how to avoid them, including global variables",
        ["Python Best Practices", "What Not To Do in Python"],
    ),
    (
        "Clean Git Workflow",
        "How to maintain a clean Git history and avoid common merge conflicts",
        ["Git Best Practices", "Conflict-Free Git Strategy", "Enterprise Git Workflow"],
    ),
    (
        "Python File Reading Examples",
        "Examples of reading files in Python using with open() and file.read()",
        ["File I/O in Python", "Python File Handling"],
    ),
    (
        "File I/O Best Practices",
        "Best practices for file input/output operations in Python",
        ["Python File Reading Examples", "File Handling Guide"],
    ),
]

# Edge cases and special scenarios
EDGE_CASES: List[Tuple[str, str, List[str]]] = [
    ("", "Some content", []),  # Empty title
    ("   ", "Some content", []),  # Whitespace title
    (
        "!@#$%^",  # Special characters
        "Title with special characters !@#$%^",
        ["Special !@#$%^ characters"],
    ),
    (
        "Very " * 20 + "long title",  # Very long title
        "Content " * 100,  # Very long content
        ["Another long " * 10 + "title"],
    ),
    ("Short", "Brief", []),
    (
        "Pythno Progrming Basics",
        "Basic Pythno tutorials for begnners",
        ["Python Programming Basics", "Python Tutorial"],
    ),
    (
        "Djano Frammework Guide",
        "Tutorial for Djano web devlopment",
        ["Django Framework Tutorial", "Web Development with Django"],
    ),
    (
        "URGENT!!! Python Help Needed",
        "Please help with Python programming ASAP!!!",
        ["Python Programming Help", "Python Support"],
    ),
    (
        "Looking for quick answer - Python file reading question",
        "How do I read files in Python? Need answer quickly for project due tomorrow!",
        ["Python File Reading", "File Handling in Python"],
    ),
]

# Domain-specific technical content
TECHNICAL_DOCS: List[Tuple[str, str, List[str]]] = [
    (
        "RESTful API Design Principles",
        "Best practices for designing RESTful APIs including versioning, authentication, and resource naming.",
        ["API Design Guidelines", "REST API Best Practices"],
    ),
    (
        "API Design Guidelines",
        "Comprehensive guide to designing clean and maintainable APIs, covering REST, GraphQL, and gRPC.",
        ["RESTful API Design Principles", "API Development Standards"],
    ),
    (
        "Database Indexing Strategies",
        "How to effectively use database indexes to improve query performance. Covers B-tree, hash, and bitmap indexes.",
        ["Database Performance Tuning", "SQL Query Optimization"],
    ),
    (
        "SQL Query Optimization",
        "Techniques for optimizing SQL queries including index usage, join optimization, and query planning.",
        ["Database Indexing Strategies", "Database Performance Tuning"],
    ),
    (
        "Enterprise Git Workflow",
        "Git workflow patterns for large teams and enterprise software development",
        ["Git Branching Strategies", "Corporate Version Control", "Clean Git Workflow"],
    ),
    (
        "Microservices Architecture Patterns",
        "Design patterns and best practices for microservices architecture",
        ["Distributed Systems Design", "Service-Oriented Architecture"],
    ),
    (
        "Full-Stack Performance Optimization",
        "End-to-end performance optimization covering frontend, backend, and database",
        ["Web Performance Guide", "System Optimization Techniques"],
    ),
    (
        "Cloud-Native Development",
        "Building and deploying applications for cloud platforms",
        ["Modern Application Architecture", "Cloud Development Guide"],
    ),
]

# Short-form content like tags and brief descriptions
SHORT_FORM: List[Tuple[str, str, List[str]]] = [
    ("python", "Programming language", ["py", "python3", "programming"]),
    ("ml", "Machine learning", ["machine-learning", "ai", "deep-learning"]),
    ("api", "Application Programming Interface", ["rest", "web-api", "endpoints"]),
    ("db", "Database", ["database", "sql", "storage"]),
    ("ui", "User Interface", ["frontend", "ux", "interface"]),
    ("dev", "Development", ["development", "programming", "coding"]),
    ("bug", "Software defect", ["issue", "error", "defect"]),
    ("doc", "Documentation", ["docs", "manual", "guide"]),
]

# Additional test data categories
NOISE_VARIATIONS: List[Tuple[str, str, List[str]]] = [
    (
        "Python Basics",
        "Basic Python programming concepts",
        ["Python Programming", "Learn Python"],
    ),
    (
        "Pythno Bassics",  # With typos
        "Bassic Pythno programming conceptss",
        ["Python Basics", "Python Programming"],
    ),
    (
        "HELP! Python Basics!!!",  # With noise
        "URGENT! Need help with basic Python programming!!!",
        ["Python Basics", "Python Help"],
    ),
]

VERSION_SPECIFIC: List[Tuple[str, str, List[str]]] = [
    (
        "Python 3.9 Features",
        "New features and improvements in Python 3.9",
        ["Modern Python Guide", "Python Updates"],
    ),
    (
        "Legacy Python Guide",
        "Guide for maintaining and migrating Python 2.x code",
        ["Python Migration Guide", "Python 2 Support"],
    ),
]


def get_test_items(category: str = "programming") -> List[CatalogItem]:
    """Get test items for a specific category."""
    data_map = {
        "programming": PROGRAMMING_QA,
        "edge_cases": EDGE_CASES,
        "technical": TECHNICAL_DOCS,
        "noise": NOISE_VARIATIONS,
        "versions": VERSION_SPECIFIC,
        "short": SHORT_FORM,
    }

    if category not in data_map:
        raise ValueError(f"Unknown category: {category}")

    return [
        CatalogItem(title=title, content=content)
        for title, content, _ in data_map[category]
    ]


def get_similar_titles(title: str, category: str = "programming") -> List[str]:
    """Get known similar titles for a given title."""
    data_map = {
        "programming": PROGRAMMING_QA,
        "edge_cases": EDGE_CASES,
        "technical": TECHNICAL_DOCS,
        "noise": NOISE_VARIATIONS,
        "versions": VERSION_SPECIFIC,
        "short": SHORT_FORM,
    }

    if category not in data_map:
        raise ValueError(f"Unknown category: {category}")

    for t, _, similar in data_map[category]:
        if t == title:
            return similar

    return []
