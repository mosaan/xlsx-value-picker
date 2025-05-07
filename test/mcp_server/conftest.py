"""
Test fixtures and utilities for MCP Server tests.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml


@pytest.fixture
def mock_server():
    """Create a mock FastMCP server instance."""
    server = MagicMock()
    server.method = MagicMock()
    return server


@pytest.fixture
def mock_model_config():
    """Create a mock ModelConfig instance."""
    from xlsx_value_picker.config_loader import ModelConfig
    from xlsx_value_picker.output_formatter import OutputFormat

    # Create a mock output format
    output_format = OutputFormat(format="json")

    # Create a mock ModelConfig
    model_config = ModelConfig(
        excel_file_path="test.xlsx", sheet_name="Sheet1", fields={"A1": "header1"}, rules=[], output=output_format
    )

    return model_config


@pytest.fixture
def mock_app_config(mock_model_config):
    """Create a mock AppConfig instance with test models."""
    from xlsx_value_picker.config_loader import AppConfig

    app_config = AppConfig(models={"test_model": mock_model_config})

    return app_config


@pytest.fixture
def mock_state(mock_app_config):
    """Create a mock server state with test configuration."""
    state = MagicMock()
    state.app_config = mock_app_config
    state.config_path = "test_config.yaml"

    return state


@pytest.fixture
def test_config_data():
    """Create test configuration data."""
    return {
        "models": {
            "test_model": {
                "excel_file_path": "test.xlsx",
                "sheet_name": "Sheet1",
                "fields": {"A1": "header1"},
                "rules": [],
                "output": {"format": "json"},
            }
        }
    }


@pytest.fixture
def test_config_file(test_config_data):
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp:
        yaml.dump(test_config_data, temp)
        temp_path = Path(temp.name)

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def mock_validation_results():
    """Create mock validation results."""
    # Create a successful validation result (empty list means no issues)
    empty_result = []

    # Create a validation error result
    error_result = [
        MagicMock(
            error_message="Test validation error",
            error_fields=["field1"],
            error_locations=["A1"],
            rule_name="test_rule",
            severity="error",
        )
    ]

    return {"success": empty_result, "error": error_result}


@pytest.fixture
def mock_validation_engine(mock_validation_results):
    """Create a mock validation engine with configurable results."""
    mock_engine = MagicMock()
    mock_engine_instance = MagicMock()
    mock_engine_instance.validate.return_value = mock_validation_results["success"]
    mock_engine.return_value = mock_engine_instance

    with patch("xlsx_value_picker.validation.ValidationEngine", mock_engine):
        yield mock_engine


@pytest.fixture
def mock_excel_extractor():
    """Create a mock Excel value extractor."""
    mock_instance = MagicMock()
    mock_instance.extract_values.return_value = {"data": "test_data"}

    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_instance
    mock_cm.__exit__.return_value = None

    mock_extractor = MagicMock(return_value=mock_cm)

    with patch("xlsx_value_picker.excel_processor.ExcelValueExtractor", mock_extractor):
        yield mock_instance


@pytest.fixture
def mock_output_formatter():
    """Create a mock output formatter."""
    mock_formatter_instance = MagicMock()
    mock_formatter_instance.format_output.return_value = "formatted_output"

    mock_formatter = MagicMock(return_value=mock_formatter_instance)

    with patch("xlsx_value_picker.output_formatter.OutputFormatter", mock_formatter):
        yield mock_formatter_instance


class MockMCPClient:
    """Mock MCP client for testing server-client interactions."""

    def __init__(self, server_process):
        self.server_process = server_process
        self.stdin = server_process.stdin
        self.stdout = server_process.stdout
        self.request_id = 0

    def send_request(self, method, params=None):
        """Send a request to the MCP server and return the response."""
        import json

        self.request_id += 1
        request = {"jsonrpc": "2.0", "id": self.request_id, "method": method, "params": params or {}}

        # Send request
        self.stdin.write(json.dumps(request).encode() + b"\n")
        self.stdin.flush()

        # Receive response
        response_line = self.stdout.readline()
        return json.loads(response_line.decode())
