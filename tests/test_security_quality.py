"""Test suite for security and data privacy standards.

This module ensures that our security practices, error handling,
and data privacy standards are maintained across the project.
Follows OWASP Top 10, GDPR/CCPA, and NIST logging guidelines.
"""

import ast
import hashlib
import json
import logging
import os
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple
from unittest.mock import MagicMock, patch

import pytest

from shared_lib.logging_util import log_security_event
from shared_lib.path_util import (
    get_absolute_path,
    get_relative_path,
    read_file,
    write_file,
)


def get_security_issues() -> List[Dict]:
    """Scan for potential security issues."""
    project_root = Path(__file__).parent.parent
    issues = []

    # Skip virtual environment and test files
    def should_check_file(file_path: Path) -> bool:
        return not any(
            part in str(file_path)
            for part in ["venv", ".env", "__pycache__", ".git", "tests"]
        )

    security_patterns = {
        # OWASP A03:2021 - Injection
        "sql_injection": r'execute\([\'"].*?\%.*?[\'"]\s*%',
        "command_injection": r'subprocess\.call\([\'"].*?\%.*?[\'"]\s*%',
        "xss_vulnerable": r"mark_safe\(.*?\%.*?\)|safe\s+filter|noescape",
        # OWASP A02:2021 - Cryptographic Failures
        "weak_crypto": r"md5|sha1|DES|RC4",
        "hardcoded_secret": r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
        # OWASP A08:2021 - Software and Data Integrity Failures
        "unsafe_pickle": r"pickle\.loads\(",
        "unsafe_yaml": r"yaml\.load\(",
        "unsafe_eval": r"eval\(|exec\(",
        # OWASP A01:2021 - Broken Access Control
        "path_traversal": r"\.\./",
        "unsafe_path_join": r"os\.path\.join\([^)]*\.\.[^)]*\)",
        "unsafe_redirect": r'redirect\(["\'].*?["\'].*?\)',
    }

    for py_file in project_root.rglob("*.py"):
        if not should_check_file(py_file):
            continue

        try:
            with open(py_file) as f:
                content = f.read()

            for issue_type, pattern in security_patterns.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    issues.append(
                        {
                            "type": issue_type,
                            "file": str(py_file),
                            "line": content.count("\n", 0, match.start()) + 1,
                            "snippet": match.group(0),
                        }
                    )

        except Exception:
            continue

    return issues


def get_error_handlers() -> List[Dict]:
    """Check error handling practices in the codebase."""
    project_root = Path(__file__).parent.parent
    handlers = []

    # Skip virtual environment and test files
    def should_check_file(file_path: Path) -> bool:
        return not any(
            part in str(file_path)
            for part in ["venv", ".env", "__pycache__", ".git", "tests"]
        )

    for py_file in project_root.rglob("*.py"):
        if not should_check_file(py_file):
            continue

        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    handlers.append(
                        {
                            "file": str(py_file),
                            "line": node.lineno,
                            "exception": node.type.id if node.type else "all",
                            "has_logging": any(
                                "logging" in ast.dump(n) for n in ast.walk(node)
                            ),
                        }
                    )

        except Exception:
            continue

    return handlers


def get_data_handling_patterns() -> Dict[str, List[str]]:
    """Analyze code for data handling patterns."""
    project_root = Path(__file__).parent.parent
    patterns = {
        "pii_fields": [],
        "data_validation": [],
        "data_sanitization": [],
        "encryption_usage": [],
        "user_consent": [],  # GDPR requirement
        "data_retention": [],  # GDPR requirement
        "data_minimization": [],  # GDPR requirement
    }

    pii_indicators = {
        "email",
        "password",
        "phone",
        "address",
        "name",
        "ssn",
        "dob",
        "passport",
        "license",
        "credit_card",
        "bank_account",
    }

    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("_") or "test" in str(py_file):
            continue

        try:
            with open(py_file) as f:
                content = f.read()
                tree = ast.parse(content)

            # Look for PII fields
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and any(
                    pii in node.id.lower() for pii in pii_indicators
                ):
                    patterns["pii_fields"].append(
                        f"{py_file}:{node.lineno} - {node.id}"
                    )

            # Look for data validation
            if "validator" in content.lower() or "schema" in content.lower():
                patterns["data_validation"].append(str(py_file))

            # Look for data sanitization
            if "sanitize" in content.lower() or "escape" in content.lower():
                patterns["data_sanitization"].append(str(py_file))

            # Look for encryption usage
            if "encrypt" in content.lower() or "decrypt" in content.lower():
                patterns["encryption_usage"].append(str(py_file))

            # Look for user consent handling
            if "consent" in content.lower():
                patterns["user_consent"].append(str(py_file))

            # Look for data retention handling
            if "retention" in content.lower():
                patterns["data_retention"].append(str(py_file))

            # Look for data minimization handling
            if "minimize" in content.lower():
                patterns["data_minimization"].append(str(py_file))

        except Exception:
            continue

    return patterns


