"""Hub-free: public MCP tools advertise readOnlyHint for mcp-audit dogfood."""

from __future__ import annotations

import os

import src.mcp_server as mcp_mod


def test_public_mcp_tools_advertise_readonly_hint():
    os.environ.pop("AI_KB_MCP_PRIVATE", None)
    import importlib

    importlib.reload(mcp_mod)
    tool_manager = mcp_mod.mcp._tool_manager
    for name in sorted(mcp_mod.PUBLIC_TOOL_ALLOWLIST):
        tool = tool_manager.get_tool(name)
        assert tool is not None, name
        assert tool.annotations is not None, name
        assert tool.annotations.readOnlyHint is True, name


def test_private_mutation_tools_are_not_readonly_on_public_profile():
    os.environ.pop("AI_KB_MCP_PRIVATE", None)
    import importlib

    importlib.reload(mcp_mod)
    registered = set(mcp_mod.mcp._tool_manager._tools)
    assert registered == set(mcp_mod.PUBLIC_TOOL_ALLOWLIST)
    assert "add_channel" not in registered
    assert "sync_now" not in registered


def test_mcp_error_sanitizes_paths():
    """Verify that sanitize_error redacts host filesystem paths."""
    err = "/workspace/data/lancedb/table.lance: file not found"
    sanitized = mcp_mod.sanitize_error(err)
    assert "/workspace" not in sanitized
    assert "[path]" in sanitized

    home_err = "Error at /home/ubuntu/project/file.py line 42"
    sanitized_home = mcp_mod.sanitize_error(home_err)
    assert "/home/ubuntu" not in sanitized_home
    assert "[path]" in sanitized_home
