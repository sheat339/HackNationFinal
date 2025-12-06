"""
Custom exceptions for the project.
"""


class IndeksBranzError(Exception):
    """Base exception for Indeks Branż project."""
    pass


class ConfigurationError(IndeksBranzError):
    """Configuration-related errors."""
    pass


class DataCollectionError(IndeksBranzError):
    """Data collection errors."""
    pass


class DataProcessingError(IndeksBranzError):
    """Data processing errors."""
    pass


class CalculationError(IndeksBranzError):
    """Calculation errors."""
    pass


class VisualizationError(IndeksBranzError):
    """Visualization errors."""
    pass


class ValidationError(IndeksBranzError):
    """Validation errors."""
    pass

