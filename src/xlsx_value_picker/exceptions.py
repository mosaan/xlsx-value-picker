"""
xlsx-value-picker application specific exceptions.
"""


class XlsxValuePickerError(Exception):
    """Base class for exceptions in this application."""

    pass


class ConfigError(XlsxValuePickerError):
    """Base class for configuration related errors."""

    pass


class ConfigLoadError(ConfigError):
    """Exception raised for errors during config file loading."""

    pass


class ConfigValidationError(ConfigError):
    """Exception raised for errors during config validation."""

    pass


class ExcelProcessingError(XlsxValuePickerError):
    """Exception raised for errors during Excel file processing."""

    pass


class ValidationError(XlsxValuePickerError):
    """Exception raised for data validation errors."""

    pass


class OutputError(XlsxValuePickerError):
    """Exception raised for errors during output generation."""

    pass
