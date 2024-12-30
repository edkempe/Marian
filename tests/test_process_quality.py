"""Test suite for process and documentation quality.

This module ensures that our development processes and documentation
maintain high quality standards across the project.
"""

import ast
import importlib.util
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pytest
import yaml


@dataclass
class APIEndpoint:
    """Represents an API endpoint definition."""

    path: str
    method: str
    description: Optional[str]
    parameters: List[Dict]
    responses: Dict[str, Dict]
    examples: List[Dict]


def get_openapi_spec() -> Dict:
    """Load OpenAPI specification."""
    project_root = Path(__file__).parent.parent
    api_spec_path = project_root / "api" / "openapi.yaml"

    if not api_spec_path.exists():
        return {}

    with open(api_spec_path) as f:
        return yaml.safe_load(f)


def get_implemented_endpoints() -> List[APIEndpoint]:
    """Extract implemented API endpoints from code."""
    project_root = Path(__file__).parent.parent
    endpoints = []

    # Search through route definitions
    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Look for route decorators
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and any(
                            name in ast.unparse(decorator.func)
                            for name in ["route", "get", "post", "put", "delete"]
                        ):

                            # Extract endpoint info from decorator and function
                            path = None
                            method = None
                            if decorator.args:
                                path = ast.literal_eval(decorator.args[0])
                            if "method" in ast.unparse(decorator).lower():
                                method = re.search(
                                    r'method=[\'"](\w+)[\'"]', ast.unparse(decorator)
                                ).group(1)

                            if path:
                                endpoints.append(
                                    APIEndpoint(
                                        path=path,
                                        method=method or "GET",
                                        description=ast.get_docstring(node),
                                        parameters=[],  # Would need more parsing
                                        responses={},  # Would need more parsing
                                        examples=[],  # Would need more parsing
                                    )
                                )
        except Exception as e:
            print(f"Warning: Error processing {py_file}: {e}")

    return endpoints


def test_api_documentation():
    """Verify API documentation completeness and accuracy."""
    spec = get_openapi_spec()
    implemented = get_implemented_endpoints()

    # Check all implemented endpoints are documented
    documented_paths = {
        f"{path}:{method.lower()}"
        for path, methods in spec.get("paths", {}).items()
        for method in methods.keys()
    }

    implemented_paths = {
        f"{endpoint.path}:{endpoint.method.lower()}" for endpoint in implemented
    }

    undocumented = implemented_paths - documented_paths
    assert not undocumented, f"Undocumented endpoints found: {undocumented}"

    # Check documentation quality
    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            # Verify description exists
            assert details.get(
                "description"
            ), f"Missing description for {method.upper()} {path}"

            # Check for examples
            assert details.get("examples") or details.get("requestBody", {}).get(
                "examples"
            ), f"Missing examples for {method.upper()} {path}"

            # Verify error responses
            responses = details.get("responses", {})
            assert (
                "400" in responses or "404" in responses or "500" in responses
            ), f"Missing error responses for {method.upper()} {path}"


def get_config_variables() -> Dict[str, Set[str]]:
    """Get configuration variables from code and documentation."""
    project_root = Path(__file__).parent.parent

    # Variables found in code
    code_vars = set()
    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            with open(py_file) as f:
                content = f.read()

            # Look for common config patterns
            code_vars.update(re.findall(r'config\[[\'"]([\w_]+)[\'"]\]', content))
            code_vars.update(re.findall(r'os\.environ\[[\'"]([\w_]+)[\'"]\]', content))
            code_vars.update(re.findall(r'os\.getenv\([\'"]([\w_]+)[\'"]\)', content))
        except Exception as e:
            print(f"Warning: Error processing {py_file}: {e}")

    # Variables documented in config files
    doc_vars = set()
    config_files = [
        project_root / ".env.example",
        project_root / "config" / "default.yaml",
        project_root / "docs" / "configuration.md",
    ]

    for config_file in config_files:
        if config_file.exists():
            try:
                with open(config_file) as f:
                    content = f.read()
                doc_vars.update(re.findall(r"^([\w_]+)[=:]", content, re.M))
            except Exception as e:
                print(f"Warning: Error processing {config_file}: {e}")

    return {"code": code_vars, "documented": doc_vars}


def test_configuration():
    """Validate configuration management."""
    variables = get_config_variables()

    # All used config variables should be documented
    undocumented = variables["code"] - variables["documented"]
    assert not undocumented, f"Undocumented config variables found: {undocumented}"

    # Check for example .env file
    project_root = Path(__file__).parent.parent
    assert (project_root / ".env.example").exists(), "Missing .env.example file"

    # Verify config documentation exists
    config_doc = project_root / "docs" / "configuration.md"
    assert config_doc.exists(), "Missing configuration documentation"

    if config_doc.exists():
        with open(config_doc) as f:
            content = f.read().lower()
            # Check for important config documentation sections
            assert (
                "default values" in content
            ), "Configuration docs missing default values section"
            assert (
                "environment variables" in content
            ), "Configuration docs missing environment variables section"
            assert (
                "override" in content
            ), "Configuration docs missing override information"


