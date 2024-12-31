"""Test suite for development process quality.

This module focuses on process-related quality checks:
1. Git workflow standards
2. Testing practices
3. Performance monitoring
4. Data handling patterns
5. Industry standards compliance
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

@dataclass
class ProcessMetric:
    """Represents a process quality metric."""
    name: str
    value: float
    threshold: float
    description: str


def get_git_info() -> Dict:
    """Get Git repository information."""
    project_root = Path(__file__).parent.parent
    info = {}

    try:
        # Check for git hooks
        hooks_dir = project_root / ".git" / "hooks"
        if hooks_dir.exists():
            info["hooks"] = [
                f.name
                for f in hooks_dir.iterdir()
                if f.is_file() and not f.name.endswith(".sample")
            ]

        # Get branch naming patterns
        result = subprocess.run(
            ["git", "branch"], cwd=project_root, capture_output=True, text=True
        )
        if result.returncode == 0:
            branches = result.stdout.split("\n")
            info["branches"] = [b.strip("* ") for b in branches if b.strip()]

        # Get commit message patterns
        result = subprocess.run(
            ["git", "log", "--format=%s", "-n", "50"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            info["commits"] = result.stdout.split("\n")

        # Check for git configuration
        git_configs = [
            project_root / ".gitignore",
            project_root / ".gitattributes",
            project_root / ".github",
        ]
        info["configs"] = [
            str(cfg.relative_to(project_root)) for cfg in git_configs if cfg.exists()
        ]

    except Exception as e:
        print(f"Warning: Error getting git info: {e}")

    return info


def test_git_workflow():
    """Verify Git workflow standards."""
    info = get_git_info()

    # Check for essential git configs
    assert ".gitignore" in info.get("configs", []), "Missing .gitignore file"

    # Check for CI configuration
    assert any(
        "github/workflows" in cfg for cfg in info.get("configs", [])
    ), "No GitHub Actions workflows found"

    # Check branch naming
    branch_patterns = {
        "feature": r"feature/[a-z0-9-]+",
        "bugfix": r"bugfix/[a-z0-9-]+",
        "hotfix": r"hotfix/[a-z0-9-]+",
        "release": r"release/v\d+\.\d+\.\d+",
    }

    for branch in info.get("branches", []):
        assert any(
            re.match(pattern, branch) for pattern in branch_patterns.values()
        ), f"Branch {branch} doesn't follow naming convention"

    # Check commit messages
    for commit in info.get("commits", []):
        # Check conventional commits format
        assert re.match(
            r"^(feat|fix|docs|style|refactor|test|chore)(\([a-z]+\))?: .+", commit
        ), f"Commit message doesn't follow conventional commits: {commit}"

    # Check for git hooks
    essential_hooks = {"pre-commit", "pre-push"}
    existing_hooks = set(info.get("hooks", []))
    missing_hooks = essential_hooks - existing_hooks
    assert not missing_hooks, f"Missing git hooks: {missing_hooks}"


def get_test_stats() -> Dict[str, int]:
    """Analyze test statistics."""
    project_root = Path(__file__).parent.parent
    stats = {
        "test_files": 0,
        "test_functions": 0,
        "assertions": 0,
        "parameterized_tests": 0,
        "mock_usage": 0,
        "fixture_usage": 0,
    }

    for py_file in (project_root / "tests").rglob("*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            with open(py_file) as f:
                content = f.read()
                tree = ast.parse(content)

            stats["test_files"] += 1

            # Count test functions and features
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith("test_"):
                        stats["test_functions"] += 1

                        # Count assertions
                        stats["assertions"] += len(
                            [n for n in ast.walk(node) if isinstance(n, ast.Assert)]
                        )

                        # Check for parameterization
                        if any(
                            "parametrize" in ast.unparse(d) for d in node.decorator_list
                        ):
                            stats["parameterized_tests"] += 1

                        # Check for mocking
                        if "mock" in content.lower():
                            stats["mock_usage"] += 1

                        # Check for fixture usage
                        if any(
                            isinstance(d, ast.Name) and d.id == "fixture"
                            for d in node.decorator_list
                        ):
                            stats["fixture_usage"] += 1
        except Exception as e:
            print(f"Warning: Error processing {py_file}: {e}")

    return stats


def test_testing_quality():
    """Verify testing standards and coverage."""
    stats = get_test_stats()

    # Check test file existence
    assert stats["test_files"] > 0, "No test files found"

    # Check test count
    assert stats["test_functions"] > 0, "No test functions found"

    # Check assertion density
    assertion_density = stats["assertions"] / stats["test_functions"]
    assert (
        assertion_density >= 2
    ), f"Low assertion density ({assertion_density:.1f} per test)"

    # Check test features usage
    assert stats["parameterized_tests"] > 0, "No parameterized tests found"
    assert stats["mock_usage"] > 0, "No mocking usage found"
    assert stats["fixture_usage"] > 0, "No fixture usage found"

    # Check pytest.ini configuration
    project_root = Path(__file__).parent.parent
    pytest_configs = [
        project_root / "pytest.ini",
        project_root / "setup.cfg",
        project_root / "pyproject.toml",
    ]

    assert any(cfg.exists() for cfg in pytest_configs), "No pytest configuration found"

    # Check coverage configuration
    coverage_configs = [
        project_root / ".coveragerc",
        project_root / "setup.cfg",
        project_root / "pyproject.toml",
    ]

    assert any(
        cfg.exists() for cfg in coverage_configs
    ), "No coverage configuration found"


def get_performance_metrics() -> Dict[str, List[Dict]]:
    """Analyze code for performance considerations."""
    project_root = Path(__file__).parent.parent
    metrics = {"database_queries": [], "api_endpoints": [], "heavy_operations": []}

    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            with open(py_file) as f:
                content = f.read()
                tree = ast.parse(content)

            # Check for database queries
            if "query" in content.lower() or "select" in content.lower():
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        call_str = ast.unparse(node)
                        if any(
                            term in call_str.lower()
                            for term in ["query", "select", "join"]
                        ):
                            metrics["database_queries"].append(
                                {
                                    "file": str(py_file.relative_to(project_root)),
                                    "line": node.lineno,
                                    "query": call_str,
                                }
                            )

            # Check API endpoint response time annotations
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and any(
                    "route" in ast.unparse(d) for d in node.decorator_list
                ):
                    metrics["api_endpoints"].append(
                        {
                            "file": str(py_file.relative_to(project_root)),
                            "line": node.lineno,
                            "name": node.name,
                            "has_cache": any(
                                "cache" in ast.unparse(d) for d in node.decorator_list
                            ),
                        }
                    )

            # Check for potentially heavy operations
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    # Check for nested loops
                    nested_loops = len(
                        [n for n in ast.walk(node) if isinstance(n, ast.For)]
                    )
                    if nested_loops > 1:
                        metrics["heavy_operations"].append(
                            {
                                "file": str(py_file.relative_to(project_root)),
                                "line": node.lineno,
                                "type": "nested_loops",
                                "depth": nested_loops,
                            }
                        )

                # Check for large data structure operations
                elif isinstance(node, ast.Call):
                    call_str = ast.unparse(node)
                    if any(
                        op in call_str.lower()
                        for op in ["map", "filter", "reduce", "sort"]
                    ):
                        metrics["heavy_operations"].append(
                            {
                                "file": str(py_file.relative_to(project_root)),
                                "line": node.lineno,
                                "type": "data_operation",
                                "operation": call_str,
                            }
                        )

        except Exception as e:
            print(f"Warning: Error processing {py_file}: {e}")

    return metrics


def test_performance_monitoring():
    """Verify performance monitoring and optimization."""
    metrics = get_performance_metrics()

    # Check database query patterns
    for query in metrics["database_queries"]:
        # Check for N+1 query patterns
        assert not any(
            term in query["query"].lower() for term in ["for", "while"]
        ), f"Potential N+1 query in {query['file']}:{query['line']}"

    # Check API endpoint patterns
    for endpoint in metrics["api_endpoints"]:
        # Check for caching on read endpoints
        if endpoint["name"].startswith(("get_", "list_", "search_")):
            assert endpoint[
                "has_cache"
            ], f"Read endpoint without cache in {endpoint['file']}:{endpoint['line']}"

    # Check heavy operations
    for op in metrics["heavy_operations"]:
        if op["type"] == "nested_loops":
            assert (
                op["depth"] <= 2
            ), f"Deep nested loops ({op['depth']}) in {op['file']}:{op['line']}"

    # Check for performance monitoring setup
    project_root = Path(__file__).parent.parent
    monitoring_files = ["prometheus.yml", "grafana.yml", "datadog.yml", "newrelic.ini"]

    assert any(
        (project_root / f).exists() for f in monitoring_files
    ), "No performance monitoring configuration found"


def get_data_handling_patterns() -> Dict[str, List[Dict]]:
    """Analyze code for data handling patterns."""
    project_root = Path(__file__).parent.parent
    patterns = {
        "personal_data": [],
        "data_validation": [],
        "data_encryption": [],
        "data_logging": [],
    }

    sensitive_fields = {
        "password",
        "ssn",
        "credit_card",
        "bank_account",
        "address",
        "phone",
        "email",
        "birth_date",
    }

    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            with open(py_file) as f:
                content = f.read()
                tree = ast.parse(content)

            # Check for personal data handling
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check model definitions
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Assign):
                            for target in subnode.targets:
                                if isinstance(target, ast.Name):
                                    field_name = target.id.lower()
                                    if any(
                                        term in field_name for term in sensitive_fields
                                    ):
                                        patterns["personal_data"].append(
                                            {
                                                "file": str(
                                                    py_file.relative_to(project_root)
                                                ),
                                                "line": subnode.lineno,
                                                "field": field_name,
                                                "class": node.name,
                                            }
                                        )

                # Check for data validation
                elif isinstance(node, ast.FunctionDef):
                    func_str = ast.unparse(node)
                    if any(
                        term in func_str.lower()
                        for term in ["validate", "check", "verify"]
                    ):
                        patterns["data_validation"].append(
                            {
                                "file": str(py_file.relative_to(project_root)),
                                "line": node.lineno,
                                "function": node.name,
                            }
                        )

                # Check for encryption usage
                elif isinstance(node, ast.Call):
                    call_str = ast.unparse(node)
                    if any(
                        term in call_str.lower()
                        for term in ["encrypt", "decrypt", "hash"]
                    ):
                        patterns["data_encryption"].append(
                            {
                                "file": str(py_file.relative_to(project_root)),
                                "line": node.lineno,
                                "call": call_str,
                            }
                        )

            # Check logging patterns
            if "log" in content.lower():
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        call_str = ast.unparse(node)
                        if "log" in call_str.lower():
                            patterns["data_logging"].append(
                                {
                                    "file": str(py_file.relative_to(project_root)),
                                    "line": node.lineno,
                                    "log_call": call_str,
                                }
                            )

        except Exception as e:
            print(f"Warning: Error processing {py_file}: {e}")

    return patterns


def get_industry_standards() -> Dict:
    """Define common industry standards for Python projects."""
    return {
        "project_structure": {
            "required_files": {
                "README.md": "Project documentation",
                "requirements.txt": "Dependencies",
                "setup.py": "Package configuration",
                ".gitignore": "Git ignore patterns",
                "Dockerfile": "Container definition",
                "docker-compose.yml": "Container orchestration",
                "Makefile": "Build automation",
            },
            "required_folders": {
                "docs/": "Documentation",
                "tests/": "Test suite",
                "scripts/": "Utility scripts",
                ".github/": "GitHub configuration",
            },
        },
        "code_organization": {
            "module_patterns": [
                "models/",  # Data models
                "views/",  # View logic
                "services/",  # Business logic
                "utils/",  # Utilities
                "config/",  # Configuration
                "migrations/",  # Database migrations
            ],
            "test_patterns": [
                "unit/",  # Unit tests
                "integration/",  # Integration tests
                "e2e/",  # End-to-end tests
                "fixtures/",  # Test fixtures
                "mocks/",  # Test mocks
            ],
        },
        "documentation": {
            "required_sections": {
                "Installation": "Setup instructions",
                "Usage": "How to use",
                "API": "API documentation",
                "Contributing": "Contribution guidelines",
                "License": "License information",
            },
            "code_documentation": {
                "Module": "Module purpose and contents",
                "Class": "Class responsibility and usage",
                "Method": "Parameters, return values, and behavior",
                "Example": "Usage examples",
            },
        },
        "development_workflow": {
            "branch_strategy": {
                "main": "Production code",
                "develop": "Development code",
                "feature/*": "New features",
                "bugfix/*": "Bug fixes",
                "release/*": "Release preparation",
            },
            "review_process": {
                "PR Template": "Pull request template",
                "Code Review": "Review guidelines",
                "CI Checks": "Automated checks",
            },
        },
        "security": {
            "required_practices": {
                "Input Validation": "Validate all inputs",
                "Output Encoding": "Encode all outputs",
                "Authentication": "User verification",
                "Authorization": "Access control",
                "Data Protection": "Data encryption",
                "Logging": "Security events",
                "Error Handling": "Secure error messages",
            }
        },
        "performance": {
            "monitoring": {
                "Metrics": "Performance metrics",
                "Logging": "Application logs",
                "Tracing": "Request tracing",
                "Alerting": "Performance alerts",
            },
            "optimization": {
                "Caching": "Data caching",
                "Database": "Query optimization",
                "Assets": "Asset optimization",
            },
        },
    }


def test_industry_standards_compliance():
    """Verify compliance with industry standards."""
    project_root = Path(__file__).parent.parent
    standards = get_industry_standards()

    # Track missing and implemented standards
    missing_standards = {
        "project_structure": [],
        "code_organization": [],
        "documentation": [],
        "development_workflow": [],
        "security": [],
        "performance": [],
    }

    implemented_standards = {
        "project_structure": [],
        "code_organization": [],
        "documentation": [],
        "development_workflow": [],
        "security": [],
        "performance": [],
    }

    # Check project structure
    for file, desc in standards["project_structure"]["required_files"].items():
        if (project_root / file).exists():
            implemented_standards["project_structure"].append(f"File: {file}")
        else:
            missing_standards["project_structure"].append(f"File: {file} ({desc})")

    for folder, desc in standards["project_structure"]["required_folders"].items():
        if (project_root / folder).exists():
            implemented_standards["project_structure"].append(f"Folder: {folder}")
        else:
            missing_standards["project_structure"].append(f"Folder: {folder} ({desc})")

    # Check code organization
    for pattern in standards["code_organization"]["module_patterns"]:
        if any(
            d.name == pattern.rstrip("/") for d in project_root.iterdir() if d.is_dir()
        ):
            implemented_standards["code_organization"].append(f"Module: {pattern}")
        else:
            missing_standards["code_organization"].append(f"Module: {pattern}")

    # Check documentation
    readme = project_root / "README.md"
    if readme.exists():
        with open(readme) as f:
            content = f.read().lower()
            for section, desc in standards["documentation"][
                "required_sections"
            ].items():
                if section.lower() in content:
                    implemented_standards["documentation"].append(f"Section: {section}")
                else:
                    missing_standards["documentation"].append(
                        f"Section: {section} ({desc})"
                    )

    # Check development workflow
    github_dir = project_root / ".github"
    if github_dir.exists():
        for item, desc in standards["development_workflow"]["review_process"].items():
            if any(
                item.lower() in f.name.lower()
                for f in github_dir.rglob("*")
                if f.is_file()
            ):
                implemented_standards["development_workflow"].append(f"Process: {item}")
            else:
                missing_standards["development_workflow"].append(
                    f"Process: {item} ({desc})"
                )

    # Check security practices
    security_file = project_root / "docs" / "security.md"
    if security_file.exists():
        with open(security_file) as f:
            content = f.read().lower()
            for practice, desc in standards["security"]["required_practices"].items():
                if practice.lower() in content:
                    implemented_standards["security"].append(f"Practice: {practice}")
                else:
                    missing_standards["security"].append(
                        f"Practice: {practice} ({desc})"
                    )

    # Check performance monitoring
    monitoring_files = ["prometheus.yml", "grafana.yml", "datadog.yml", "newrelic.ini"]

    if any((project_root / f).exists() for f in monitoring_files):
        implemented_standards["performance"].append("Monitoring: Configuration")
    else:
        missing_standards["performance"].append(
            "Monitoring: No monitoring configuration"
        )

    # Generate report
    report = ["Industry Standards Compliance Report:", ""]

    report.append("Implemented Standards:")
    for category, items in implemented_standards.items():
        if items:
            report.append(f"\n{category.replace('_', ' ').title()}:")
            report.extend(f"  ✓ {item}" for item in items)

    report.append("\nMissing Standards:")
    for category, items in missing_standards.items():
        if items:
            report.append(f"\n{category.replace('_', ' ').title()}:")
            report.extend(f"  ✗ {item}" for item in items)

    # Write report to file
    report_file = project_root / "reports" / "industry_standards.md"
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, "w") as f:
        f.write("\n".join(report))

    # Fail if missing critical standards
    critical_categories = ["security", "documentation"]
    critical_missing = [
        f"{category}: {len(items)} missing standards"
        for category, items in missing_standards.items()
        if category in critical_categories and items
    ]

    if critical_missing:
        pytest.fail(
            "Missing critical industry standards:\n"
            + "\n".join(critical_missing)
            + f"\nSee full report at: {report_file}"
        )