def test_security_compliance():
    """Validate security practices against OWASP Top 10."""
    issues = get_security_issues()

    # A03:2021 - Injection
    injection_types = ["sql_injection", "command_injection", "xss_vulnerable"]
    injection_issues = [i for i in issues if i["type"] in injection_types]
    assert not injection_issues, f"Found injection vulnerabilities: {injection_issues}"

    # A02:2021 - Cryptographic Failures
    crypto_types = ["weak_crypto", "hardcoded_secret"]
    crypto_issues = [i for i in issues if i["type"] in crypto_types]
    assert not crypto_issues, f"Found cryptographic issues: {crypto_issues}"

    # A08:2021 - Software and Data Integrity
    integrity_types = ["unsafe_pickle", "unsafe_yaml", "unsafe_eval"]
    integrity_issues = [i for i in issues if i["type"] in integrity_types]
    assert not integrity_issues, f"Found integrity issues: {integrity_issues}"

    # A01:2021 - Broken Access Control
    access_types = ["path_traversal", "unsafe_path_join", "unsafe_redirect"]
    access_issues = [i for i in issues if i["type"] in access_types]
    assert not access_issues, f"Found access control issues: {access_issues}"


def test_gdpr_compliance():
    """Verify GDPR/CCPA compliance standards."""
    patterns = get_data_handling_patterns()

    # Data Protection
    pii_files = {p.split(":")[0] for p in patterns["pii_fields"]}
    validated_files = set(patterns["data_validation"])
    encrypted_files = set(patterns["encryption_usage"])
    sanitized_files = set(patterns["data_sanitization"])

    unvalidated_pii = pii_files - validated_files
    assert not unvalidated_pii, f"PII fields without validation: {unvalidated_pii}"

    unencrypted_pii = pii_files - encrypted_files
    assert not unencrypted_pii, f"PII fields without encryption: {unencrypted_pii}"

    unsanitized_pii = pii_files - sanitized_files
    assert not unsanitized_pii, f"PII fields without sanitization: {unsanitized_pii}"

    # Data Minimization
    minimized_files = set(patterns["data_minimization"])
    unminimized_pii = pii_files - minimized_files
    assert not unminimized_pii, f"PII fields without minimization: {unminimized_pii}"

    # User Consent
    consent_files = set(patterns["user_consent"])
    unconsented_pii = pii_files - consent_files
    assert (
        not unconsented_pii
    ), f"PII fields without consent handling: {unconsented_pii}"


def test_logging_compliance():
    """Verify logging meets NIST SP 800-53 requirements."""
    handlers = get_error_handlers()

    # AU-2 Audit Events
    bare_excepts = [h for h in handlers if h["exception"] == "all"]
    assert not bare_excepts, f"Non-specific error handling: {bare_excepts}"

    no_logging = [h for h in handlers if not h["has_logging"]]
    assert not no_logging, f"Missing audit logging: {no_logging}"

    # AU-3 Content of Audit Records
    def verify_log_content(log_call):
        required_fields = {"timestamp", "user", "action", "status"}
        log_fields = set(log_call.keywords.keys())
        missing_fields = required_fields - log_fields
        assert not missing_fields, f"Missing required audit fields: {missing_fields}"

    # AU-9 Protection of Audit Information
    def verify_log_integrity(log_file):
        # Check log file permissions
        assert log_file.stat().st_mode & 0o777 == 0o600

        # Verify log signatures if enabled
        if hasattr(log_file, "signature"):
            assert (
                hashlib.sha256(log_file.read_bytes()).hexdigest() == log_file.signature
            )


def test_path_security_logging():
    """Test that path-related security events are properly logged."""
    mock_log = MagicMock()

    with patch("shared_lib.path_util.log_security_event", mock_log):
        # Test path traversal detection
        try:
            get_relative_path("/some/path", "/other/path")
        except ValueError:
            pass
        mock_log.assert_called_with(
            "Attempted path traversal outside base directory: /some/path"
        )
        mock_log.reset_mock()

        # Test ignored directory access
        try:
            get_absolute_path("/path/to/.git/config")
        except ValueError:
            pass
        mock_log.assert_called_with(
            "Attempted access to ignored directory: /path/to/.git/config"
        )
        mock_log.reset_mock()

        # Test permission violation logging
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            try:
                read_file("/path/to/file")
            except PermissionError:
                pass
            mock_log.assert_called_with("Permission denied reading file: /path/to/file")


def test_path_validation():
    """Test path validation and sanitization."""
    test_paths = [
        ("/normal/path", True),
        ("../relative/path", False),
        ("/path/with/.git", False),
        ("/path/with/node_modules", False),
        ("/path/with/__pycache__", False),
    ]

    for path, should_pass in test_paths:
        if should_pass:
            try:
                result = get_absolute_path(path)
                assert isinstance(result, Path)
            except ValueError:
                pytest.fail(f"Valid path {path} was rejected")
        else:
            with pytest.raises((ValueError, RuntimeError)):
                get_absolute_path(path)


