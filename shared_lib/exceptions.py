"""Custom exceptions for the Marian project."""


class MarianError(Exception):
    """Base exception for all Marian errors."""
    pass


class APIError(MarianError):
    """Error when calling external APIs."""
    pass


class ValidationError(MarianError):
    """Error when validating data."""
    pass


class DatabaseError(MarianError):
    """Error when accessing the database."""
    pass


class ConfigurationError(MarianError):
    """Error in configuration settings."""
    pass


class AuthenticationError(MarianError):
    """Error with authentication."""
    pass


class SemanticError(MarianError):
    """Error in semantic analysis."""
    pass


class DuplicateError(MarianError):
    """Error when duplicate items are found."""
    pass


class TagError(MarianError):
    """Error managing tags."""
    pass


class RelationshipError(MarianError):
    """Error managing relationships."""
    pass
