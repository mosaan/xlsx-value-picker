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
        list_tools_result = await client.list_tools()

        # Check if the server has tools and specific tools are available
        assert len(list_tools_result) > 0
        tool_names = [tool.name for tool in list_tools_result]
        assert "listModels" in tool_names
        # assert "getModelInfo" in tool_names
        # assert "getDiagnostics" in tool_names
        # assert "getFileContent" in tool_names

        # try to call a tool and check the result
        print(await client.call_tool("listModels"))