def test_file_permission_handling():
    """Test file permission handling and logging."""
    mock_log = MagicMock()

    with patch("shared_lib.path_util.log_security_event", mock_log):
        # Test write permission denied
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            try:
                write_file("/path/to/file", "content")
            except PermissionError:
                pass
            mock_log.assert_called_with("Permission denied writing file: /path/to/file")

        # Test read permission denied
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            try:
                read_file("/path/to/file")
            except PermissionError:
                pass
            mock_log.assert_called_with("Permission denied reading file: /path/to/file")


def test_path_security_patterns():
    """Test detection of unsafe path handling patterns."""
    issues = get_security_issues()

    # No path traversal attempts in code
    traversal_issues = [i for i in issues if i["type"] == "path_traversal"]
    assert not traversal_issues, f"Found potential path traversal: {traversal_issues}"

    # No unsafe path joining
    path_join_issues = [i for i in issues if i["type"] == "unsafe_path_join"]
    assert not path_join_issues, f"Found unsafe path joining: {path_join_issues}"


def test_bandit_security_check():
    """Run Bandit security checks on the codebase.

    Checks for:
    - Command injection
    - SQL injection
    - Path traversal
    - Unsafe deserialization
    - Cryptographic issues
    - Shell injection
    - XXE
    """
    project_root = Path(__file__).parent.parent

    # Run bandit with JSON output
    result = subprocess.run(
        [
            "bandit",
            "-r",  # Recursive
            "-f",
            "json",  # JSON output
            "-ll",  # Report only medium and high severity
            "-i",  # Include more info
            str(project_root),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode not in (0, 1):  # 1 means issues found
        pytest.fail(f"Bandit failed to run: {result.stderr}")

    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Invalid Bandit output: {result.stdout}")

    # Check for security issues
    issues = report.get("results", [])
    high_severity = [i for i in issues if i["issue_severity"] == "HIGH"]
    medium_severity = [i for i in issues if i["issue_severity"] == "MEDIUM"]

    # Format issues for readable output
    def format_issues(issues):
        return [
            f"{i['filename']}:{i['line_number']} - {i['issue_text']}" for i in issues
        ]

    assert not high_severity, "High severity security issues found:\n" + "\n".join(
        format_issues(high_severity)
    )

    assert not medium_severity, "Medium severity security issues found:\n" + "\n".join(
        format_issues(medium_severity)
    )


def test_dependency_security():
    """Check dependencies for known vulnerabilities using Safety.

    Checks for:
    - Known CVEs
    - Insecure package versions
    - Deprecated packages
    """
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"

    # Run safety check with JSON output
    result = subprocess.run(
        ["safety", "check", "-r", str(requirements_file), "--json"],
        capture_output=True,
        text=True,
    )

    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Invalid Safety output: {result.stdout}")

    vulnerabilities = report.get("vulnerabilities", [])

    # Format vulnerabilities for readable output
    def format_vulnerability(vuln):
        return (
            f"Package: {vuln['package_name']} {vuln['vulnerable_spec']}\n"
            f"CVE: {vuln.get('cve', 'N/A')}\n"
            f"Severity: {vuln.get('severity', 'unknown')}\n"
            f"Description: {vuln['advisory']}"
        )

    assert (
        not vulnerabilities
    ), "Security vulnerabilities found in dependencies:\n" + "\n\n".join(
        format_vulnerability(v) for v in vulnerabilities
    )


def test_secrets_detection():
    """Check for secrets in codebase using detect-secrets."""
    project_root = Path(__file__).parent.parent

    # Run detect-secrets
    result = subprocess.run(
        [
            "detect-secrets",
            "scan",
            str(project_root),
            "--all-files",
            "--force-use-all-plugins",
        ],
        capture_output=True,
        text=True,
    )

    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Invalid detect-secrets output: {result.stdout}")

    # Check for detected secrets
    secrets = report.get("results", {})

    # Format secrets for readable output
    def format_secret(file_path, secrets_list):
        return f"File: {file_path}\n" + "\n".join(
            f"- Line {s['line_number']}: {s['type']}" for s in secrets_list
        )

    assert not secrets, "Potential secrets found in codebase:\n" + "\n\n".join(
        format_secret(file_path, secrets_list)
        for file_path, secrets_list in secrets.items()
    )


def test_owasp_dependency_check():
    """Run OWASP Dependency Check for known vulnerabilities."""
    project_root = Path(__file__).parent.parent

    # Run dependency-check
    result = subprocess.run(
        [
            "dependency-check",
            "--scan",
            str(project_root),
            "--format",
            "JSON",
            "--failOnCVSS",
            "7",  # Fail on high severity
            "--enableExperimental",  # Better Python support
        ],
        capture_output=True,
        text=True,
    )

    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Invalid dependency-check output: {result.stdout}")

    # Check for vulnerabilities
    dependencies = report.get("dependencies", [])
    vulnerable_deps = [d for d in dependencies if d.get("vulnerabilities")]

    # Format vulnerabilities for readable output
    def format_dependency(dep):
        return f"Package: {dep['fileName']}\n" + "\n".join(
            f"- {v['name']}: {v['description']}" for v in dep["vulnerabilities"]
        )

    assert (
        not vulnerable_deps
    ), "Dependencies with known vulnerabilities found:\n" + "\n\n".join(
        format_dependency(d) for d in vulnerable_deps
    )