def get_log_statements() -> List[Dict]:
    """Extract logging statements from code."""
    project_root = Path(__file__).parent.parent
    log_statements = []

    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr
                    in ["debug", "info", "warning", "error", "critical"]
                ):

                    log_statements.append(
                        {
                            "file": str(py_file.relative_to(project_root)),
                            "level": node.func.attr,
                            "message": ast.unparse(node.args[0]) if node.args else None,
                            "line": node.lineno,
                        }
                    )
        except Exception as e:
            print(f"Warning: Error processing {py_file}: {e}")

    return log_statements


def test_logging_standards():
    """Verify logging practices."""
    log_statements = get_log_statements()

    # Check for consistent log levels
    for log in log_statements:
        assert log["level"] in [
            "debug",
            "info",
            "warning",
            "error",
            "critical",
        ], f"Invalid log level in {log['file']}:{log['line']}"

    # Check for structured logging
    for log in log_statements:
        if log["message"]:
            # Look for string concatenation (bad practice)
            assert (
                " + " not in log["message"]
            ), f"String concatenation in log message: {log['file']}:{log['line']}"

            # Check for f-strings or % formatting
            assert any(
                marker in log["message"] for marker in ["{", "%s", "%d"]
            ), f"Non-structured log message: {log['file']}:{log['line']}"

    # Check log configuration
    project_root = Path(__file__).parent.parent
    log_configs = list(project_root.rglob("logging.yaml")) + list(
        project_root.rglob("logging.conf")
    )

    assert log_configs, "No logging configuration found"

    if log_configs:
        with open(log_configs[0]) as f:
            config = yaml.safe_load(f)

        # Verify log rotation
        handlers = config.get("handlers", {})
        assert any(
            "rotating" in str(h).lower() for h in handlers.values()
        ), "No log rotation configured"


def get_security_issues() -> List[Dict]:
    """Scan for potential security issues."""
    project_root = Path(__file__).parent.parent
    issues = []

    # Patterns to check
    patterns = {
        "hardcoded_secret": r'(?:password|secret|key|token).*?[\'"][A-Za-z0-9+/=]{8,}[\'"]',
        "basic_auth": r"Authorization:\s*Basic\s+[A-Za-z0-9+/=]+",
        "unsafe_redirect": r"redirect\([^)]*request\.",
        "sql_injection": r"execute\([^)]*%|execute\([^)]*format",
        "xss_vulnerable": r"render_template\([^)]*request\.",
    }

    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            with open(py_file) as f:
                content = f.read()

            for issue_type, pattern in patterns.items():
                matches = re.finditer(pattern, content, re.I)
                for match in matches:
                    issues.append(
                        {
                            "type": issue_type,
                            "file": str(py_file.relative_to(project_root)),
                            "line": content.count("\n", 0, match.start()) + 1,
                        }
                    )
        except Exception as e:
            print(f"Warning: Error processing {py_file}: {e}")

    return issues


def test_security_compliance():
    """Validate security practices."""
    issues = get_security_issues()

    # Report all security issues
    if issues:
        report = ["Security issues found:"]
        for issue in issues:
            report.append(f"  - {issue['type']} in {issue['file']}:{issue['line']}")
        pytest.fail("\n".join(report))

    # Check for security documentation
    project_root = Path(__file__).parent.parent
    security_docs = list(project_root.rglob("security.md"))
    assert security_docs, "Missing security documentation"

    if security_docs:
        with open(security_docs[0]) as f:
            content = f.read().lower()
            # Check for important security sections
            assert (
                "authentication" in content
            ), "Security docs missing authentication section"
            assert (
                "authorization" in content
            ), "Security docs missing authorization section"
            assert "api keys" in content, "Security docs missing API key section"


def get_error_handlers() -> Dict[str, List[Dict]]:
    """Extract error handling patterns from code."""
    project_root = Path(__file__).parent.parent
    handlers = {"try_except": [], "error_routes": [], "custom_exceptions": []}

    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                # Find try-except blocks
                if isinstance(node, ast.Try):
                    handlers["try_except"].append(
                        {
                            "file": str(py_file.relative_to(project_root)),
                            "line": node.lineno,
                            "exceptions": [
                                ast.unparse(handler.type)
                                for handler in node.handlers
                                if handler.type
                            ],
                        }
                    )

                # Find error handler routes
                if isinstance(node, ast.FunctionDef) and any(
                    "errorhandler" in ast.unparse(d) for d in node.decorator_list
                ):
                    handlers["error_routes"].append(
                        {
                            "file": str(py_file.relative_to(project_root)),
                            "line": node.lineno,
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                        }
                    )

                # Find custom exception classes
                if isinstance(node, ast.ClassDef) and any(
                    "Exception" in base.id
                    for base in node.bases
                    if isinstance(base, ast.Name)
                ):
                    handlers["custom_exceptions"].append(
                        {
                            "file": str(py_file.relative_to(project_root)),
                            "line": node.lineno,
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                        }
                    )
        except Exception as e:
            print(f"Warning: Error processing {py_file}: {e}")

    return handlers


