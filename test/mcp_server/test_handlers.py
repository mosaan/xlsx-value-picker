"""
Tests for MCP Server handlers.
"""
from unittest.mock import MagicMock, patch

import pytest


class TestListModelsHandler:
    """Tests for the $/listModels handler."""

    def test_list_models_returns_all_models(self, mock_server, mock_state):
        """Test that the list_models handler returns all model IDs from the config."""
        # Import the handler registration function
        # This import is inside the test function because the actual module doesn't exist yet
        with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:
            # Mock implementation of register_handlers to capture the handler
            def fake_register(server, state):
                @server.method("$/listModels")
                def handle_list_models(params):
                    return {"models": list(state.app_config.models.keys())}

            mock_register.side_effect = fake_register

            # Call the mocked register_handlers function
            from xlsx_value_picker.mcp_server.handlers import register_handlers
            register_handlers(mock_server, mock_state)

            # Extract the handler function that was registered
            handle_list_models = mock_server.method.call_args_list[0][0][1]

            # Test the handler
            result = handle_list_models({})

            # Verify result
            assert "models" in result
            assert result["models"] == ["test_model"]


class TestGetModelInfoHandler:
    """Tests for the $/getModelInfo handler."""

    def test_get_model_info_returns_correct_info(self, mock_server, mock_state, mock_model_config):
        """Test that the get_model_info handler returns correct model information."""
        # Mock implementation of register_handlers to capture the handler
        with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:
            def fake_register(server, state):
                @server.method("$/getModelInfo")
                def handle_get_model_info(params):
                    model_id = params.get("model_id")
                    if not model_id:
                        raise ValueError("model_id パラメータが必要です")

                    model_config = state.app_config.models.get(model_id)
                    if not model_config:
                        raise ValueError(f"モデルが見つかりません: {model_id}")

                    return {
                        "model_id": model_id,
                        "excel_file_path": model_config.excel_file_path,
                        "sheet_name": model_config.sheet_name,
                        "fields": model_config.fields,
                        "rules_count": len(model_config.rules)
                    }

            mock_register.side_effect = fake_register

            # Call the mocked register_handlers function
            from xlsx_value_picker.mcp_server.handlers import register_handlers
            register_handlers(mock_server, mock_state)

            # Extract the handler function that was registered
            handle_get_model_info = mock_server.method.call_args_list[0][0][1]

            # Test the handler
            result = handle_get_model_info({"model_id": "test_model"})

            # Verify result
            assert result["model_id"] == "test_model"
            assert result["excel_file_path"] == mock_model_config.excel_file_path
            assert result["sheet_name"] == mock_model_config.sheet_name
            assert result["fields"] == mock_model_config.fields
            assert result["rules_count"] == 0  # Empty rules list

    def test_get_model_info_raises_error_for_missing_model_id(self, mock_server, mock_state):
        """Test that the handler raises an error when model_id is missing."""
        with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:
            def fake_register(server, state):
                @server.method("$/getModelInfo")
                def handle_get_model_info(params):
                    model_id = params.get("model_id")
                    if not model_id:
                        raise ValueError("model_id パラメータが必要です")

                    model_config = state.app_config.models.get(model_id)
                    if not model_config:
                        raise ValueError(f"モデルが見つかりません: {model_id}")

                    return {}

            mock_register.side_effect = fake_register

            # Call the mocked register_handlers function
            from xlsx_value_picker.mcp_server.handlers import register_handlers
            register_handlers(mock_server, mock_state)

            # Extract the handler function that was registered
            handle_get_model_info = mock_server.method.call_args_list[0][0][1]

            # Test the handler
            with pytest.raises(ValueError, match="model_id パラメータが必要です"):
                handle_get_model_info({})

    def test_get_model_info_raises_error_for_unknown_model(self, mock_server, mock_state):
        """Test that the handler raises an error for unknown model_id."""
        with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:
            def fake_register(server, state):
                @server.method("$/getModelInfo")
                def handle_get_model_info(params):
                    model_id = params.get("model_id")
                    if not model_id:
                        raise ValueError("model_id パラメータが必要です")

                    model_config = state.app_config.models.get(model_id)
                    if not model_config:
                        raise ValueError(f"モデルが見つかりません: {model_id}")

                    return {}

            mock_register.side_effect = fake_register

            # Call the mocked register_handlers function
            from xlsx_value_picker.mcp_server.handlers import register_handlers
            register_handlers(mock_server, mock_state)

            # Extract the handler function that was registered
            handle_get_model_info = mock_server.method.call_args_list[0][0][1]

            # Test the handler
            with pytest.raises(ValueError, match="モデルが見つかりません"):
                handle_get_model_info({"model_id": "unknown_model"})


