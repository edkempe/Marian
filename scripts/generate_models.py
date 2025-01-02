#!/usr/bin/env python3
"""Generate SQLAlchemy models from schema.yaml."""

import os
import yaml
from typing import Dict, Any, List


def load_schema() -> Dict[str, Any]:
    """Load schema from yaml file."""
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'schema.yaml')
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)


def get_column_type(col_config: Dict[str, Any]) -> str:
    """Convert schema type to SQLAlchemy type."""
    type_map = {
        'string': lambda size: f'String({size})' if 'size' in col_config else 'String',
        'text': lambda _: 'Text',
        'integer': lambda _: 'Integer',
        'float': lambda _: 'Float',
        'boolean': lambda _: 'Boolean',
        'datetime': lambda _: 'DateTime',
        'json': lambda _: 'JSON',
    }
    col_type = col_config.get('type', 'string').lower()
    type_func = type_map.get(col_type, type_map['string'])
    return type_func(col_config.get('size', None))


def get_class_name(name: str) -> str:
    """Get the class name for a table."""
    name_map = {
        'email': 'EmailMessage',
        'analysis': 'EmailAnalysis',
        'label': 'GmailLabel',
        'catalog': 'CatalogItem',
        'tags': 'Tag',
        'relationships': 'ItemRelationship',
        'catalog_tags': 'CatalogTag'
    }
    return name_map.get(name, name.title().replace('_', ''))


def get_table_name(name: str) -> str:
    """Get the table name for a model."""
    name_map = {
        'email': 'email_messages',
        'analysis': 'email_analysis',
        'label': 'gmail_labels',
        'catalog': 'catalog_items',
        'tags': 'tags',
        'relationships': 'item_relationships',
        'catalog_tags': 'catalog_tags'
    }
    return name_map.get(name, name)


def get_file_name(name: str) -> str:
    """Get the file name for a table."""
    name_map = {
        'email': 'email_message',
        'analysis': 'email_analysis',
        'label': 'gmail_label',
        'catalog': 'catalog_item',
        'tags': 'tag',
        'relationships': 'item_relationship',
        'catalog_tags': 'catalog_tag'
    }
    return name_map.get(name, name) + '.py'


def generate_column_str(col_name: str, col_config: Dict[str, Any], defaults: Dict[str, Any]) -> str:
    """Generate a column definition string."""
    col_type = get_column_type(col_config)
    attrs = []
    
    # Add nullable
    nullable = col_config.get('nullable', True)
    attrs.append(f'nullable={nullable}')
    
    # Add primary key
    if col_config.get('primary_key', False):
        attrs.append('primary_key=True')
    
    # Get default from defaults section if exists
    default = defaults.get(col_name)
    if default is not None:
        if isinstance(default, str):
            attrs.append(f'default="{default}"')
        elif isinstance(default, (bool, int, float)):
            attrs.append(f'default={default}')

    comment = col_config.get('description', '')
    attrs_str = ', '.join(attrs)
    
    return f"""    {col_name} = Column(
        {col_type},
        {attrs_str},
        comment="{comment}"
    )"""


