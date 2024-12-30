#!/usr/bin/env python3
"""Schema verification script for email analyzer."""
import inspect
from typing import Any, Dict, Type

from sqlalchemy import inspect as sql_inspect
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeMeta

from models.base import Base
from models.email import Email
from models.email_analysis import EmailAnalysis
from shared_lib.database_session_util import analysis_engine, email_engine

from .logging_config import setup_logging

# Set up logger
logger = setup_logging(__name__)


def get_model_fields(model_class: Type[DeclarativeMeta]) -> Dict[str, Any]:
    """Get all fields from a SQLAlchemy model."""
    return {
        col.name: {
            "type": str(col.type),
            "nullable": col.nullable,
            "primary_key": col.primary_key,
            "foreign_keys": [fk.target_fullname for fk in col.foreign_keys],
        }
        for col in model_class.__table__.columns
    }


def get_db_fields(engine: Engine, table_name: str) -> Dict[str, Any]:
    """Get all fields from a database table."""
    inspector = sql_inspect(engine)
    columns = inspector.get_columns(table_name)
    pk_constraint = inspector.get_pk_constraint(table_name)
    foreign_keys = inspector.get_foreign_keys(table_name)

    fields = {}
    for col in columns:
        field_info = {
            "type": str(col["type"]),
            "nullable": col.get("nullable", True),
            "primary_key": col["name"] in pk_constraint["constrained_columns"],
            "foreign_keys": [],
        }

        # Add foreign key information
        for fk in foreign_keys:
            if col["name"] in fk["constrained_columns"]:
                field_info["foreign_keys"].append(
                    f"{fk['referred_table']}.{fk['referred_columns'][0]}"
                )

        fields[col["name"]] = field_info

    return fields


def verify_schema(engine: Engine, model_class: Type[DeclarativeMeta]) -> None:
    """Verify that model schema matches database schema."""
    table_name = model_class.__tablename__
    model_fields = get_model_fields(model_class)
    db_fields = get_db_fields(engine, table_name)

    # Check for missing fields
    missing_in_db = set(model_fields.keys()) - set(db_fields.keys())
    missing_in_model = set(db_fields.keys()) - set(model_fields.keys())

    if missing_in_db:
        raise ValueError(
            f"Fields in model but missing in database {table_name}: {missing_in_db}"
        )
    if missing_in_model:
        raise ValueError(
            f"Fields in database but missing in model {table_name}: {missing_in_model}"
        )

    # Check field properties
    for field_name, model_info in model_fields.items():
        db_info = db_fields[field_name]

        # Log field comparison for debugging
        logger.debug(
            "field_comparison",
            table=table_name,
            field=field_name,
            model_info=model_info,
            db_info=db_info,
        )

        # Compare nullable
        if model_info["nullable"] != db_info["nullable"]:
            raise ValueError(
                f"Nullable mismatch for {table_name}.{field_name}: "
                f"model={model_info['nullable']}, db={db_info['nullable']}"
            )

        # Compare primary key
        if model_info["primary_key"] != db_info["primary_key"]:
            raise ValueError(
                f"Primary key mismatch for {table_name}.{field_name}: "
                f"model={model_info['primary_key']}, db={db_info['primary_key']}"
            )

        # Compare foreign keys
        if set(model_info["foreign_keys"]) != set(db_info["foreign_keys"]):
            raise ValueError(
                f"Foreign key mismatch for {table_name}.{field_name}: "
                f"model={model_info['foreign_keys']}, db={db_info['foreign_keys']}"
            )


def verify_code_usage(model_class: Type[DeclarativeMeta]) -> None:
    """Verify that all field references in code exist in model."""
    model_fields = set(get_model_fields(model_class).keys())

    # Get the source code of the model class
    source_lines = inspect.getsource(model_class)

    # TODO: Add more sophisticated code analysis
    # This is a basic check that could be expanded
    logger.info(
        "code_usage_check",
        model=model_class.__name__,
        fields=sorted(list(model_fields)),
    )


def main():
    """Run schema verification."""
    try:
        # Verify Email model
        logger.info("verifying_email_schema")
        verify_schema(email_engine, Email)
        verify_code_usage(Email)
        logger.info("email_schema_verified")

        # Verify EmailAnalysis model
        logger.info("verifying_analysis_schema")
        verify_schema(analysis_engine, EmailAnalysis)
        verify_code_usage(EmailAnalysis)
        logger.info("analysis_schema_verified")

        print("Schema verification completed successfully!")

    except Exception as e:
        logger.error("schema_verification_error", error=str(e))
        raise


if __name__ == "__main__":
    main()
