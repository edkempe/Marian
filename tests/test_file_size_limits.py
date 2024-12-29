"""Test module for file size and complexity limits.

This module checks if files are getting too large for reliable processing
by Windsurf.ai. It provides warnings for files approaching limits and
errors for files exceeding limits.

Thresholds are adjusted based on file type:
- Python files: More permissive due to docstrings and type hints
- Documentation: More permissive due to markdown formatting
- Other code files: Stricter limits to encourage modularity
"""

import os
import ast
from pathlib import Path
import pytest
from typing import Dict, List, Set, Tuple, NamedTuple
from dataclasses import dataclass

@dataclass
class ComplexityMetrics:
    """Stores code complexity metrics for a file."""
    class_count: int = 0
    method_count: int = 0
    function_count: int = 0
    max_method_lines: int = 0
    max_function_lines: int = 0
    max_class_lines: int = 0
    max_nesting_depth: int = 0
    cognitive_complexity: int = 0
    import_count: int = 0
    comment_ratio: float = 0.0
    longest_method_name: str = ""
    longest_function_name: str = ""
    longest_class_name: str = ""

class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to compute complexity metrics."""
    
    def __init__(self):
        self.metrics = ComplexityMetrics()
        self.current_depth = 0
        self.max_depth = 0
        self.current_node_lines = 0
        self.class_stack = []
        
    def visit_ClassDef(self, node):
        """Visit a class definition."""
        self.metrics.class_count += 1
        lines = len(ast.unparse(node).split('\n'))
        self.metrics.max_class_lines = max(self.metrics.max_class_lines, lines)
        if len(node.name) > len(self.metrics.longest_class_name):
            self.metrics.longest_class_name = node.name
        self.class_stack.append(node)
        self.generic_visit(node)
        self.class_stack.pop()
        
    def visit_FunctionDef(self, node):
        """Visit a function definition."""
        if self.class_stack:
            self.metrics.method_count += 1
            lines = len(ast.unparse(node).split('\n'))
            self.metrics.max_method_lines = max(self.metrics.max_method_lines, lines)
            if len(node.name) > len(self.metrics.longest_method_name):
                self.metrics.longest_method_name = node.name
        else:
            self.metrics.function_count += 1
            lines = len(ast.unparse(node).split('\n'))
            self.metrics.max_function_lines = max(self.metrics.max_function_lines, lines)
            if len(node.name) > len(self.metrics.longest_function_name):
                self.metrics.longest_function_name = node.name
        self.generic_visit(node)
        
    def visit_Import(self, node):
        """Visit an import statement."""
        self.metrics.import_count += len(node.names)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        """Visit a from-import statement."""
        self.metrics.import_count += len(node.names)
        self.generic_visit(node)
        
    def _increment_complexity(self, node):
        """Increment cognitive complexity based on node type."""
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        # Basic complexity increment
        self.metrics.cognitive_complexity += self.current_depth
        
    def visit_If(self, node):
        self._increment_complexity(node)
        self.generic_visit(node)
        self.current_depth -= 1
        
    def visit_For(self, node):
        self._increment_complexity(node)
        self.generic_visit(node)
        self.current_depth -= 1
        
    def visit_While(self, node):
        self._increment_complexity(node)
        self.generic_visit(node)
        self.current_depth -= 1
        
    def visit_Try(self, node):
        self._increment_complexity(node)
        self.generic_visit(node)
        self.current_depth -= 1

def analyze_file_complexity(file_path: str) -> ComplexityMetrics:
    """Analyze a Python file for complexity metrics."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Calculate comment ratio
        lines = content.split('\n')
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        total_lines = len(lines)
        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
            
        # Parse and analyze AST
        tree = ast.parse(content)
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        # Update metrics
        visitor.metrics.max_nesting_depth = visitor.max_depth
        visitor.metrics.comment_ratio = comment_ratio
        
        return visitor.metrics
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {str(e)}")
        return ComplexityMetrics()

# Complexity thresholds
COMPLEXITY_THRESHOLDS = {
    'class_count': 10,
    'method_count': 20,
    'function_count': 20,
    'max_method_lines': 50,
    'max_function_lines': 50,
    'max_class_lines': 200,
    'max_nesting_depth': 5,
    'cognitive_complexity': 30,
    'import_count': 30,
    'min_comment_ratio': 0.1
}

# Base thresholds
BASE_WARNING_LINES = 750
BASE_ERROR_LINES = 1500
BASE_WARNING_SIZE = 75 * 1024  # 75KB
BASE_ERROR_SIZE = 150 * 1024   # 150KB

# File type specific multipliers
THRESHOLD_MULTIPLIERS = {
    # Python files get 1.2x allowance for docstrings and type hints
    '.py': {
        'lines': 1.2,
        'size': 1.2
    },
    # Documentation files get different multipliers for warnings vs errors
    '.md': {
        'lines': {
            'warning': 1.5,  # Warning at 1125 lines
            'error': 1.2     # Error at 1800 lines
        },
        'size': {
            'warning': 1.5,  # Warning at 112.5KB
            'error': 1.2     # Error at 180KB
        }
    },
    '.rst': {
        'lines': {
            'warning': 1.5,
            'error': 2.0
        },
        'size': {
            'warning': 1.5,
            'error': 2.0
        }
    },
    # Default multiplier for other files
    'default': {
        'lines': 1.0,
        'size': 1.0
    }
}

