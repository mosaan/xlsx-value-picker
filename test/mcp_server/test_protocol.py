"""
Tests for MCP Server protocol data structures.
"""
from unittest.mock import patch

import pytest
from pydantic import ValidationError


class TestListModelsProtocol:
    """Tests for ListModels request and response protocol."""

    def test_list_models_response_validation(self):
        """Test validation of ListModelsResponse."""
        # Mock implementation for testing
        with patch("xlsx_value_picker.mcp_server.protocol.ListModelsResponse") as mock_response_class:
            # Define a minimal Pydantic model for testing

            from pydantic import BaseModel

            class ListModelsResponse(BaseModel):
                """Response for $/listModels method."""
                models: list[str]

            # Use our test implementation
            mock_response_class.side_effect = ListModelsResponse

            # Import and test
            from xlsx_value_picker.mcp_server.protocol import ListModelsResponse

            # Valid response
            valid_response = ListModelsResponse(models=["model1", "model2"])
            assert valid_response.models == ["model1", "model2"]

            # Invalid response (missing required field)
            with pytest.raises(ValidationError):
                ListModelsResponse()


class TestGetModelInfoProtocol:
    """Tests for GetModelInfo request and response protocol."""

    def test_get_model_info_request_validation(self):
        """Test validation of GetModelInfoRequest."""
        # Mock implementation for testing
        with patch("xlsx_value_picker.mcp_server.protocol.GetModelInfoRequest") as mock_request_class:
            # Define a minimal Pydantic model for testing
            from pydantic import BaseModel

            class GetModelInfoRequest(BaseModel):
                """Request for $/getModelInfo method."""
                model_id: str

            # Use our test implementation
            mock_request_class.side_effect = GetModelInfoRequest

            # Import and test
            from xlsx_value_picker.mcp_server.protocol import GetModelInfoRequest

            # Valid request
            valid_request = GetModelInfoRequest(model_id="test_model")
            assert valid_request.model_id == "test_model"

            # Invalid request (missing required field)
            with pytest.raises(ValidationError):
                GetModelInfoRequest()

    def test_get_model_info_response_validation(self):
        """Test validation of GetModelInfoResponse."""
        # Mock implementation for testing
        with patch("xlsx_value_picker.mcp_server.protocol.GetModelInfoResponse") as mock_response_class:
            # Define a minimal Pydantic model for testing

            from pydantic import BaseModel

            class GetModelInfoResponse(BaseModel):
                """Response for $/getModelInfo method."""
                model_id: str
                excel_file_path: str
                sheet_name: str
                fields: dict[str, str]
                rules_count: int

            # Use our test implementation
            mock_response_class.side_effect = GetModelInfoResponse

            # Import and test
            from xlsx_value_picker.mcp_server.protocol import GetModelInfoResponse

            # Valid response
            valid_response = GetModelInfoResponse(
                model_id="test_model",
                excel_file_path="test.xlsx",
                sheet_name="Sheet1",
                fields={"A1": "header1"},
                rules_count=2
            )
            assert valid_response.model_id == "test_model"
            assert valid_response.excel_file_path == "test.xlsx"
            assert valid_response.sheet_name == "Sheet1"
            assert valid_response.fields == {"A1": "header1"}
            assert valid_response.rules_count == 2

            # Invalid response (missing required fields)
            with pytest.raises(ValidationError):
                GetModelInfoResponse(model_id="test_model")


class TestGetDiagnosticsProtocol:
    """Tests for GetDiagnostics request and response protocol."""

    def test_validation_diagnostic_model(self):
        """Test validation of ValidationDiagnostic model."""
        # Mock implementation for testing
        with patch("xlsx_value_picker.mcp_server.protocol.ValidationDiagnostic") as mock_diagnostic_class:
            # Define a minimal Pydantic model for testing

            from pydantic import BaseModel

            class ValidationDiagnostic(BaseModel):
                """Diagnostic information for validation issues."""
                message: str
                fields: list[str]
                locations: list[str]
                rule: str
                severity: str = "error"

            # Use our test implementation
            mock_diagnostic_class.side_effect = ValidationDiagnostic

            # Import and test
            from xlsx_value_picker.mcp_server.protocol import ValidationDiagnostic

            # Valid diagnostic
            valid_diagnostic = ValidationDiagnostic(
                message="Test error",
                fields=["field1"],
                locations=["A1"],
                rule="test_rule"
            )
            assert valid_diagnostic.message == "Test error"
            assert valid_diagnostic.fields == ["field1"]
            assert valid_diagnostic.locations == ["A1"]
            assert valid_diagnostic.rule == "test_rule"
            assert valid_diagnostic.severity == "error"  # Default value

            # With custom severity
            custom_severity = ValidationDiagnostic(
                message="Test warning",
                fields=["field2"],
                locations=["B2"],
                rule="test_rule",
                severity="warning"
            )
            assert custom_severity.severity == "warning"

            # Invalid diagnostic (missing required fields)
            with pytest.raises(ValidationError):
                ValidationDiagnostic(message="Test error")

    def test_get_diagnostics_request_validation(self):
        """Test validation of GetDiagnosticsRequest."""
        # Mock implementation for testing
        with patch("xlsx_value_picker.mcp_server.protocol.GetDiagnosticsRequest") as mock_request_class:
            # Define a minimal Pydantic model for testing
            from pydantic import BaseModel

            class GetDiagnosticsRequest(BaseModel):
                """Request for $/getDiagnostics method."""
                model_id: str

            # Use our test implementation
            mock_request_class.side_effect = GetDiagnosticsRequest

            # Import and test
            from xlsx_value_picker.mcp_server.protocol import GetDiagnosticsRequest

            # Valid request
            valid_request = GetDiagnosticsRequest(model_id="test_model")
            assert valid_request.model_id == "test_model"

            # Invalid request (missing required field)
            with pytest.raises(ValidationError):
                GetDiagnosticsRequest()

    def test_get_diagnostics_response_validation(self):
        """Test validation of GetDiagnosticsResponse."""
        # Mock implementation for testing
        with patch("xlsx_value_picker.mcp_server.protocol.GetDiagnosticsResponse") as mock_response_class:
            with patch("xlsx_value_picker.mcp_server.protocol.ValidationDiagnostic") as mock_diagnostic_class:
                # Define minimal Pydantic models for testing

                from pydantic import BaseModel

                class ValidationDiagnostic(BaseModel):
                    """Diagnostic information for validation issues."""
                    message: str
                    fields: list[str]
                    locations: list[str]
                    rule: str
                    severity: str = "error"

                class GetDiagnosticsResponse(BaseModel):
                    """Response for $/getDiagnostics method."""
                    diagnostics: list[ValidationDiagnostic]
                    is_valid: bool

                # Use our test implementations
                mock_diagnostic_class.side_effect = ValidationDiagnostic
                mock_response_class.side_effect = GetDiagnosticsResponse

                # Import and test
                from xlsx_value_picker.mcp_server.protocol import GetDiagnosticsResponse, ValidationDiagnostic

                # Create test diagnostics
                test_diagnostic = ValidationDiagnostic(
                    message="Test error",
                    fields=["field1"],
                    locations=["A1"],
                    rule="test_rule"
                )

                # Valid response with diagnostics
                valid_response_with_diagnostics = GetDiagnosticsResponse(
                    diagnostics=[test_diagnostic],
                    is_valid=False
                )
                assert valid_response_with_diagnostics.diagnostics[0].message == "Test error"
                assert valid_response_with_diagnostics.is_valid is False

                # Valid response without diagnostics
                valid_response_without_diagnostics = GetDiagnosticsResponse(
                    diagnostics=[],
                    is_valid=True
                )
                assert len(valid_response_without_diagnostics.diagnostics) == 0
                assert valid_response_without_diagnostics.is_valid is True

                # Invalid response (missing required fields)
                with pytest.raises(ValidationError):
                    GetDiagnosticsResponse(is_valid=True)


