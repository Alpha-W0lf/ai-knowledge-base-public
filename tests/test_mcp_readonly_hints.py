"""Public MCP tools advertise readOnlyHint; write tools stay off the public profile.

Checked over the MCP protocol (in-process client), so this is what a client sees.
"""

from __future__ import annotations

import asyncio
import importlib

import pytest
from mcp import Client

import src.mcp_server as mcp_mod


def _listed_tools(monkeypatch, private: bool) -> dict[str, dict]:
    """tools/list as JSON on the wire, keyed by tool name."""
    if private:
        monkeypatch.setenv("AI_KB_MCP_PRIVATE", "1")
    else:
        monkeypatch.delenv("AI_KB_MCP_PRIVATE", raising=False)
    server = importlib.reload(mcp_mod).mcp

    async def list_tools():
        async with Client(server) as client:
            return await client.list_tools()

    result = asyncio.run(list_tools())
    wire = result.model_dump(mode="json", by_alias=True, exclude_none=True)
    return {tool["name"]: tool for tool in wire["tools"]}


@pytest.fixture(autouse=True)
def _public_profile_after(monkeypatch):
    yield
    monkeypatch.delenv("AI_KB_MCP_PRIVATE", raising=False)
    importlib.reload(mcp_mod)


def test_public_profile_lists_exactly_the_read_only_tools(monkeypatch):
    tools = _listed_tools(monkeypatch, private=False)
    assert set(tools) == {"search", "discover", "get_status", "get_context"}
    assert set(tools) == mcp_mod.PUBLIC_TOOL_ALLOWLIST
    for name, tool in tools.items():
        assert tool["annotations"]["readOnlyHint"] is True, name


def test_private_profile_adds_only_the_mutation_tools(monkeypatch):
    tools = _listed_tools(monkeypatch, private=True)
    assert set(tools) == mcp_mod.PUBLIC_TOOL_ALLOWLIST | mcp_mod.PRIVATE_MUTATION_TOOLS
    for name in mcp_mod.PRIVATE_MUTATION_TOOLS:
        assert tools[name].get("annotations", {}).get("readOnlyHint") is not True, name


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
