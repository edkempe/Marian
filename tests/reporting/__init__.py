"""Reporting module for test analysis and validation results."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, TextIO

from jinja2 import Environment, FileSystemLoader


class ReportManager:
    """Manages report generation and output."""

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            project_root = Path(__file__).parent.parent.parent
            base_dir = project_root / "reports"

        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

        # Create subdirectories for different report types
        self.schema_dir = self.base_dir / "schema"
        self.docs_dir = self.base_dir / "documentation"
        self.deps_dir = self.base_dir / "dependencies"
        self.reqs_dir = self.base_dir / "requirements"
        self.html_dir = self.base_dir / "html"

        for directory in [
            self.schema_dir,
            self.docs_dir,
            self.deps_dir,
            self.reqs_dir,
            self.html_dir,
        ]:
            directory.mkdir(exist_ok=True)

        # Set up Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

        # Create HTML templates if they don't exist
        self._ensure_templates_exist()

    def _ensure_templates_exist(self):
        """Create HTML templates if they don't exist."""
        template_dir = Path(__file__).parent / "templates"

        # Base template
        base_template = template_dir / "base.html"
        if not base_template.exists():
            base_template.write_text(
                """
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .report { margin-bottom: 30px; }
        .section { margin: 20px 0; }
        .issue { margin: 10px 0; padding: 10px; border-left: 4px solid #ff6b6b; }
        .warning { background: #fff3cd; padding: 10px; border-radius: 4px; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 20px; color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="index.html">Overview</a>
            <a href="schema.html">Schema</a>
            <a href="documentation.html">Documentation</a>
            <a href="dependencies.html">Dependencies</a>
            <a href="requirements.html">Requirements</a>
        </div>
        {% block content %}{% endblock %}
    </div>
</body>
</html>
            """
            )

        # Report-specific templates
        templates = {
            "index.html": """
{% extends "base.html" %}
{% block title %}Test Reports Overview{% endblock %}
{% block content %}
    <h1>Test Reports Overview</h1>
    <div class="report">
        <h2>Latest Reports</h2>
        <ul>
            {% for report_type, data in reports.items() %}
            <li>
                <a href="{{ report_type }}.html">{{ report_type|title }}</a>
                (Generated: {{ data.timestamp }})
            </li>
            {% endfor %}
        </ul>
    </div>
{% endblock %}
            """,
            "schema.html": """
{% extends "base.html" %}
{% block title %}Schema Analysis Report{% endblock %}
{% block content %}
    <h1>Schema Analysis Report</h1>
    <div class="report">
        {% if data.unused_tables %}
        <div class="section">
            <h2>Unused Tables</h2>
            <ul>
                {% for table in data.unused_tables %}
                <li>{{ table }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if data.unused_columns %}
        <div class="section">
            <h2>Unused Columns</h2>
            {% for table, columns in data.unused_columns.items() %}
            <h3>{{ table }}</h3>
            <ul>
                {% for column in columns %}
                <li>{{ column }}</li>
                {% endfor %}
            </ul>
            {% endfor %}
        </div>
        {% endif %}
    </div>
{% endblock %}
            """,
            "documentation.html": """
{% extends "base.html" %}
{% block title %}Documentation Analysis Report{% endblock %}
{% block content %}
    <h1>Documentation Analysis Report</h1>
    <div class="report">
        <div class="section">
            <h2>Statistics</h2>
            <ul>
                <li>{{ data.stats.doc_count }} documentation files</li>
                <li>{{ data.stats.folder_count }} documentation folders</li>
                <li>{{ data.stats.ref_count }} total references</li>
            </ul>
        </div>

        {% if data.broken_refs %}
        <div class="section">
            <h2>Broken References</h2>
            {% for source, refs in data.broken_refs.items() %}
            <h3>In {{ source }}</h3>
            <ul>
                {% for ref in refs|sort %}
                <li>{{ ref }}</li>
                {% endfor %}
            </ul>
            {% endfor %}
        </div>
        {% endif %}

        {% if data.unreferenced %}
        <div class="section">
            <h2>Unreferenced Files</h2>
            <ul>
                {% for doc in data.unreferenced|sort %}
                <li>{{ doc }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
{% endblock %}
            """,
            "dependencies.html": """
{% extends "base.html" %}
{% block title %}Dependency Analysis Report{% endblock %}
{% block content %}
    <h1>Dependency Analysis Report</h1>
    <div class="report">
        <div class="section">
            <h2>Module Statistics</h2>
            <ul>
                {% for type, count in data.module_stats.items() %}
                <li>{{ count }} {{ type }} modules</li>
                {% endfor %}
            </ul>
        </div>

        {% if data.cycles %}
        <div class="section">
            <h2>Circular Dependencies</h2>
            <ul>
                {% for cycle in data.cycles %}
                <li>{{ " -> ".join(cycle + [cycle[0]]) }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if data.violations %}
        <div class="section">
            <h2>Layer Violations</h2>
            <ul>
                {% for source, target in data.violations %}
                <li>{{ source }} imports {{ target }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if data.unused_libs %}
        <div class="section">
            <h2>Unused Shared Library Modules</h2>
            <ul>
                {% for module in data.unused_libs|sort %}
                <li>{{ module }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
{% endblock %}
            """,
            "requirements.html": """
{% extends "base.html" %}
{% block title %}Requirements Analysis Report{% endblock %}
{% block content %}
    <h1>Requirements Analysis Report</h1>
    <div class="report">
        <div class="section">
            <h2>Statistics</h2>
            <ul>
                <li>{{ data.stats.installed_count }} installed packages</li>
                <li>{{ data.stats.required_count }} required packages</li>
                <li>{{ data.stats.imported_count }} imported packages</li>
            </ul>
        </div>

        {% if data.issues.unused_requirements %}
        <div class="section">
            <h2>Unused Requirements</h2>
            <div class="warning">These packages are listed in requirements.txt but not imported in the code:</div>
            <ul>
                {% for pkg in data.issues.unused_requirements|sort %}
                <li>{{ pkg }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if data.issues.missing_requirements %}
        <div class="section">
            <h2>Missing Requirements</h2>
            <div class="warning">These packages are imported in the code but not listed in requirements.txt:</div>
            <ul>
                {% for pkg in data.issues.missing_requirements|sort %}
                <li>{{ pkg }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if data.issues.version_mismatches %}
        <div class="section">
            <h2>Version Mismatches</h2>
            <div class="warning">These packages have version mismatches between requirements.txt and installed versions:</div>
            <ul>
                {% for pkg in data.issues.version_mismatches|sort %}
                <li>{{ pkg }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        <div class="section">
            <h2>Package Details</h2>
            <table>
                <tr>
                    <th>Package</th>
                    <th>Required Version</th>
                    <th>Installed Version</th>
                    <th>Status</th>
                </tr>
                {% for pkg in data.details.installed|sort %}
                <tr>
                    <td>{{ pkg }}</td>
                    <td>{{ data.details.required.get(pkg, 'Not specified') }}</td>
                    <td>{{ data.details.installed[pkg] }}</td>
                    <td>
                        {% if pkg in data.details.imported %}
                        <span class="success">Used</span>
                        {% else %}
                        <span class="error">Unused</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
{% endblock %}
            """,
        }

        for name, content in templates.items():
            template_path = template_dir / name
            if not template_path.exists():
                template_path.write_text(content.strip())

    def _get_report_file(
        self, subdir: Path, prefix: str, suffix: str = "txt"
    ) -> TextIO:
        """Get a file handle for writing a report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{suffix}"
        filepath = subdir / filename
        return open(filepath, "w")

    def _write_html_report(self, template_name: str, data: Dict[str, Any]):
        """Write an HTML report using a template."""
        template = self.jinja_env.get_template(template_name)
        output = template.render(data=data)

        with open(self.html_dir / template_name, "w") as f:
            f.write(output)

    def write_schema_report(self, report_data: Dict[str, Any]):
        """Write schema validation report."""
        # Write text report
        with self._get_report_file(self.schema_dir, "schema_analysis") as f:
            json.dump(report_data, f, indent=2)

        # Write HTML report
        self._write_html_report("schema.html", report_data)

    def write_documentation_report(self, report_data: Dict[str, Any]):
        """Write documentation analysis report."""
        # Write text report
        with self._get_report_file(self.docs_dir, "documentation_analysis") as f:
            json.dump(report_data, f, indent=2)

        # Write HTML report
        self._write_html_report("documentation.html", report_data)

    def write_dependency_report(self, report_data: Dict[str, Any]):
        """Write dependency analysis report."""
        # Write text report
        with self._get_report_file(self.deps_dir, "dependency_analysis") as f:
            json.dump(report_data, f, indent=2)

        # Write HTML report
        self._write_html_report("dependencies.html", report_data)

    def write_requirements_report(self, report_data: Dict[str, Any]):
        """Write requirements analysis report."""
        # Write text report
        with self._get_report_file(self.reqs_dir, "requirements_analysis") as f:
            json.dump(report_data, f, indent=2)

        # Write HTML report
        self._write_html_report("requirements.html", report_data)

    def generate_index(self):
        """Generate index page linking to all reports."""
        latest_reports = {}

        for report_type, directory in [
            ("schema", self.schema_dir),
            ("documentation", self.docs_dir),
            ("dependencies", self.deps_dir),
            ("requirements", self.reqs_dir),
        ]:
            reports = sorted(directory.glob("*_analysis_*.txt"))
            if reports:
                latest = reports[-1]
                timestamp = datetime.strptime(
                    latest.stem.split("_")[-2] + latest.stem.split("_")[-1],
                    "%Y%m%d%H%M%S",
                )
                latest_reports[report_type] = {
                    "path": latest,
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }

        self._write_html_report("index.html", {"reports": latest_reports})

    def get_latest_reports(self) -> Dict[str, Path]:
        """Get paths to the most recent reports of each type."""
        latest_reports = {}

        for report_type, directory in [
            ("schema", self.schema_dir),
            ("documentation", self.docs_dir),
            ("dependencies", self.deps_dir),
            ("requirements", self.reqs_dir),
        ]:
            reports = sorted(directory.glob("*_analysis_*.txt"))
            if reports:
                latest_reports[report_type] = reports[-1]

        return latest_reports