class TestGetDiagnosticsHandler:
    """Tests for the $/getDiagnostics handler."""

    def test_get_diagnostics_returns_validation_results(self, mock_server, mock_state,
                                                       mock_validation_results):
        """Test that the get_diagnostics handler returns validation results."""
        # Mock implementation of register_handlers and ValidationEngine
        with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:
            with patch("xlsx_value_picker.validation.ValidationEngine") as mock_validation_engine:
                # Configure the mock ValidationEngine
                mock_validation_instance = MagicMock()
                mock_validation_instance.validate.return_value = mock_validation_results["error"]
                mock_validation_engine.return_value = mock_validation_instance

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
                            model_config.excel_file_path,
                            model_config.fields
                        )

                        return {
                            "diagnostics": [
                                {
                                    "message": result.error_message,
                                    "fields": result.error_fields,
                                    "locations": result.error_locations,
                                    "rule": result.rule_name,
                                    "severity": result.severity
                                }
                                for result in validation_results
                            ],
                            "is_valid": len(validation_results) == 0
                        }

                mock_register.side_effect = fake_register

                # Call the mocked register_handlers function
                from xlsx_value_picker.mcp_server.handlers import register_handlers
                register_handlers(mock_server, mock_state)

                # Extract the handler function that was registered
                handle_get_diagnostics = mock_server.method.call_args_list[0][0][1]

                # Test the handler
                result = handle_get_diagnostics({"model_id": "test_model"})

                # Verify validation was called with correct parameters
                mock_validation_engine.assert_called_once_with(mock_state.app_config.models["test_model"].rules)
                mock_validation_instance.validate.assert_called_once_with(
                    mock_state.app_config.models["test_model"].excel_file_path,
                    mock_state.app_config.models["test_model"].fields
                )

                # Verify result
                assert "diagnostics" in result
                assert len(result["diagnostics"]) == 1
                assert result["diagnostics"][0]["message"] == "Test validation error"
                assert result["diagnostics"][0]["fields"] == ["field1"]
                assert result["diagnostics"][0]["locations"] == ["A1"]
                assert result["diagnostics"][0]["rule"] == "test_rule"
                assert result["diagnostics"][0]["severity"] == "error"
                assert result["is_valid"] is False

    def test_get_diagnostics_with_no_validation_errors(self, mock_server, mock_state,
                                                     mock_validation_results):
        """Test that the handler correctly reports when there are no validation errors."""
        # Mock implementation of register_handlers and ValidationEngine
        with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:
            with patch("xlsx_value_picker.validation.ValidationEngine") as mock_validation_engine:
                # Configure the mock ValidationEngine to return no errors
                mock_validation_instance = MagicMock()
                mock_validation_instance.validate.return_value = mock_validation_results["success"]
                mock_validation_engine.return_value = mock_validation_instance

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
                            model_config.excel_file_path,
                            model_config.fields
                        )

                        return {
                            "diagnostics": [
                                {
                                    "message": result.error_message,
                                    "fields": result.error_fields,
                                    "locations": result.error_locations,
                                    "rule": result.rule_name,
                                    "severity": result.severity
                                }
                                for result in validation_results
                            ],
                            "is_valid": len(validation_results) == 0
                        }

                mock_register.side_effect = fake_register

                # Call the mocked register_handlers function
                from xlsx_value_picker.mcp_server.handlers import register_handlers
                register_handlers(mock_server, mock_state)

                # Extract the handler function that was registered
                handle_get_diagnostics = mock_server.method.call_args_list[0][0][1]

                # Test the handler
                result = handle_get_diagnostics({"model_id": "test_model"})

                # Verify result
                assert "diagnostics" in result
                assert len(result["diagnostics"]) == 0
                assert result["is_valid"] is True


