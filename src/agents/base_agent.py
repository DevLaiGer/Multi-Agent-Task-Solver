"""Base agent implementations for the Multi-Agent Task Solver."""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models import AgentResult, AgentStatus


class BaseAgent(ABC):
    """Abstract base class providing retry and timeout handling for agents."""

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.agent_id = agent_id
        self.config: Dict[str, Any] = config or {}
        self.retry_count: int = int(self.config.get("retry_count", 3))
        self.timeout_seconds: int = int(self.config.get("timeout_seconds", 30))

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent logic and return a dictionary result."""

    async def run_with_retries(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the agent with retry, timeout, and exponential backoff."""

        start_time = time.perf_counter()
        last_error: Optional[str] = None

        for attempt in range(self.retry_count + 1):
            try:
                output = await asyncio.wait_for(
                    self.execute(input_data), timeout=self.timeout_seconds
                )

                return AgentResult(
                    agent_id=self.agent_id,
                    status=AgentStatus.COMPLETED,
                    output=output,
                    execution_time=time.perf_counter() - start_time,
                    retry_count=attempt,
                )

            except asyncio.TimeoutError:
                last_error = (
                    f"Agent {self.agent_id} timed out after {self.timeout_seconds}s "
                    f"(attempt {attempt + 1})"
                )
            except Exception as exc:  # pragma: no cover - error path validated in tests
                last_error = (
                    f"Agent {self.agent_id} failed: {exc} (attempt {attempt + 1})"
                )

            if attempt < self.retry_count:
                await asyncio.sleep(2**attempt)

        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.FAILED,
            error=last_error,
            execution_time=time.perf_counter() - start_time,
            retry_count=self.retry_count,
        )

    def get_required_inputs(self) -> List[str]:
        """List the input keys required by the agent implementation."""

        return []
