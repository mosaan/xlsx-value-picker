from src.xlsx_value_picker.config_loader import ConfigLoader


def main(config_path: str = "config.yaml"):
    """
    Main entry point for the MCP server.
    """
    try:
        # Load the configuration
        loader = ConfigLoader()
        mcp_config = loader.load_mcp_config(config_path)
        # Configure and start the server
        server = mcp_config.configure()
        server.run()  # Default to stdio transport
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        raise