def test_error_handling():
    """Verify error handling practices."""
    handlers = get_error_handlers()

    # Check for bare except clauses
    for handler in handlers["try_except"]:
        assert handler[
            "exceptions"
        ], f"Bare except clause found in {handler['file']}:{handler['line']}"

    # Verify error handlers have documentation
    for handler in handlers["error_routes"]:
        assert handler[
            "docstring"
        ], f"Undocumented error handler {handler['name']} in {handler['file']}:{handler['line']}"

    # Check custom exceptions
    for exc in handlers["custom_exceptions"]:
        assert exc[
            "docstring"
        ], f"Undocumented exception class {exc['name']} in {exc['file']}:{exc['line']}"

    # Check error documentation
    project_root = Path(__file__).parent.parent
    error_docs = list(project_root.rglob("errors.md"))
    assert error_docs, "Missing error documentation"

    if error_docs:
        with open(error_docs[0]) as f:
            content = f.read().lower()
            # Check for important error doc sections
            assert "error codes" in content, "Error docs missing error codes section"
            assert "handling" in content, "Error docs missing error handling section"
            assert "logging" in content, "Error docs missing error logging section"


def test_process_documentation():
    """Verify development process documentation."""
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"

    required_docs = {
        "development.md": ["setup", "workflow", "guidelines"],
        "deployment.md": ["environment", "configuration", "procedure"],
        "testing.md": ["setup", "running tests", "writing tests"],
        "architecture.md": ["overview", "components", "data flow"],
    }

    for doc_file, required_sections in required_docs.items():
        doc_path = docs_dir / doc_file
        assert doc_path.exists(), f"Missing {doc_file}"

        if doc_path.exists():
            with open(doc_path) as f:
                content = f.read().lower()
                for section in required_sections:
                    assert (
                        section.lower() in content
                    ), f"Missing {section} section in {doc_file}"


def test_code_style():
    """Verify code style and maintainability standards."""
    project_root = Path(__file__).parent.parent

    # Check for style configuration files
    style_files = {
        "pyproject.toml": ["black", "isort", "flake8"],
        ".pylintrc": ["pylint"],
        ".flake8": ["flake8"],
        "setup.cfg": ["flake8", "pycodestyle"],
    }

    found_configs = []
    for file, tools in style_files.items():
        if (project_root / file).exists():
            found_configs.extend(tools)

    assert found_configs, "No code style configuration found"

    # Check function and file complexity
    complexity_issues = []
    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())

            # Check file length
            num_lines = sum(1 for _ in open(py_file))
            if num_lines > 500:  # Configurable threshold
                complexity_issues.append(
                    f"{py_file.relative_to(project_root)}: File too long ({num_lines} lines)"
                )

            # Check function complexity
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Count branches (if/for/while/try)
                    branches = len(
                        [
                            n
                            for n in ast.walk(node)
                            if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))
                        ]
                    )
                    if branches > 10:  # Configurable threshold
                        complexity_issues.append(
                            f"{py_file.relative_to(project_root)}:{node.lineno}: "
                            f"Function {node.name} too complex ({branches} branches)"
                        )

                    # Check function length
                    func_lines = len(
                        [n for n in ast.walk(node) if isinstance(n, ast.Expr)]
                    )
                    if func_lines > 50:  # Configurable threshold
                        complexity_issues.append(
                            f"{py_file.relative_to(project_root)}:{node.lineno}: "
                            f"Function {node.name} too long ({func_lines} lines)"
                        )
        except Exception as e:
            print(f"Warning: Error processing {py_file}: {e}")

    assert not complexity_issues, "\n".join(complexity_issues)


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


def get_git_info() -> Dict[str, Any]:
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


