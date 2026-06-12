"""In-memory dependency stores for the gateway."""
from __future__ import annotations

from typing import Dict

from common.models import Agent, RunResult

agents: Dict[str, Agent] = {}
runs: Dict[str, RunResult] = {}
