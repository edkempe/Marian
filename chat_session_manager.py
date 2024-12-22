#!/usr/bin/env python3
"""
Session management utilities for Marian development.
Handles updating NEXT_SESSION.md and generating session summaries.
"""

import subprocess
import sys
from datetime import datetime
import pytz
from pathlib import Path
import json
from typing import List, Dict, Optional
import re

def run_command(cmd: List[str]) -> str:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}: {e}")
        return ""

def get_recent_changes(num_commits: int = 5) -> Dict[str, List[str]]:
    """Get recent git changes."""
    changes = {
        'commits': [],
        'files': [],
        'stats': ''
    }
    
    # Get recent commits
    commits = run_command(['git', 'log', f'-n{num_commits}', '--pretty=format:%h - %s'])
    changes['commits'] = commits.split('\n') if commits else []
    
    # Get modified files
    files = run_command(['git', 'diff', '--name-status', f'HEAD~{num_commits}'])
    changes['files'] = files.split('\n') if files else []
    
    # Get stats
    stats = run_command(['git', 'diff', '--stat', f'HEAD~{num_commits}'])
    changes['stats'] = stats
    
    return changes

def get_test_status() -> Dict[str, str]:
    """Run tests and return status."""
    status = {
        'passing': 'unknown',
        'coverage': 'unknown',
        'failures': []
    }
    
    try:
        result = run_command(['python', '-m', 'pytest', 'tests/', '--quiet'])
        status['passing'] = 'all tests passing' if result else 'tests failing'
    except Exception as e:
        status['failures'].append(str(e))
    
    return status

def get_environment_changes() -> Dict[str, List[str]]:
    """Check for environment changes."""
    changes = {
        'new_deps': [],
        'config': [],
        'database': []
    }
    
    # Check requirements.txt changes
    if Path('requirements.txt').exists():
        reqs = run_command(['git', 'diff', 'HEAD~5', '--', 'requirements.txt'])
        if reqs:
            changes['new_deps'] = [line for line in reqs.split('\n') 
                                 if line.startswith('+') and not line.startswith('++')]
    
    # Check config files
    config_changes = run_command(['git', 'diff', 'HEAD~5', '--', '*.ini', '*.cfg', '*.conf'])
    if config_changes:
        changes['config'] = config_changes.split('\n')
    
    return changes

def update_next_session(changes: Dict[str, List[str]], 
                       test_status: Dict[str, str],
                       env_changes: Dict[str, List[str]]) -> str:
    """Generate NEXT_SESSION.md content."""
    now = datetime.now(pytz.UTC)
    
    content = [
        "# Starting Point for Next Session",
        "",
        "## Recent Changes",
    ]
    
    # Add commits
    for commit in changes['commits']:
        content.append(f"- {commit}")
    
    content.extend([
        "",
        "## Current State",
        f"- Last Updated: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- Tests: {test_status['passing']}",
    ])
    
    if test_status['failures']:
        content.append("- Test Failures:")
        for failure in test_status['failures']:
            content.append(f"  - {failure}")
    
    # Add modified files
    if changes['files']:
        content.extend(["", "## Modified Files"])
        for file in changes['files']:
            content.append(f"- {file}")
    
    # Add environment changes
    if any(env_changes.values()):
        content.extend(["", "## Environment Changes"])
        if env_changes['new_deps']:
            content.append("### New Dependencies")
            for dep in env_changes['new_deps']:
                content.append(f"- {dep}")
        if env_changes['config']:
            content.append("### Configuration Changes")
            for conf in env_changes['config']:
                content.append(f"- {conf}")
    
    # Add next steps from BACKLOG.md
    if Path('BACKLOG.md').exists():
        backlog = Path('BACKLOG.md').read_text()
        tasks = re.findall(r'[-*] \[(.*?)\]', backlog)
        if tasks:
            content.extend([
                "",
                "## Next Steps",
                "High priority tasks from BACKLOG.md:"
            ])
            for task in tasks[:3]:  # Top 3 tasks
                content.append(f"- {task}")
    
    return '\n'.join(content)

def main():
    """Main function to update session documentation."""
    if len(sys.argv) < 2:
        print("Usage: python session_manager.py [start|close]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'close':
        print("Generating session close documentation...")
        changes = get_recent_changes()
        test_status = get_test_status()
        env_changes = get_environment_changes()
        
        next_session_content = update_next_session(changes, test_status, env_changes)
        
        # Write to NEXT_SESSION.md
        Path('NEXT_SESSION.md').write_text(next_session_content)
        print("Updated NEXT_SESSION.md")
        
        # Generate session summary
        summary = [
            f"## Session Summary {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "### Changes",
            changes['stats'],
            "",
            "### Test Status",
            f"- {test_status['passing']}",
            "",
            "### Next Steps",
            "See NEXT_SESSION.md for detailed next steps"
        ]
        
        print("\nSession Summary:")
        print('\n'.join(summary))
        
    elif command == 'start':
        print("Performing session start checks...")
        # Run checks from CHAT_START.md
        checks = [
            ('Git Status', ['git', 'status']),
            ('Recent Commits', ['git', 'log', '-n3', '--oneline']),
            ('Test Status', ['python', '-m', 'pytest', 'tests/', '--quiet']),
            ('Environment', ['pip', 'list'])
        ]
        
        for name, cmd in checks:
            print(f"\n{name}:")
            result = run_command(cmd)
            print(result if result else "No output")

if __name__ == "__main__":
    main()