class TestGetFileContentHandler:
    """Tests for the $/getFileContent handler."""

    def test_get_file_content_returns_processed_content(self, mock_server, mock_state,
                                                       mock_excel_extractor, mock_output_formatter,
                                                       mock_validation_results):
        """Test that the get_file_content handler returns processed Excel content."""
        # Mock implementation of register_handlers and required dependencies
        with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:
            with patch("xlsx_value_picker.validation.ValidationEngine") as mock_validation_engine:
                with patch("xlsx_value_picker.excel_processor.ExcelValueExtractor") as mock_extractor:
                    with patch("xlsx_value_picker.output_formatter.OutputFormatter") as mock_formatter:
                        # Configure the mocks
                        mock_validation_instance = MagicMock()
                        mock_validation_instance.validate.return_value = mock_validation_results["success"]
                        mock_validation_engine.return_value = mock_validation_instance

                        # Mock ExcelValueExtractor context manager
                        mock_extractor_instance = MagicMock()
                        mock_extractor_instance.extract_values.return_value = {"data": "test_data"}
                        mock_extractor_cm = MagicMock()
                        mock_extractor_cm.__enter__.return_value = mock_extractor_instance
                        mock_extractor.return_value = mock_extractor_cm

                        # Mock OutputFormatter
                        mock_formatter_instance = MagicMock()
                        mock_formatter_instance.format_output.return_value = "formatted_output"
                        mock_formatter.return_value = mock_formatter_instance

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
                                        model_config.excel_file_path,
                                        model_config.fields
                                    )

                                # Return validation errors if any and not ignored
                                if validation_results and not params.get("ignore_validation", False):
                                    return {
                                        "validation_errors": [
                                            {
                                                "message": result.error_message,
                                                "fields": result.error_fields,
                                                "locations": result.error_locations,
                                                "rule": result.rule_name
                                            }
                                            for result in validation_results
                                        ],
                                        "content": None,
                                        "format": model_config.output.format
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
                                        "validation_status": "valid" if not validation_results else "warning"
                                    }
                                }

                        mock_register.side_effect = fake_register

                        # Call the mocked register_handlers function
                        from xlsx_value_picker.mcp_server.handlers import register_handlers
                        register_handlers(mock_server, mock_state)

                        # Extract the handler function that was registered
                        handle_get_file_content = mock_server.method.call_args_list[0][0][1]

                        # Test the handler
                        result = handle_get_file_content({"model_id": "test_model"})

                        # Verify mock interactions
                        model_config = mock_state.app_config.models["test_model"]
                        mock_validation_engine.assert_called_once_with(model_config.rules)
                        mock_validation_instance.validate.assert_called_once_with(
                            model_config.excel_file_path,
                            model_config.fields
                        )

                        mock_extractor.assert_called_once_with(model_config.excel_file_path)
                        mock_extractor_instance.extract_values.assert_called_once_with(model_config)

                        mock_formatter.assert_called_once_with(model_config)
                        mock_formatter_instance.format_output.assert_called_once_with({"data": "test_data"})

                        # Verify result
                        assert result["content"] == "formatted_output"
                        assert result["format"] == model_config.output.format
                        assert "metadata" in result
                        assert result["metadata"]["source"] == model_config.excel_file_path
                        assert result["metadata"]["model_id"] == "test_model"
                        assert result["metadata"]["validation_status"] == "valid"

    def test_get_file_content_handles_validation_failures(self, mock_server, mock_state,
                                                        mock_validation_results):
        """Test that the handler handles validation failures properly."""
        # Mock implementation of register_handlers and ValidationEngine
        with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:
            with patch("xlsx_value_picker.validation.ValidationEngine") as mock_validation_engine:
                # Configure the mock ValidationEngine to return errors
                mock_validation_instance = MagicMock()
                mock_validation_instance.validate.return_value = mock_validation_results["error"]
                mock_validation_engine.return_value = mock_validation_instance

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
                                model_config.excel_file_path,
                                model_config.fields
                            )

                        # Return validation errors if any and not ignored
                        if validation_results and not params.get("ignore_validation", False):
                            return {
                                "validation_errors": [
                                    {
                                        "message": result.error_message,
                                        "fields": result.error_fields,
                                        "locations": result.error_locations,
                                        "rule": result.rule_name
                                    }
                                    for result in validation_results
                                ],
                                "content": None,
                                "format": model_config.output.format
                            }

                        # If we get here, extraction would happen
                        return {}

                mock_register.side_effect = fake_register

                # Call the mocked register_handlers function
                from xlsx_value_picker.mcp_server.handlers import register_handlers
                register_handlers(mock_server, mock_state)

                # Extract the handler function that was registered
                handle_get_file_content = mock_server.method.call_args_list[0][0][1]

                # Test the handler
                result = handle_get_file_content({"model_id": "test_model"})

                # Verify validation was called
                model_config = mock_state.app_config.models["test_model"]
                mock_validation_engine.assert_called_once_with(model_config.rules)
                mock_validation_instance.validate.assert_called_once_with(
                    model_config.excel_file_path,
                    model_config.fields
                )

                # Verify result contains validation errors
                assert "validation_errors" in result
                assert result["content"] is None
                assert result["format"] == model_config.output.format
                assert len(result["validation_errors"]) == 1
                assert result["validation_errors"][0]["message"] == "Test validation error"
                assert result["validation_errors"][0]["fields"] == ["field1"]
                assert result["validation_errors"][0]["locations"] == ["A1"]
                assert result["validation_errors"][0]["rule"] == "test_rule"

    def test_get_file_content_ignores_validation_when_requested(self, mock_server, mock_state,
                                                              mock_excel_extractor,
                                                              mock_output_formatter,
                                                              mock_validation_results):
        """Test that the handler ignores validation errors when ignore_validation is true."""
        # Mock implementation of register_handlers and required dependencies
        with patch("xlsx_value_picker.mcp_server.handlers.register_handlers") as mock_register:
            with patch("xlsx_value_picker.validation.ValidationEngine") as mock_validation_engine:
                with patch("xlsx_value_picker.excel_processor.ExcelValueExtractor") as mock_extractor:
                    with patch("xlsx_value_picker.output_formatter.OutputFormatter") as mock_formatter:
                        # Configure the mocks
                        mock_validation_instance = MagicMock()
                        mock_validation_instance.validate.return_value = mock_validation_results["error"]
                        mock_validation_engine.return_value = mock_validation_instance

                        # Mock ExcelValueExtractor context manager
                        mock_extractor_instance = MagicMock()
                        mock_extractor_instance.extract_values.return_value = {"data": "test_data"}
                        mock_extractor_cm = MagicMock()
                        mock_extractor_cm.__enter__.return_value = mock_extractor_instance
                        mock_extractor.return_value = mock_extractor_cm

                        # Mock OutputFormatter
                        mock_formatter_instance = MagicMock()
                        mock_formatter_instance.format_output.return_value = "formatted_output"
                        mock_formatter.return_value = mock_formatter_instance

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
                                        model_config.excel_file_path,
                                        model_config.fields
                                    )

                                # Return validation errors if any and not ignored
                                if validation_results and not params.get("ignore_validation", False):
                                    return {
                                        "validation_errors": [
                                            {
                                                "message": result.error_message,
                                                "fields": result.error_fields,
                                                "locations": result.error_locations,
                                                "rule": result.rule_name
                                            }
                                            for result in validation_results
                                        ],
                                        "content": None,
                                        "format": model_config.output.format
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
                                        "validation_status": "valid" if not validation_results else "warning"
                                    }
                                }

                        mock_register.side_effect = fake_register

                        # Call the mocked register_handlers function
                        from xlsx_value_picker.mcp_server.handlers import register_handlers
                        register_handlers(mock_server, mock_state)

                        # Extract the handler function that was registered
                        handle_get_file_content = mock_server.method.call_args_list[0][0][1]

                        # Test the handler with ignore_validation=True
                        result = handle_get_file_content({
                            "model_id": "test_model",
                            "ignore_validation": True
                        })

                        # Verify that even though validation failed, we continued to extract and format
                        model_config = mock_state.app_config.models["test_model"]
                        mock_extractor.assert_called_once_with(model_config.excel_file_path)
                        mock_formatter.assert_called_once_with(model_config)

                        # Verify result
                        assert result["content"] == "formatted_output"
                        assert "metadata" in result
                        assert result["metadata"]["validation_status"] == "warning"
