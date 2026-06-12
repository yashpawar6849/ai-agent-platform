"""Tests for file_tools."""
from __future__ import annotations

import pytest
from pathlib import Path

from harness.tools.file_tools import (
    SANDBOX_ROOT,
    read_file,
    write_file,
    _resolve_and_validate,
)


@pytest.mark.asyncio
async def test_write_and_read_roundtrip():
    test_path = "test_roundtrip.txt"
    content = "Hello, world!"

    write_result = await write_file(test_path, content)
    assert write_result == f"Wrote {len(content)} bytes to {test_path}"

    read_result = await read_file(test_path)
    assert read_result == content

    # Cleanup
    (SANDBOX_ROOT / test_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_nonexistent_file_error():
    result = await read_file("nonexistent_file_12345.txt")
    assert result.startswith("Error:")
    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_path_traversal_rejected():
    # Attempt path traversal with absolute path
    result = await write_file("/etc/passwd", "malicious content")
    assert result.startswith("Error:")
    assert "Path traversal" in result

    # Attempt path traversal with ..
    result = await read_file("../../../etc/passwd")
    assert result.startswith("Error:")
    assert "Path traversal" in result


@pytest.mark.asyncio
async def test_nested_directory():
    """Test that files can be written and read in nested directories."""
    test_path = "subdir/nested/file.txt"
    content = "Nested file content"

    write_result = await write_file(test_path, content)
    assert "bytes" in write_result

    read_result = await read_file(test_path)
    assert read_result == content

    # Cleanup
    import shutil
    shutil.rmtree(SANDBOX_ROOT / "subdir", ignore_errors=True)


@pytest.mark.asyncio
async def test_overwrite_file():
    """Test that writing to an existing file overwrites it."""
    test_path = "overwrite_test.txt"

    await write_file(test_path, "original")
    await write_file(test_path, "modified")

    result = await read_file(test_path)
    assert result == "modified"

    # Cleanup
    (SANDBOX_ROOT / test_path).unlink(missing_ok=True)


def test_resolve_and_validate_valid():
    """Test that valid paths resolve correctly."""
    resolved = _resolve_and_validate("some/path/file.txt")
    assert str(resolved).startswith(str(SANDBOX_ROOT))


def test_resolve_and_validate_traversal():
    """Test that path traversal raises ValueError."""
    with pytest.raises(ValueError, match="Path traversal detected"):
        _resolve_and_validate("../../../etc/passwd")

    with pytest.raises(ValueError):
        _resolve_and_validate("/etc/passwd")


@pytest.mark.asyncio
async def test_write_empty_file():
    """Test writing an empty file."""
    test_path = "empty_file.txt"
    write_result = await write_file(test_path, "")
    assert write_result == "Wrote 0 bytes to empty_file.txt"

    read_result = await read_file(test_path)
    assert read_result == ""

    # Cleanup
    (SANDBOX_ROOT / test_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_write_binary_content():
    """Test writing content that looks binary."""
    test_path = "binary_file.txt"
    content = "\x00\x01\x02\x03binary"
    write_result = await write_file(test_path, content)
    assert "bytes" in write_result

    read_result = await read_file(test_path)
    assert read_result == content

    # Cleanup
    (SANDBOX_ROOT / test_path).unlink(missing_ok=True)