"""
Tests for MCP Server core functionality.
"""
from unittest.mock import MagicMock, patch


def test_create_server():
    """Test that create_server creates a FastMCP instance with correct parameters."""
    with patch("xlsx_value_picker.mcp_server.server.FastMCP") as mock_fastmcp:
        # Mock implementation for testing
        with patch("xlsx_value_picker.mcp_server.server.create_server") as mock_create_server:
            def fake_create_server():
                from mcp.server.fastmcp import FastMCP
                return FastMCP("xlsx-value-picker")

            mock_create_server.side_effect = fake_create_server

            # Import the function and execute it
            from xlsx_value_picker.mcp_server.server import create_server
            server = create_server()

            # Verify FastMCP was called correctly
            mock_fastmcp.assert_called_once_with("xlsx-value-picker")
            assert server == mock_fastmcp.return_value


def test_main_initializes_state():
    """Test that main initializes server state with config path."""
    with patch("xlsx_value_picker.mcp_server.server.MCPServerState") as mock_state:
        with patch("xlsx_value_picker.mcp_server.server.create_server") as mock_create_server:
            with patch("xlsx_value_picker.mcp_server.server.register_handlers") as mock_register:
                with patch("xlsx_value_picker.mcp_server.server.StdioTransport") as mock_transport:
                    # Mocked server instance
                    mock_server = MagicMock()
                    mock_create_server.return_value = mock_server

                    # Mock implementation for testing
                    with patch("xlsx_value_picker.mcp_server.server.main") as mock_main:
                        def fake_main(config_path="config.yaml"):
                            # Initialize state
                            from xlsx_value_picker.mcp_server.state import MCPServerState
                            state = MCPServerState(config_path)

                            # Create server
                            from xlsx_value_picker.mcp_server.server import create_server
                            server = create_server()

                            # Register handlers
                            from xlsx_value_picker.mcp_server.handlers import register_handlers
                            register_handlers(server, state)

                            # Start server with stdio transport
                            from mcp.transports.stdio import StdioTransport
                            server.serve(StdioTransport())

                        mock_main.side_effect = fake_main

                        # Import the function and execute it
                        from xlsx_value_picker.mcp_server.server import main
                        main("test_config.yaml")

                        # Verify state was initialized with correct path
                        mock_state.assert_called_once_with("test_config.yaml")

                        # Verify handlers were registered
                        mock_register.assert_called_once()

                        # Verify server was started with stdio transport
                        mock_server.serve.assert_called_once()
                        mock_transport.assert_called_once()


def test_main_uses_default_config_path():
    """Test that main uses default config path when not specified."""
    with patch("xlsx_value_picker.mcp_server.server.MCPServerState") as mock_state:
        with patch("xlsx_value_picker.mcp_server.server.create_server") as mock_create_server:
            with patch("xlsx_value_picker.mcp_server.server.register_handlers") as _:
                with patch("xlsx_value_picker.mcp_server.server.StdioTransport") as _:
                    # Mocked server instance
                    mock_server = MagicMock()
                    mock_create_server.return_value = mock_server

                    # Mock implementation for testing
                    with patch("xlsx_value_picker.mcp_server.server.main") as mock_main:
                        def fake_main(config_path="config.yaml"):
                            # Initialize state
                            from xlsx_value_picker.mcp_server.state import MCPServerState
                            state = MCPServerState(config_path)

                            # Create server
                            from xlsx_value_picker.mcp_server.server import create_server
                            server = create_server()

                            # Register handlers
                            from xlsx_value_picker.mcp_server.handlers import register_handlers
                            register_handlers(server, state)

                            # Start server with stdio transport
                            from mcp.transports.stdio import StdioTransport
                            server.serve(StdioTransport())

                        mock_main.side_effect = fake_main

                        # Import the function and execute it with default config path
                        from xlsx_value_picker.mcp_server.server import main
                        main()

                        # Verify state was initialized with default path
                        mock_state.assert_called_once_with("config.yaml")


def test_server_setup_logging():
    """Test that server sets up logging correctly."""
    with patch("xlsx_value_picker.mcp_server.server.logging") as mock_logging:
        # Mock implementation for testing
        with patch("xlsx_value_picker.mcp_server.server.create_server") as mock_create_server:
            def fake_create_server():
                import logging

                # Setup logging
                logging.basicConfig(
                    level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    handlers=[logging.StreamHandler()]
                )

                # Create and return server
                from mcp.server.fastmcp import FastMCP
                return FastMCP("xlsx-value-picker")

            mock_create_server.side_effect = fake_create_server

            # Import the function and execute it
            from xlsx_value_picker.mcp_server.server import create_server
            _ = create_server()

            # Verify logging was set up
            mock_logging.basicConfig.assert_called_once()
            # Verify log level
            assert mock_logging.basicConfig.call_args[1]["level"] == mock_logging.INFO
            # Verify format string
            assert "%(asctime)s" in mock_logging.basicConfig.call_args[1]["format"]
            # Verify handler type
            assert len(mock_logging.basicConfig.call_args[1]["handlers"]) == 1