def get_thresholds(file_suffix: str) -> Dict[str, Dict[str, int]]:
    """Get warning and error thresholds for a file type."""
    multiplier = THRESHOLD_MULTIPLIERS.get(file_suffix, THRESHOLD_MULTIPLIERS['default'])
    
    # Handle the new nested multiplier structure for markdown files
    if isinstance(multiplier.get('lines'), dict):
        return {
            'warning': {
                'lines': int(BASE_WARNING_LINES * multiplier['lines']['warning']),
                'size': int(BASE_WARNING_SIZE * multiplier['size']['warning'])
            },
            'error': {
                'lines': int(BASE_ERROR_LINES * multiplier['lines']['error']),
                'size': int(BASE_ERROR_SIZE * multiplier['size']['error'])
            }
        }
    
    return {
        'warning': {
            'lines': int(BASE_WARNING_LINES * multiplier['lines']),
            'size': int(BASE_WARNING_SIZE * multiplier['size'])
        },
        'error': {
            'lines': int(BASE_ERROR_LINES * multiplier['lines']),
            'size': int(BASE_ERROR_SIZE * multiplier['size'])
        }
    }

def get_file_stats() -> List[Dict]:
    """Get statistics for all relevant files in the project."""
    project_root = Path(__file__).parent.parent
    stats = []
    
    # File patterns to check
    code_patterns = ['*.py', '*.js', '*.ts', '*.jsx', '*.tsx']
    doc_patterns = ['*.md', '*.rst', '*.txt']
    
    # Directories to exclude
    exclude_dirs = {'.git', '.pytest_cache', '__pycache__', 'venv', '.env', 'node_modules'}
    
    def should_check_dir(path: Path) -> bool:
        return not any(part in path.parts for part in exclude_dirs)
    
    # Gather file statistics
    for pattern in code_patterns + doc_patterns:
        for file_path in project_root.rglob(pattern):
            if not should_check_dir(file_path):
                continue
                
            try:
                size = file_path.stat().st_size
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = sum(1 for _ in f)
                    
                stats.append({
                    'path': str(file_path),
                    'size': size,
                    'lines': lines,
                    'is_doc': file_path.suffix in ['.md', '.rst', '.txt']
                })
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                
    return stats

def print_file_statistics(stats: List[Dict]) -> None:
    """Print statistics about files sorted by length."""
    print("\nFile length statistics:")
    print("=" * 80)
    
    # Filter and sort Python files by length
    python_files = [s for s in stats if s['path'].endswith('.py')]
    python_files.sort(key=lambda x: x['lines'], reverse=True)
    
    print("\nTop 10 longest Python files:")
    print("-" * 80)
    for stat in python_files[:10]:
        metrics = analyze_file_complexity(stat['path'])
        print(f"\n{stat['path']}:")
        print(f"  Lines: {stat['lines']} ({stat['size']/1024:.1f}KB)")
        print(f"  Classes: {metrics.class_count} (longest: {metrics.max_class_lines} lines)")
        print(f"  Methods: {metrics.method_count} (longest: {metrics.max_method_lines} lines)")
        print(f"  Functions: {metrics.function_count} (longest: {metrics.max_function_lines} lines)")
        print(f"  Max Nesting: {metrics.max_nesting_depth}")
        print(f"  Cognitive Complexity: {metrics.cognitive_complexity}")
        print(f"  Imports: {metrics.import_count}")
        print(f"  Comment Ratio: {metrics.comment_ratio:.1%}")
        
def test_file_size_warnings(capsys):
    """Test for files approaching size limits (warning level)."""
    stats = get_file_stats()
    warnings = []
    
    # Print statistics
    print_file_statistics(stats)
    captured = capsys.readouterr()
    print(captured.out)  # This will show in pytest output
    
    for stat in stats:
        thresholds = get_thresholds(stat['path'].split('.')[-1])
        if stat['lines'] > thresholds['warning']['lines']:
            warnings.append(f"WARNING: {stat['path']} has {stat['lines']} lines (threshold: {thresholds['warning']['lines']})")
        if stat['size'] > thresholds['warning']['size']:
            warnings.append(f"WARNING: {stat['path']} is {stat['size']/1024:.1f}KB (threshold: {thresholds['warning']['size']/1024:.1f}KB)")
    
    if warnings:
        print("\nFile size warnings:")
        for warning in warnings:
            print(warning)
        
    # Don't fail the test for warnings
    assert True

def test_file_size_errors():
    """Test for files exceeding size limits (error level)."""
    stats = get_file_stats()
    errors = []
    
    for stat in stats:
        thresholds = get_thresholds(stat['path'].split('.')[-1])
        if stat['lines'] > thresholds['error']['lines']:
            errors.append(f"ERROR: {stat['path']} has {stat['lines']} lines (threshold: {thresholds['error']['lines']})")
        if stat['size'] > thresholds['error']['size']:
            errors.append(f"ERROR: {stat['path']} is {stat['size']/1024:.1f}KB (threshold: {thresholds['error']['size']/1024:.1f}KB)")
    
    if errors:
        print("\nFile size errors:")
        for error in errors:
            print(error)
        
    # Fail the test if there are errors
    assert not errors, "Files found exceeding size limits"

def test_file_complexity():
    """Test for file complexity metrics."""
    stats = get_file_stats()
    warnings = []
    
    for stat in stats:
        if not stat['is_doc'] and stat['path'].endswith('.py'):
            metrics = analyze_file_complexity(stat['path'])
            for metric, value in metrics.__dict__.items():
                if metric in COMPLEXITY_THRESHOLDS and value > COMPLEXITY_THRESHOLDS[metric]:
                    warnings.append(f"WARNING: {stat['path']} has high {metric} ({value})")
                    
    if warnings:
        print("\nComplexity warnings:")
        for warning in warnings:
            print(warning)
            
    # Don't fail the test for complexity warnings
    assert True

if __name__ == '__main__':
    pytest.main([__file__])