def test_data_privacy():
    """Verify data privacy and compliance standards."""
    patterns = get_data_handling_patterns()

    # Check personal data handling
    for field in patterns["personal_data"]:
        # Verify encryption for sensitive fields
        related_encryption = any(
            enc["file"] == field["file"] and field["field"] in enc["call"].lower()
            for enc in patterns["data_encryption"]
        )
        assert (
            related_encryption
        ), f"Unencrypted sensitive field {field['field']} in {field['file']}:{field['line']}"

    # Check data validation
    model_files = set(f["file"] for f in patterns["personal_data"])
    for model_file in model_files:
        # Verify validation exists for models with sensitive data
        has_validation = any(
            v["file"] == model_file for v in patterns["data_validation"]
        )
        assert has_validation, f"Missing data validation in {model_file}"

    # Check logging practices
    for log in patterns["data_logging"]:
        # Verify no sensitive data in logs
        log_str = log["log_call"].lower()
        assert not any(
            field["field"] in log_str for field in patterns["personal_data"]
        ), f"Sensitive data in log at {log['file']}:{log['line']}"

    # Check for privacy documentation
    project_root = Path(__file__).parent.parent
    privacy_docs = list(project_root.rglob("privacy.md"))
    assert privacy_docs, "Missing privacy documentation"

    if privacy_docs:
        with open(privacy_docs[0]) as f:
            content = f.read().lower()
            # Check for important privacy sections
            assert (
                "data collection" in content
            ), "Privacy docs missing data collection section"
            assert (
                "data protection" in content
            ), "Privacy docs missing data protection section"
            assert "user rights" in content, "Privacy docs missing user rights section"


def get_naming_patterns() -> Dict[str, List[Dict]]:
    """Analyze naming patterns in the codebase."""
    project_root = Path(__file__).parent.parent
    patterns = {
        "files": [],
        "folders": [],
        "modules": [],
        "classes": [],
        "functions": [],
    }

    # Common naming conventions
    conventions = {
        "files": r"^[a-z][a-z0-9_]*\.py$",  # snake_case.py
        "folders": r"^[a-z][a-z0-9_]*$",  # snake_case
        "modules": r"^[a-z][a-z0-9_]*$",  # snake_case
        "classes": r"^[A-Z][a-zA-Z0-9]*$",  # PascalCase
        "functions": r"^[a-z][a-z0-9_]*$",  # snake_case
    }

    # Scan files and folders
    for path in project_root.rglob("*"):
        if path.name.startswith(".") or path.name.startswith("__"):
            continue

        rel_path = path.relative_to(project_root)

        if path.is_file() and path.suffix == ".py":
            patterns["files"].append(
                {
                    "name": path.name,
                    "path": str(rel_path),
                    "matches_convention": bool(
                        re.match(conventions["files"], path.name)
                    ),
                }
            )

            try:
                with open(path) as f:
                    tree = ast.parse(f.read())

                # Check module-level names
                module_name = path.stem
                patterns["modules"].append(
                    {
                        "name": module_name,
                        "path": str(rel_path),
                        "matches_convention": bool(
                            re.match(conventions["modules"], module_name)
                        ),
                    }
                )

                # Check class and function names
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        patterns["classes"].append(
                            {
                                "name": node.name,
                                "path": f"{rel_path}:{node.lineno}",
                                "matches_convention": bool(
                                    re.match(conventions["classes"], node.name)
                                ),
                            }
                        )
                    elif isinstance(node, ast.FunctionDef):
                        patterns["functions"].append(
                            {
                                "name": node.name,
                                "path": f"{rel_path}:{node.lineno}",
                                "matches_convention": bool(
                                    re.match(conventions["functions"], node.name)
                                ),
                            }
                        )
            except Exception as e:
                print(f"Warning: Error processing {path}: {e}")

        elif path.is_dir():
            patterns["folders"].append(
                {
                    "name": path.name,
                    "path": str(rel_path),
                    "matches_convention": bool(
                        re.match(conventions["folders"], path.name)
                    ),
                }
            )

    return patterns


def get_industry_standards() -> Dict[str, Dict]:
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


def test_naming_standards():
    """Verify file and folder naming standards."""
    patterns = get_naming_patterns()

    # Check documented standards
    project_root = Path(__file__).parent.parent
    standards_doc = project_root / "docs" / "standards.md"

    if not standards_doc.exists():
        pytest.fail("Missing standards documentation (docs/standards.md)")

    with open(standards_doc) as f:
        standards_content = f.read().lower()

    # Verify naming violations
    violations = []

    for category, items in patterns.items():
        non_compliant = [
            f"{item['name']} ({item['path']})"
            for item in items
            if not item["matches_convention"]
        ]
        if non_compliant:
            violations.append(f"{category.title()} not following convention:")
            violations.extend(f"  - {item}" for item in non_compliant)

    if violations:
        pytest.fail("\n".join(violations))

    # Verify standards documentation
    naming_sections = {
        "files": "file naming",
        "folders": "folder naming",
        "modules": "module naming",
        "classes": "class naming",
        "functions": "function naming",
    }

    missing_docs = [
        section
        for name, section in naming_sections.items()
        if section not in standards_content
    ]

    if missing_docs:
        pytest.fail(
            f"Standards documentation missing sections: {', '.join(missing_docs)}"
        )


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
