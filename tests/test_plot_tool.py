"""Tests for plot_tool."""
import pytest

from harness.tools.plot_tool import plot_tool


@pytest.mark.asyncio
async def test_plot_tool_sin():
    """Test that plot_tool generates a base64-encoded PNG."""
    result = await plot_tool("np.sin(x)", title="Sine Wave")
    assert result.startswith("data:image/png;base64,")
    # Base64 data should be reasonably large for a plot
    assert len(result) > 1000