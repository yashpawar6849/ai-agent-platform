"""Tests for fetch_tool."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from harness.tools.fetch_tool import fetch_tool


@pytest.mark.asyncio
async def test_fetch_success():
    mock_response = AsyncMock()
    mock_response.text = "Hello, World!" * 1000  # Will be truncated to 5000 chars
    mock_response.raise_for_status = AsyncMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.return_value = mock_response

    with patch("harness.tools.fetch_tool.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_tool("https://example.com")

    # Check that result is the response text (truncated to 5000 chars)
    assert len(result) <= 5000
    assert "Hello, World!" in result


@pytest.mark.asyncio
async def test_fetch_timeout():
    import httpx

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.side_effect = httpx.TimeoutException("Request timed out")

    with patch("harness.tools.fetch_tool.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_tool("https://example.com")

    assert result.startswith("Error:")
    assert "TimeoutException" in result or "timed out" in result


@pytest.mark.asyncio
async def test_fetch_dns_error():
    import httpx

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.side_effect = httpx.ConnectError("Connection failed")

    with patch("harness.tools.fetch_tool.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_tool("https://invalid.example.com")

    assert result.startswith("Error:")
    assert "ConnectError" in result or "Connection" in result


@pytest.mark.asyncio
async def test_fetch_http_error():
    import httpx

    mock_response = AsyncMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", request=AsyncMock(), response=AsyncMock()
    )

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.return_value = mock_response

    with patch("harness.tools.fetch_tool.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_tool("https://example.com/notfound")

    assert result.startswith("Error:")


@pytest.mark.asyncio
async def test_fetch_truncation():
    long_content = "A" * 10000

    mock_response = AsyncMock()
    mock_response.text = long_content
    mock_response.raise_for_status = AsyncMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get.return_value = mock_response

    with patch("harness.tools.fetch_tool.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_tool("https://example.com")

    assert len(result) == 5000