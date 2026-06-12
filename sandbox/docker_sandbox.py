"""Docker-based sandbox for isolated Python code execution."""
from __future__ import annotations

import asyncio
import os
import tempfile
import uuid

from common.models import SandboxResult


class DockerSandbox:
    """Executes Python code inside a temporary Docker container."""

    def __init__(self, image: str = "python:3.12-slim") -> None:
        self.image = image

    async def run_code(
        self,
        code: str,
        timeout: int = 30,
        memory: str = "128m",
        cpus: str = "1.0",
    ) -> SandboxResult:
        """Run *code* in a disposable Docker container.

        Args:
            code: Python source to execute.
            timeout: Maximum seconds to wait for the container.
            memory: Docker memory limit (e.g. "128m", "512m").
            cpus: Docker CPU limit (e.g. "1.0", "0.5").
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as fh:
            fh.write(code)
            script_path = fh.name

        container_name = f"sandbox_{uuid.uuid4().hex[:8]}"
        try:
            cmd = [
                "docker",
                "run",
                "--rm",
                "--name",
                container_name,
                "-v",
                f"{script_path}:/app/script.py:ro",
                "--memory",
                memory,
                "--memory-swap",
                memory,
                "--cpus",
                cpus,
                "--network",
                "none",
                self.image,
                "python",
                "/app/script.py",
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout,
            )
            return SandboxResult(
                stdout=stdout.decode(errors="replace"),
                stderr=stderr.decode(errors="replace"),
                returncode=proc.returncode,
            )
        except asyncio.TimeoutError:
            # Best-effort container cleanup on timeout
            try:
                await asyncio.create_subprocess_exec(
                    "docker",
                    "kill",
                    container_name,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
            except Exception:
                pass
            return SandboxResult(
                stdout="",
                stderr="Execution timed out",
                returncode=-1,
            )
        finally:
            try:
                os.unlink(script_path)
            except OSError:
                pass

    async def run_command(
        self,
        command: list[str],
        timeout: int = 30,
        memory: str = "128m",
        cpus: str = "1.0",
        image: str = "python:3.12-slim",
    ) -> SandboxResult:
        """Run an arbitrary shell command in a disposable Docker container.

        Args:
            command: Command and arguments as a list.
            timeout: Maximum seconds to wait for the container.
            memory: Docker memory limit (e.g. "128m", "512m").
            cpus: Docker CPU limit (e.g. "1.0", "0.5").
            image: Docker image to use.
        """
        container_name = f"sandbox_cmd_{uuid.uuid4().hex[:8]}"
        try:
            cmd = [
                "docker",
                "run",
                "--rm",
                "--name",
                container_name,
                "--memory",
                memory,
                "--memory-swap",
                memory,
                "--cpus",
                cpus,
                "--network",
                "none",
                image,
                *command,
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout,
            )
            return SandboxResult(
                stdout=stdout.decode(errors="replace"),
                stderr=stderr.decode(errors="replace"),
                returncode=proc.returncode,
            )
        except asyncio.TimeoutError:
            # Best-effort container cleanup on timeout
            try:
                await asyncio.create_subprocess_exec(
                    "docker",
                    "kill",
                    container_name,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
            except Exception:
                pass
            return SandboxResult(
                stdout="",
                stderr="Execution timed out",
                returncode=-1,
            )

    async def run_with_output_volume(
        self,
        code: str,
        output_host_dir: str,
        output_container_dir: str = "/output",
        timeout: int = 30,
        memory: str = "128m",
        cpus: str = "1.0",
    ) -> SandboxResult:
        """Run Python code in a disposable Docker container with an output volume.

        Args:
            code: Python source to execute.
            output_host_dir: Host directory to mount for output files.
            output_container_dir: Container directory to mount (default /output).
            timeout: Maximum seconds to wait for the container.
            memory: Docker memory limit (e.g. "128m", "512m").
            cpus: Docker CPU limit (e.g. "1.0", "0.5").
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as fh:
            fh.write(code)
            script_path = fh.name

        container_name = f"sandbox_vol_{uuid.uuid4().hex[:8]}"
        try:
            cmd = [
                "docker",
                "run",
                "--rm",
                "--name",
                container_name,
                "-v",
                f"{script_path}:/app/script.py:ro",
                "-v",
                f"{output_host_dir}:{output_container_dir}",
                "--memory",
                memory,
                "--memory-swap",
                memory,
                "--cpus",
                cpus,
                "--network",
                "none",
                self.image,
                "python",
                "/app/script.py",
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout,
            )
            return SandboxResult(
                stdout=stdout.decode(errors="replace"),
                stderr=stderr.decode(errors="replace"),
                returncode=proc.returncode,
            )
        except asyncio.TimeoutError:
            # Best-effort container cleanup on timeout
            try:
                await asyncio.create_subprocess_exec(
                    "docker",
                    "kill",
                    container_name,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
            except Exception:
                pass
            return SandboxResult(
                stdout="",
                stderr="Execution timed out",
                returncode=-1,
            )
        finally:
            try:
                os.unlink(script_path)
            except OSError:
                pass