def generate_model(name, config):
    """Generate a SQLAlchemy model class."""
    model_lines = [
        f'"""SQLAlchemy model for {name} table."""',
        '',
        'from datetime import datetime',
        'from typing import Any, Dict, List, Optional',
        'from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, Table',
        'from sqlalchemy.orm import relationship, validates',
        'from models.base import Base',
        'from shared_lib.schema_constants import COLUMN_SIZES',
        '',
        '',
    ]

    # Add association tables first
    relationships = config.get('relationships', {})
    for rel_name, rel_config in relationships.items():
        if rel_config['type'] == 'many_to_many':
            secondary_table = rel_config.get('secondary')
            if secondary_table:
                source_fk = f'{name}.id'
                target_fk = f'{rel_config["model"].lower()}.id'
                
                model_lines.extend([
                    f'# Define {secondary_table} if it does not exist',
                    f'try:',
                    f'    {secondary_table}',
                    f'except NameError:',
                    f'    {secondary_table} = Table(',
                    f'        "{secondary_table}",',
                    '        Base.metadata,',
                    f'        Column("source_id", String(100), ForeignKey("{source_fk}"), primary_key=True),',
                    f'        Column("target_id", String(100), ForeignKey("{target_fk}"), primary_key=True),',
                    '        extend_existing=True',
                    '    )',
                    ''
                ])

    # Generate model class
    class_name = get_class_name(name)
    table_name = get_table_name(name)
    database = config.get("database", "catalog")
    docstring = config.get("description", "Model based on schema.yaml configuration.")
    
    model_lines.extend([
        f'class {class_name}(Base):',
        f'    """{docstring}"""',
        '',
        f'    __tablename__ = "{table_name}"',
        '',
        '    # Table configuration',
        '    __table_args__ = {"extend_existing": True}',
        '',
        '    # Database configuration',
        f'    __database__ = "{database}"  # Default to catalog if not specified',
        '',
        '    # Columns'
    ])

    # Add columns
    columns = config['columns']
    for col_name, col_config in columns.items():
        col_type = col_config['type']
        nullable = col_config.get('nullable', True)
        default = col_config.get('default', None)
        comment = col_config.get('description', '')
        primary_key = col_config.get('primary_key', False)
        foreign_key = col_config.get('foreign_key', None)
        
        col_args = []
        if col_type == 'string':
            size = col_config.get('size', 100)
            col_args.append(f'String({size})')
        elif col_type == 'text':
            col_args.append('Text')
        elif col_type == 'integer':
            col_args.append('Integer')
        elif col_type == 'float':
            col_args.append('Float')
        elif col_type == 'boolean':
            col_args.append('Boolean')
        elif col_type == 'json':
            col_args.append('JSON')
        elif col_type == 'datetime':
            col_args.append('DateTime')

        if foreign_key:
            col_args.append(f'ForeignKey("{foreign_key}")')
        if not nullable:
            col_args.append('nullable=False')
        if primary_key:
            col_args.append('primary_key=True')
        if default is not None:
            if isinstance(default, str):
                col_args.append(f'default="{default}"')
            else:
                col_args.append(f'default={default}')
        if comment:
            col_args.append(f'comment="{comment}"')

        col_def = f'    {col_name} = Column(\n        {",\n        ".join(col_args)}\n    )'
        model_lines.append(col_def)
        model_lines.append('')

    # Add relationships
    if relationships:
        model_lines.append('    # Relationships')
        for rel_name, rel_config in relationships.items():
            rel_type = rel_config['type']
            target_model = rel_config['model']
            back_populates = rel_config.get('back_populates', '')
            cascade = rel_config.get('cascade', '')
            
            rel_args = [f'        "{target_model}"']
            if back_populates:
                rel_args.append(f'        back_populates="{back_populates}"')
            if cascade:
                rel_args.append(f'        cascade="{cascade}"')
            if rel_type == 'many_to_many':
                secondary = rel_config.get('secondary', '')
                if secondary:
                    rel_args.append(f'        secondary={secondary}')
            
            model_lines.extend([
                f'    {rel_name} = relationship(',
                ',\n'.join(rel_args),
                '    )',
                ''
            ])

    # Add timestamps
    model_lines.extend([
        '    # Timestamps',
        '    created_at = Column(DateTime, default=datetime.utcnow)',
        '    updated_at = Column(',
        '        DateTime,',
        '        default=datetime.utcnow,',
        '        onupdate=datetime.utcnow',
        '    )',
        ''
    ])

    # Add validation methods
    validation = config.get('validation', {})
    if validation:
        model_lines.append('    # Validation methods')
        for field, rules in validation.items():
            if isinstance(rules, dict) and 'max_length' in rules:
                model_lines.extend([
                    f'    @validates("{field}")',
                    f'    def validate_{field}(self, key, value):',
                    f'        """Validate {field} length."""',
                    f'        if value is not None and len(value) > {rules["max_length"]}:',
                    f'            raise ValueError(f"{field} cannot be longer than {rules["max_length"]} characters")',
                    '        return value',
                    ''
                ])

    # Add constructor and repr
    model_lines.extend([
        '    def __init__(self, **kwargs):',
        '        """Initialize a new record."""',
        '        super().__init__(**kwargs)',
        '',
        '    def __repr__(self) -> str:',
        '        """Get string representation."""',
        f'        return f"<{class_name}(id={{self.id!r}})>"'
    ])

    return '\n'.join(model_lines)


