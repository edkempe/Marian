"""String manipulation utilities for the Jexi project."""

import re
from typing import List

def camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', name).lower()

def snake_to_camel(name: str) -> str:
    """Convert snake_case to CamelCase."""
    components = name.split('_')
    return ''.join(x.title() for x in components)

def split_keep_delimiters(text: str, delimiters: str) -> List[str]:
    """Split text but keep the delimiters."""
    pattern = f'([{re.escape(delimiters)}])'
    return [x for x in re.split(pattern, text) if x]
