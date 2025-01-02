#!/usr/bin/env python3
"""Generate schema constants from schema.yaml."""

import os
import yaml
from typing import Dict, Any


def load_schema() -> Dict[str, Any]:
    """Load schema from yaml file."""
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'schema.yaml')
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)


def generate_column_sizes(schema: Dict[str, Any]) -> str:
    """Generate column size constants."""
    sizes = []
    
    # Email columns
    for name, col in schema['email']['columns'].items():
        if 'size' in col:
            const_name = f"EMAIL_{name.upper()}"
            sizes.append(f'    "{const_name}": {col["size"]},')
    
    # Analysis columns
    for name, col in schema['analysis']['columns'].items():
        if 'size' in col:
            const_name = f"ANALYSIS_{name.upper()}"
            sizes.append(f'    "{const_name}": {col["size"]},')
    
    # Label columns
    for name, col in schema['label']['columns'].items():
        if 'size' in col:
            const_name = f"LABEL_{name.upper()}"
            sizes.append(f'    "{const_name}": {col["size"]},')
    
    return "COLUMN_SIZES: Dict[str, int] = {\n" + "\n".join(sizes) + "\n}"


def generate_defaults(schema: Dict[str, Any]) -> str:
    """Generate default value classes."""
    classes = []
    
    # Email defaults
    email_defaults = []
    for name, value in schema['email']['defaults'].items():
        if isinstance(value, str):
            email_defaults.append(f'    {name}: str = "{value}"')
        elif isinstance(value, bool):
            email_defaults.append(f'    {name}: bool = {str(value)}')
        elif value is None:
            email_defaults.append(f'    {name}: Optional[str] = None')
    classes.append("""
@dataclass
class EmailDefaults:
    \"\"\"Default values for Email fields from schema.yaml.\"\"\"
""" + "\n".join(email_defaults))

    # Analysis defaults
    analysis_defaults = []
    for name, value in schema['analysis']['defaults'].items():
        if isinstance(value, str):
            analysis_defaults.append(f'    {name}: str = "{value}"')
        elif isinstance(value, bool):
            analysis_defaults.append(f'    {name}: bool = {str(value)}')
        elif value is None:
            analysis_defaults.append(f'    {name}: Optional[str] = None')
    classes.append("""
@dataclass
class AnalysisDefaults:
    \"\"\"Default values for Analysis fields from schema.yaml.\"\"\"
""" + "\n".join(analysis_defaults))

    # Label defaults
    label_defaults = []
    for name, value in schema['label']['defaults'].items():
        if isinstance(value, str):
            label_defaults.append(f'    {name}: str = "{value}"')
        elif isinstance(value, bool):
            label_defaults.append(f'    {name}: bool = {str(value)}')
        elif value is None:
            label_defaults.append(f'    {name}: Optional[int] = None')
    classes.append("""
@dataclass
class LabelDefaults:
    \"\"\"Default values for Label fields from schema.yaml.\"\"\"
""" + "\n".join(label_defaults))
    
    return "\n".join(classes)


def generate_validation_constants(schema: Dict[str, Any]) -> str:
    """Generate validation constants."""
    constants = []
    
    # Sentiment validation
    sentiments = schema['analysis']['validation']['valid_sentiments']
    constants.append(f'VALID_SENTIMENTS = {sentiments}')
    
    # Category validation
    categories = schema['analysis']['validation']['valid_categories']
    constants.append(f'VALID_CATEGORIES = {categories}')
    
    # Label validation
    label_types = schema['label']['validation']['valid_types']
    constants.append(f'VALID_LABEL_TYPES = {label_types}')
    
    visibilities = schema['label']['validation']['valid_visibilities']
    constants.append(f'VALID_VISIBILITIES = {visibilities}')
    
    return "\n".join(constants)


def main():
    """Generate schema constants."""
    schema = load_schema()
    
    output = [
        '"""',
        'Schema constants generated from schema.yaml.',
        'DO NOT EDIT THIS FILE MANUALLY - it is generated by generate_schema_constants.py',
        '"""',
        '',
        'from dataclasses import dataclass',
        'from typing import Dict, List, Any, Optional',
        '',
        '# Column sizes',
        generate_column_sizes(schema),
        '',
        '# Default values',
        generate_defaults(schema),
        '',
        '# Validation constants',
        generate_validation_constants(schema),
    ]
    
    constants_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared_lib', 'schema_constants.py')
    with open(constants_path, 'w') as f:
        f.write('\n'.join(output))


if __name__ == '__main__':
    main()