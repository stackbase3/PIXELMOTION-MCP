"""
Unit tests for PixelMotion FastMCP Server
Verifies tool registration, schema generation, JSON-RPC handling, and execution.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from pixelmotion.server.mcp_server import mcp


def test_mcp_tool_registration():
    tools = mcp.list_tools()
    tool_names = [t["name"] for t in tools]
    print(f"Registered MCP tools count: {len(tool_names)}")

    expected_tools = [
        "reference_import", "reference_analyze", "reference_detect_regions", "reference_extract_asset", "reference_compare",
        "ui_reconstruct", "ui_validate", "ui_capture_state",
        "motion_generate_plan", "motion_generate_camera_path", "motion_generate_cursor_path", "motion_generate_3d_composition", "motion_validate",
        "scene_create", "scene_update", "scene_preview", "scene_validate",
        "audio_analyze_beats", "audio_align_events",
        "render_preview", "render_final", "render_status", "render_cancel",
        "export_video", "export_project", "export_assets"
    ]

    for expected in expected_tools:
        assert expected in tool_names or expected.replace("_", ".") in tool_names, f"Tool '{expected}' missing from MCP server!"
    print("  ✓ All required MCP tools verified and listed in schema.")


def test_mcp_jsonrpc_call():
    async def _run():
        # Test Initialize message
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"}
        }
        res = await mcp.handle_jsonrpc_message(init_msg)
        assert res["result"]["serverInfo"]["name"] == "pixelmotion"
        print("  ✓ MCP initialize handshake passed.")

        # Test Tools list message
        list_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        res_list = await mcp.handle_jsonrpc_message(list_msg)
        assert len(res_list["result"]["tools"]) >= 24
        print(f"  ✓ tools/list returned {len(res_list['result']['tools'])} tool schemas.")

        # Test Tools call message (reference_analyze)
        asset_img = root_dir / "pixelmotion/data/test_assets/trading_journal_dashboard.png"
        call_msg = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "reference_analyze",
                "arguments": {"file_path": str(asset_img)}
            }
        }
        call_res = await mcp.handle_jsonrpc_message(call_msg)
        assert not call_res["result"]["isError"], f"Tool call error: {call_res}"
        print("  ✓ tools/call (reference_analyze) executed successfully.")

    asyncio.run(_run())


if __name__ == "__main__":
    print("\n--- Running MCP Server Unit Tests ---")
    test_mcp_tool_registration()
    test_mcp_jsonrpc_call()
    print("All MCP Server unit tests passed!\n")
