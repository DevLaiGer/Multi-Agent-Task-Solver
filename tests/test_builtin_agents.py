"""Tests for built-in agents."""

import pytest

from src.agents import AgentRegistry, register_builtin_agents
from src.tools import tool_registry, register_builtin_tools


@pytest.fixture(autouse=True)
def reset_registries():
    for name in list(tool_registry.list_tools()):
        tool_registry.unregister(name)
    register_builtin_tools()
    registry = AgentRegistry()
    register_builtin_agents(registry)
    yield registry


@pytest.mark.asyncio
async def test_data_fetcher_agent(reset_registries):
    registry = reset_registries
    agent = registry.create_agent("fetch", "data_fetcher", {"source": "db"})
    result = await agent.run_with_retries({"data": {"rows": [1, 2, 3]}})
    assert result.status.value == "completed"
    assert result.output["source"] == "db"


@pytest.mark.asyncio
async def test_data_processor_agent(reset_registries):
    registry = reset_registries
    agent = registry.create_agent("processor", "data_processor", {"operation": "sum"})
    fetch_output = {"data": [1, 2, 3]}
    result = await agent.run_with_retries({"fetch": fetch_output})
    assert result.output["result"] == 6


@pytest.mark.asyncio
async def test_calculator_agent(reset_registries):
    registry = reset_registries
    agent = registry.create_agent("calc", "calculator", {"operation": "multiply"})
    result = await agent.run_with_retries({"values": [2, 3, 4]})
    assert result.output["result"] == 24


@pytest.mark.asyncio
async def test_chart_generator_agent(reset_registries):
    registry = reset_registries
    agent = registry.create_agent("chart", "chart_generator", {})
    processor_output = {"result": [5, 10]}
    labels = ["A", "B"]
    result = await agent.run_with_retries({"processor": processor_output, "labels": labels})
    assert result.output["chart_type"] == "bar"
    assert result.output["series"][0]["label"] == "A"
