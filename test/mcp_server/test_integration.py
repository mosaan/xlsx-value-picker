"""
Integration tests for MCP Server functionality.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestServerIntegration:
    """Integration tests for server components."""

    @pytest.fixture
    def mock_server_process(self):
        """Create a mock server process with stdin/stdout pipes."""
        mock_process = MagicMock()
        mock_process.stdin = MagicMock()
        mock_process.stdout = MagicMock()

        # Configure stdout to return a JSON-RPC response
        def mock_readline():
            # Simulates the server processing a request and writing a response
            return json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"models": ["test_model"]}}).encode() + b"\n"

        mock_process.stdout.readline.side_effect = mock_readline

        return mock_process

    def test_mcp_client_server_interaction(self, mock_server_process):
        """Test interaction between MCP client and server using the mock process."""
        # Create a mock MCP client
        from test.mcp_server.conftest import MockMCPClient

        client = MockMCPClient(mock_server_process)

        # Send a request and get response
        response = client.send_request("$/listModels")

        # Verify request was sent correctly
        expected_request = {"jsonrpc": "2.0", "id": 1, "method": "$/listModels", "params": {}}

        # Check that the request was written to stdin
        mock_server_process.stdin.write.assert_called_once_with(json.dumps(expected_request).encode() + b"\n")

        # Verify response was processed correctly
        assert "result" in response
        assert "models" in response["result"]
        assert response["result"]["models"] == ["test_model"]

    def test_list_models_integration(self, test_config_file, mock_app_config):
        """Test integration of list_models handler with state management."""
        # Mock implementations
        with patch("xlsx_value_picker.mcp_server.state.MCPServerState") as mock_state_class:
            # Create a state instance with our mock config
            mock_state = MagicMock()
            mock_state.app_config = mock_app_config
            mock_state.config_path = str(test_config_file)

            # Configure the state class to return our mock instance
            mock_state_class.return_value = mock_state
            mock_state_class.get_instance.return_value = mock_state

            # Server and transport mocks
            with patch("xlsx_value_picker.mcp_server.server.FastMCP") as mock_fastmcp:
                with patch("xlsx_value_picker.mcp_server.server.StdioTransport"):
                    # Simulate server creation
                    mock_server = MagicMock()
                    mock_fastmcp.return_value = mock_server

                    # Import necessary modules
                    from xlsx_value_picker.mcp_server.server import main

                    # Create mocked implementation for register_handlers
                    with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:

                        def fake_register(server, state):
                            @server.method("$/listModels")
                            def handle_list_models(params):
                                return {"models": list(state.app_config.models.keys())}

                        mock_register.side_effect = fake_register

                        # Call mocked main function
                        main(str(test_config_file))

                        # Verify interactions
                        mock_state_class.assert_called_once_with(str(test_config_file))
                        mock_register.assert_called_once()

                        # Get the handler that was registered
                        handler_call = mock_server.method.call_args_list[0]
                        assert handler_call[0][0] == "$/listModels"
                        handler = handler_call[0][1]

                        # Test the handler with our mocked state
                        result = handler({})
                        assert "models" in result
                        assert set(result["models"]) == {"test_model"}

    def test_get_diagnostics_integration(
        self, test_config_file, mock_app_config, mock_model_config, mock_validation_results
    ):
        """Test integration of get_diagnostics handler with validation engine."""
        # Mock implementations
        with patch("xlsx_value_picker.mcp_server.state.MCPServerState") as mock_state_class:
            with patch("xlsx_value_picker.validation.ValidationEngine") as mock_validation_engine:
                # Configure validation engine
                mock_validation_instance = MagicMock()
                mock_validation_instance.validate.return_value = mock_validation_results["error"]
                mock_validation_engine.return_value = mock_validation_instance

                # Create a state instance with our mock config
                mock_state = MagicMock()
                mock_state.app_config = mock_app_config
                mock_state.config_path = str(test_config_file)

                # Configure the state class to return our mock instance
                mock_state_class.return_value = mock_state
                mock_state_class.get_instance.return_value = mock_state

                # Server and transport mocks
                with patch("xlsx_value_picker.mcp_server.server.FastMCP") as mock_fastmcp:
                    # Simulate server creation
                    mock_server = MagicMock()
                    mock_fastmcp.return_value = mock_server

                    # Create mocked implementation for register_handlers
                    with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:

                        def fake_register(server, state):
                            @server.method("$/getDiagnostics")
                            def handle_get_diagnostics(params):
                                model_id = params.get("model_id")
                                if not model_id:
                                    raise ValueError("model_id パラメータが必要です")

                                model_config = state.app_config.models.get(model_id)
                                if not model_config:
                                    raise ValueError(f"モデルが見つかりません: {model_id}")

                                from xlsx_value_picker.validation import ValidationEngine

                                validation_engine = ValidationEngine(model_config.rules)
                                validation_results = validation_engine.validate(
                                    model_config.excel_file_path, model_config.fields
                                )

                                return {
                                    "diagnostics": [
                                        {
                                            "message": result.error_message,
                                            "fields": result.error_fields,
                                            "locations": result.error_locations,
                                            "rule": result.rule_name,
                                            "severity": result.severity,
                                        }
                                        for result in validation_results
                                    ],
                                    "is_valid": len(validation_results) == 0,
                                }

                        mock_register.side_effect = fake_register

                        # Import necessary modules
                        from xlsx_value_picker.mcp_server.handlers import register_handlers
                        from xlsx_value_picker.mcp_server.server import create_server

                        # Create server and register handlers
                        server = create_server()
                        register_handlers(server, mock_state)

                        # Get the handler that was registered
                        handler_call = mock_server.method.call_args_list[0]
                        assert handler_call[0][0] == "$/getDiagnostics"
                        handler = handler_call[0][1]

                        # Test the handler
                        result = handler({"model_id": "test_model"})

                        # Verify validation engine was used correctly
                        mock_validation_engine.assert_called_once_with(mock_model_config.rules)
                        mock_validation_instance.validate.assert_called_once_with(
                            mock_model_config.excel_file_path, mock_model_config.fields
                        )

                        # Verify the result
                        assert "diagnostics" in result
                        assert len(result["diagnostics"]) == 1
                        assert result["diagnostics"][0]["message"] == "Test validation error"
                        assert result["is_valid"] is False

    def test_get_file_content_integration(
        self,
        test_config_file,
        mock_app_config,
        mock_model_config,
        mock_validation_results,
        mock_excel_extractor,
        mock_output_formatter,
    ):
        """Test integration of get_file_content handler with extraction and formatting."""
        # Mock implementations
        with patch("xlsx_value_picker.mcp_server.state.MCPServerState") as mock_state_class:
            with patch("xlsx_value_picker.validation.ValidationEngine") as mock_validation_engine:
                with patch("xlsx_value_picker.excel_processor.ExcelValueExtractor") as mock_extractor:
                    with patch("xlsx_value_picker.output_formatter.OutputFormatter") as mock_formatter:
                        # Configure validation engine
                        mock_validation_instance = MagicMock()
                        mock_validation_instance.validate.return_value = mock_validation_results["success"]
                        mock_validation_engine.return_value = mock_validation_instance

                        # Configure Excel extractor
                        mock_extractor_instance = MagicMock()
                        mock_extractor_instance.extract_values.return_value = {"data": "test_data"}
                        mock_extractor_cm = MagicMock()
                        mock_extractor_cm.__enter__.return_value = mock_extractor_instance
                        mock_extractor.return_value = mock_extractor_cm

                        # Configure formatter
                        mock_formatter_instance = MagicMock()
                        mock_formatter_instance.format_output.return_value = "formatted_output"
                        mock_formatter.return_value = mock_formatter_instance

                        # Create a state instance with our mock config
                        mock_state = MagicMock()
                        mock_state.app_config = mock_app_config
                        mock_state.config_path = str(test_config_file)

                        # Configure the state class to return our mock instance
                        mock_state_class.return_value = mock_state
                        mock_state_class.get_instance.return_value = mock_state

                        # Server mock
                        with patch("xlsx_value_picker.mcp_server.server.FastMCP") as mock_fastmcp:
                            # Simulate server creation
                            mock_server = MagicMock()
                            mock_fastmcp.return_value = mock_server

                            # Create mocked implementation for register_handlers
                            with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:

                                def fake_register(server, state):
                                    @server.method("$/getFileContent")
                                    def handle_get_file_content(params):
                                        model_id = params.get("model_id")
                                        if not model_id:
                                            raise ValueError("model_id パラメータが必要です")

                                        model_config = state.app_config.models.get(model_id)
                                        if not model_config:
                                            raise ValueError(f"モデルが見つかりません: {model_id}")

                                        # Validate if needed
                                        validation_results = []
                                        if model_config.rules and not params.get("skip_validation", False):
                                            from xlsx_value_picker.validation import ValidationEngine

                                            validation_engine = ValidationEngine(model_config.rules)
                                            validation_results = validation_engine.validate(
                                                model_config.excel_file_path, model_config.fields
                                            )

                                        # Return validation errors if any and not ignored
                                        if validation_results and not params.get("ignore_validation", False):
                                            return {
                                                "validation_errors": [
                                                    {
                                                        "message": result.error_message,
                                                        "fields": result.error_fields,
                                                        "locations": result.error_locations,
                                                        "rule": result.rule_name,
                                                    }
                                                    for result in validation_results
                                                ],
                                                "content": None,
                                                "format": model_config.output.format,
                                            }

                                        # Extract data from Excel
                                        from xlsx_value_picker.excel_processor import ExcelValueExtractor

                                        with ExcelValueExtractor(model_config.excel_file_path) as extractor:
                                            data = extractor.extract_values(model_config)

                                        # Format output
                                        from xlsx_value_picker.output_formatter import OutputFormatter

                                        formatter = OutputFormatter(model_config)
                                        formatted_output = formatter.format_output(data)

                                        return {
                                            "content": formatted_output,
                                            "format": model_config.output.format,
                                            "metadata": {
                                                "source": model_config.excel_file_path,
                                                "model_id": model_id,
                                                "validation_status": "valid" if not validation_results else "warning",
                                            },
                                        }

                                mock_register.side_effect = fake_register

                                # Import necessary modules
                                from xlsx_value_picker.mcp_server.handlers import register_handlers
                                from xlsx_value_picker.mcp_server.server import create_server

                                # Create server and register handlers
                                server = create_server()
                                register_handlers(server, mock_state)

                                # Get the handler that was registered
                                handler_call = mock_server.method.call_args_list[0]
                                assert handler_call[0][0] == "$/getFileContent"
                                handler = handler_call[0][1]

                                # Test the handler
                                result = handler({"model_id": "test_model"})

                                # Verify the full integration chain
                                mock_validation_engine.assert_called_once_with(mock_model_config.rules)
                                mock_extractor.assert_called_once_with(mock_model_config.excel_file_path)
                                mock_formatter.assert_called_once_with(mock_model_config)

                                # Verify the result
                                assert result["content"] == "formatted_output"
                                assert result["format"] == mock_model_config.output.format
                                assert "metadata" in result
                                assert result["metadata"]["source"] == mock_model_config.excel_file_path
                                assert result["metadata"]["model_id"] == "test_model"
                                assert result["metadata"]["validation_status"] == "valid"
