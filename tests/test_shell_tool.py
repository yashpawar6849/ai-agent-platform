"""Tests for shell_tool."""
import pytest

from harness.tools.shell_tool import shell_tool


@pytest.mark.asyncio
async def test_shell_tool_echo():
    """Test that shell_tool can run echo and return the output."""
    result = await shell_tool("echo hello")
    assert "hello" in result