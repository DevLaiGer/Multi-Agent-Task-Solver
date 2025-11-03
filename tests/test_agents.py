"""Tests for the agent framework."""

import asyncio
import pytest

from src.agents import BaseAgent, AgentRegistry, agent_registry
from src.models import AgentStatus


class DummyAgent(BaseAgent):
    """Simple agent used for testing."""

    def __init__(self, agent_id: str, config=None):
        super().__init__(agent_id, config)
        cfg = self.config
        self.fail_until = int(cfg.get("fail_until", 0))
        self.delay = float(cfg.get("delay", 0.0))
        self._attempts = 0

    async def execute(self, input_data):
        self._attempts += 1
        if self.delay:
            await asyncio.sleep(self.delay)
        if self._attempts <= self.fail_until:
            raise RuntimeError("intentional failure")
        return {"result": input_data.get("value", 0) + 1}


def test_agent_registry_register_and_create():
    registry = AgentRegistry()
    registry.register("dummy", DummyAgent)

    agent = registry.create_agent(
        "agent1", "dummy", {"retry_count": 2, "fail_until": 1}
    )
    assert isinstance(agent, DummyAgent)
    assert agent.retry_count == 2
    assert registry.list_agents() == ["dummy"]


def test_agent_registry_duplicate_registration():
    registry = AgentRegistry()
    registry.register("dummy", DummyAgent)
    with pytest.raises(ValueError):
        registry.register("dummy", DummyAgent)


def test_agent_registry_unknown_type():
    registry = AgentRegistry()
    with pytest.raises(ValueError):
        registry.create_agent("agent1", "unknown")


@pytest.mark.asyncio
async def test_base_agent_success_after_retries():
    agent = DummyAgent("dummy", {"retry_count": 2, "fail_until": 1})
    result = await agent.run_with_retries({"value": 10})

    assert result.status is AgentStatus.COMPLETED
    assert result.output == {"result": 11}
    assert result.retry_count == 1
    assert result.error is None


@pytest.mark.asyncio
async def test_base_agent_timeout():
    class SlowAgent(BaseAgent):
        async def execute(self, input_data):
            await asyncio.sleep(0.2)
            return {"result": 42}

    agent = SlowAgent("slow", {"timeout_seconds": 0.05, "retry_count": 0})
    result = await agent.run_with_retries({})

    assert result.status is AgentStatus.FAILED
    assert "timed out" in (result.error or "")


@pytest.mark.asyncio
async def test_base_agent_failure_after_retries():
    agent = DummyAgent("dummy", {"retry_count": 0, "fail_until": 5})
    result = await agent.run_with_retries({})

    assert result.status is AgentStatus.FAILED
    assert "failed" in (result.error or "")
    assert result.retry_count == 0


def test_global_agent_registry():
    class AnotherDummyAgent(BaseAgent):
        async def execute(self, input_data):
            return {"ok": True}

    agent_registry.unregister("another_dummy")
    agent_registry.register("another_dummy", AnotherDummyAgent)

    agent = agent_registry.create_agent("id", "another_dummy", {})
    assert isinstance(agent, AnotherDummyAgent)

    assert "another_dummy" in agent_registry.list_agents()
    agent_registry.unregister("another_dummy")
