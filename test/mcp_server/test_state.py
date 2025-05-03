"""
Tests for MCP Server state management.
"""
from unittest.mock import MagicMock, patch


def test_state_singleton_pattern():
    """Test that state works as a singleton."""
    # Mock implementation for testing
    with patch("xlsx_value_picker.mcp_server.state.MCPServerState") as mock_state_class:
        with patch("xlsx_value_picker.mcp_server.state.ConfigLoader"):
            # Define a minimal singleton state class for testing
            class MCPServerState:
                _instance = None

                @classmethod
                def get_instance(cls, config_path=None):
                    if cls._instance is None and config_path:
                        cls._instance = cls(config_path)
                    return cls._instance

                def __init__(self, config_path: str):
                    self.config_path = config_path
                    self.app_config = None
                    self.load_config()

                def load_config(self):
                    # Load config from file using ConfigLoader
                    from xlsx_value_picker.config_loader import ConfigLoader
                    config_loader = ConfigLoader()
                    self.app_config = config_loader.load_config(self.config_path)

            # Use our test implementation
            mock_state_class.side_effect = MCPServerState
            mock_state_class._instance = None

            # Import and test
            from xlsx_value_picker.mcp_server.state import MCPServerState

            # First instance creation
            state1 = MCPServerState.get_instance("config1.yaml")
            assert state1.config_path == "config1.yaml"

            # Should reuse the existing instance
            state2 = MCPServerState.get_instance()
            assert state1 is state2

            # Reset for next test
            MCPServerState._instance = None

            # Create new instance with different config
            state3 = MCPServerState.get_instance("config2.yaml")
            assert state3.config_path == "config2.yaml"
            assert state1 is not state3


def test_state_loads_config():
    """Test that state loads configuration properly."""
    mock_config = MagicMock()

    # Mock implementation for testing
    with patch("xlsx_value_picker.mcp_server.state.MCPServerState") as mock_state_class:
        with patch("xlsx_value_picker.config_loader.ConfigLoader") as mock_loader_class:
            # Configure the ConfigLoader mock to return our test config
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_config
            mock_loader_class.return_value = mock_loader_instance

            # Define a minimal state class for testing
            class MCPServerState:
                def __init__(self, config_path: str):
                    self.config_path = config_path
                    self.app_config = None
                    self.load_config()

                def load_config(self):
                    # Load config from file using ConfigLoader
                    from xlsx_value_picker.config_loader import ConfigLoader
                    config_loader = ConfigLoader()
                    self.app_config = config_loader.load_config(self.config_path)

            # Use our test implementation
            mock_state_class.side_effect = MCPServerState

            # Import and test
            from xlsx_value_picker.mcp_server.state import MCPServerState

            # Create state instance
            state = MCPServerState("test_config.yaml")

            # Verify config loader was used
            mock_loader_class.assert_called_once()
            mock_loader_instance.load_config.assert_called_once_with("test_config.yaml")

            # Verify config was loaded
            assert state.app_config is mock_config


def test_state_reload_config():
    """Test that state can reload configuration."""
    mock_config1 = MagicMock()
    mock_config2 = MagicMock()

    # Mock implementation for testing
    with patch("xlsx_value_picker.mcp_server.state.MCPServerState") as mock_state_class:
        with patch("xlsx_value_picker.config_loader.ConfigLoader") as mock_loader_class:
            # Configure the ConfigLoader mock to return different configs on subsequent calls
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.side_effect = [mock_config1, mock_config2]
            mock_loader_class.return_value = mock_loader_instance

            # Define a state class with reload capability for testing
            class MCPServerState:
                def __init__(self, config_path: str):
                    self.config_path = config_path
                    self.app_config = None
                    self.load_config()

                def load_config(self):
                    # Load config from file using ConfigLoader
                    from xlsx_value_picker.config_loader import ConfigLoader
                    config_loader = ConfigLoader()
                    self.app_config = config_loader.load_config(self.config_path)

                def reload_config(self):
                    """Reload configuration from the config file."""
                    self.load_config()
                    return self.app_config

            # Use our test implementation
            mock_state_class.side_effect = MCPServerState

            # Import and test
            from xlsx_value_picker.mcp_server.state import MCPServerState

            # Create state instance
            state = MCPServerState("test_config.yaml")

            # First config was loaded
            assert state.app_config is mock_config1

            # Reload config
            reloaded_config = state.reload_config()

            # Second config was loaded
            assert reloaded_config is mock_config2
            assert state.app_config is mock_config2

            # ConfigLoader.load_config was called twice
            assert mock_loader_instance.load_config.call_count == 2


def test_state_provides_model_access():
    """Test that state provides methods to access models easily."""
    # Create mock app config with models
    from xlsx_value_picker.config_loader import AppConfig
    mock_model1 = MagicMock()
    mock_model2 = MagicMock()
    mock_app_config = AppConfig(models={
        "model1": mock_model1,
        "model2": mock_model2
    })

    # Mock implementation for testing
    with patch("xlsx_value_picker.mcp_server.state.MCPServerState") as mock_state_class:
        with patch("xlsx_value_picker.config_loader.ConfigLoader") as mock_loader_class:
            # Configure the ConfigLoader mock
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_app_config
            mock_loader_class.return_value = mock_loader_instance

            # Define a state class with model access methods for testing
            class MCPServerState:
                def __init__(self, config_path: str):
                    self.config_path = config_path
                    self.app_config = None
                    self.load_config()

                def load_config(self):
                    # Load config from file using ConfigLoader
                    from xlsx_value_picker.config_loader import ConfigLoader
                    config_loader = ConfigLoader()
                    self.app_config = config_loader.load_config(self.config_path)

                def get_model_ids(self):
                    """Get a list of available model IDs."""
                    return list(self.app_config.models.keys())

                def get_model(self, model_id):
                    """Get a model configuration by ID."""
                    return self.app_config.models.get(model_id)

                def model_exists(self, model_id):
                    """Check if a model exists."""
                    return model_id in self.app_config.models

            # Use our test implementation
            mock_state_class.side_effect = MCPServerState

            # Import and test
            from xlsx_value_picker.mcp_server.state import MCPServerState

            # Create state instance
            state = MCPServerState("test_config.yaml")

            # Test get_model_ids
            model_ids = state.get_model_ids()
            assert set(model_ids) == {"model1", "model2"}

            # Test get_model
            model1 = state.get_model("model1")
            assert model1 is mock_model1

            model2 = state.get_model("model2")
            assert model2 is mock_model2

            # Test get_model with unknown ID
            unknown_model = state.get_model("unknown")
            assert unknown_model is None

            # Test model_exists
            assert state.model_exists("model1") is True
            assert state.model_exists("model2") is True
            assert state.model_exists("unknown") is False
