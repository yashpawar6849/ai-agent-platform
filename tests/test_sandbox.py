"""Tests for the Docker sandbox."""
import pytest

from sandbox.docker_sandbox import DockerSandbox


@pytest.mark.asyncio
async def test_sandbox_runs_hello_world():
    sandbox = DockerSandbox()
    result = await sandbox.run_code('print("Hello from sandbox")')
    assert "Hello from sandbox" in result.stdout
    assert result.returncode == 0


@pytest.mark.asyncio
async def test_sandbox_timeout():
    sandbox = DockerSandbox()
    result = await sandbox.run_code("import time; time.sleep(100)", timeout=2)
    assert result.returncode == -1
    assert "timed out" in result.stderr.lower()


@pytest.mark.asyncio
async def test_sandbox_python_error():
    sandbox = DockerSandbox()
    result = await sandbox.run_code("raise ValueError('boom')")
    assert result.returncode != 0
    assert "boom" in result.stderr


@pytest.mark.asyncio
async def test_sandbox_oom():
    """Allocate more memory than the limit and verify the container is killed."""
    sandbox = DockerSandbox()
    # Try to allocate 256MB in a 32m container → should OOM
    code = "a = bytearray(256 * 1024 * 1024); print('done')"
    result = await sandbox.run_code(code, memory="32m", timeout=10)
    assert result.returncode != 0