def generate_registry(models: Dict[str, str]) -> str:
    """Generate registry.py content."""
    imports = []
    model_names = []
    
    # Add standard imports
    imports.extend([
        '"""Model registry."""',
        '',
        'from sqlalchemy.orm import registry',
        '',
        'from models.base import Base'
    ])
    
    # Add model imports
    for filename, _ in models.items():
        module_name = filename.replace('.py', '')
        class_name = get_class_name(module_name)
        imports.append(f'from models.{module_name} import {class_name}')
        model_names.append(class_name)
    
    # Add registry setup
    registry_setup = [
        '',
        '# Create registry',
        'mapper_registry = registry()',
        '',
        '# Configure registry with all models',
        'mapper_registry.configure()',
        '',
        '# Export Base for use in tests',
        '__all__ = ["Base"]',
        ''
    ]
    
    return '\n'.join(imports + registry_setup)


def generate_env(models: Dict[str, str]) -> str:
    """Generate env.py content."""
    env_lines = [
        '"""Alembic environment configuration."""',
        '',
        'import os',
        'from logging.config import fileConfig',
        'from typing import Dict, List',
        '',
        'from alembic import context',
        'from sqlalchemy import engine_from_config, pool',
        '',
        'from models.base import Base',
        'from shared_lib.database_session_util import get_database_url',
        '',
        '# Import all models to ensure they are registered with Base.metadata',
    ]

    # Import all models
    for model_name in models:
        module_name = model_name.replace('.py', '')
        class_name = get_class_name(module_name)
        env_lines.append(f'from models.{module_name} import {class_name}')

    env_lines.extend([
        '',
        '# This is the Alembic Config object',
        'config = context.config',
        '',
        '# Interpret the config file for Python logging',
        'if config.config_file_name is not None:',
        '    fileConfig(config.config_file_name)',
        '',
        '# Get database URL',
        'url = get_database_url()',
        '',
        'def run_migrations_offline() -> None:',
        '    """Run migrations in offline mode."""',
        '    context.configure(',
        '        url=url,',
        '        target_metadata=Base.metadata,',
        '        literal_binds=True,',
        '        dialect_opts={"paramstyle": "named"}',
        '    )',
        '',
        '    with context.begin_transaction():',
        '        context.run_migrations()',
        '',
        'def run_migrations_online() -> None:',
        '    """Run migrations in online mode."""',
        '    configuration = config.get_section(config.config_ini_section) or {}',
        '    configuration["sqlalchemy.url"] = url',
        '',
        '    connectable = engine_from_config(',
        '        configuration,',
        '        prefix="sqlalchemy.",',
        '        poolclass=pool.NullPool,',
        '    )',
        '',
        '    with connectable.connect() as connection:',
        '        context.configure(',
        '            connection=connection,',
        '            target_metadata=Base.metadata',
        '        )',
        '',
        '        with context.begin_transaction():',
        '            context.run_migrations()',
        '',
        'if context.is_offline_mode():',
        '    run_migrations_offline()',
        'else:',
        '    run_migrations_online()',
        ''
    ])

    return '\n'.join(env_lines)


def generate_models(schema: Dict[str, Any]) -> Dict[str, str]:
    """Generate all models from schema."""
    models = {}
    for table_name, table_config in schema.items():
        # Skip non-table sections
        if not isinstance(table_config, dict) or 'columns' not in table_config:
            continue
        model_content = generate_model(table_name, table_config)
        models[get_file_name(table_name)] = model_content
    return models


def main():
    """Generate models from schema.yaml."""
    schema = load_schema()
    models = generate_models(schema)
    
    # Create models directory if it doesn't exist
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Write model files
    for filename, content in models.items():
        filepath = os.path.join(models_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Generated {filepath}")
    
    # Write registry
    registry_path = os.path.join(models_dir, 'registry.py')
    registry_content = generate_registry(models)
    with open(registry_path, 'w') as f:
        f.write(registry_content)
    print(f"Generated {registry_path}")
    
    # Write env.py
    migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')
    env_path = os.path.join(migrations_dir, 'env.py')
    env_content = generate_env(models)
    with open(env_path, 'w') as f:
        f.write(env_content)
    print(f"Generated {env_path}")


if __name__ == '__main__':
    main()
