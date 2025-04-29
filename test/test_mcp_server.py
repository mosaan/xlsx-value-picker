import pytest
from fastmcp.client import Client

from xlsx_value_picker.config_loader import ConfigLoader

# This is the same as using the @pytest.mark.anyio on all test functions in the module
pytestmark = pytest.mark.anyio

async def test_server_initialization():
    config_path = "test/test_config.yaml"
    loader = ConfigLoader()
    mcp_config = loader.load_mcp_config(config_path)
    server = mcp_config.configure()
    print("DEBUG: Server initialized successfully")
    async with Client(server) as client:
        print(await client.list_tools())