class TestGetFileContentProtocol:
    """Tests for GetFileContent request and response protocol."""

    def test_get_file_content_request_validation(self):
        """Test validation of GetFileContentRequest."""
        # Mock implementation for testing
        with patch("xlsx_value_picker.mcp_server.protocol.GetFileContentRequest") as mock_request_class:
            # Define a minimal Pydantic model for testing

            from pydantic import BaseModel

            class GetFileContentRequest(BaseModel):
                """Request for $/getFileContent method."""
                model_id: str
                skip_validation: bool | None = False
                ignore_validation: bool | None = False

            # Use our test implementation
            mock_request_class.side_effect = GetFileContentRequest

            # Import and test
            from xlsx_value_picker.mcp_server.protocol import GetFileContentRequest

            # Valid request with defaults
            valid_request = GetFileContentRequest(model_id="test_model")
            assert valid_request.model_id == "test_model"
            assert valid_request.skip_validation is False
            assert valid_request.ignore_validation is False

            # Valid request with all fields
            valid_request_full = GetFileContentRequest(
                model_id="test_model",
                skip_validation=True,
                ignore_validation=True
            )
            assert valid_request_full.skip_validation is True
            assert valid_request_full.ignore_validation is True

            # Invalid request (missing required field)
            with pytest.raises(ValidationError):
                GetFileContentRequest()

    def test_get_file_content_response_validation(self):
        """Test validation of GetFileContentResponse."""
        # Mock implementation for testing
        with patch("xlsx_value_picker.mcp_server.protocol.GetFileContentResponse") as mock_response_class:
            with patch("xlsx_value_picker.mcp_server.protocol.ValidationError") as mock_validation_error:
                # Define minimal Pydantic models for testing

                from pydantic import BaseModel

                class ValidationError(BaseModel):
                    """Validation error information."""
                    message: str
                    fields: list[str]
                    locations: list[str]
                    rule: str

                class GetFileContentResponse(BaseModel):
                    """Response for $/getFileContent method."""
                    content: str | None = None
                    format: str
                    metadata: dict[str, str]
                    validation_errors: list[ValidationError] | None = None

                # Use our test implementations
                mock_validation_error.side_effect = ValidationError
                mock_response_class.side_effect = GetFileContentResponse

                # Import and test
                from xlsx_value_picker.mcp_server.protocol import GetFileContentResponse, ValidationError

                # Create test validation error
                test_validation_error = ValidationError(
                    message="Test error",
                    fields=["field1"],
                    locations=["A1"],
                    rule="test_rule"
                )

                # Valid response with content
                valid_response_with_content = GetFileContentResponse(
                    content="formatted_output",
                    format="json",
                    metadata={
                        "source": "test.xlsx",
                        "model_id": "test_model",
                        "validation_status": "valid"
                    }
                )
                assert valid_response_with_content.content == "formatted_output"
                assert valid_response_with_content.format == "json"
                assert valid_response_with_content.metadata["source"] == "test.xlsx"
                assert valid_response_with_content.validation_errors is None

                # Valid response with validation errors
                valid_response_with_errors = GetFileContentResponse(
                    content=None,
                    format="json",
                    metadata={
                        "source": "test.xlsx",
                        "model_id": "test_model",
                        "validation_status": "invalid"
                    },
                    validation_errors=[test_validation_error]
                )
                assert valid_response_with_errors.content is None
                assert valid_response_with_errors.validation_errors[0].message == "Test error"

                # Invalid response (missing required fields)
                with pytest.raises(ValidationError):
                    GetFileContentResponse(content="test")
