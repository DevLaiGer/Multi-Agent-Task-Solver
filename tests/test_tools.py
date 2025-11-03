"""Tests for the tool system."""

import pytest

from src.tools import BaseTool, ToolRegistry, tool_registry, register_builtin_tools


@pytest.fixture(autouse=True)
def reset_tool_registry():
    existing = list(tool_registry.list_tools())
    for name in existing:
        tool_registry.unregister(name)
    yield
    for name in list(tool_registry.list_tools()):
        tool_registry.unregister(name)


class DummyTool(BaseTool):
    @property
    def name(self) -> str:
        return "dummy"

    async def execute(self, **kwargs):
        return {"value": kwargs.get("value", 0)}


def test_tool_registry_register_and_get():
    registry = ToolRegistry()
    tool = DummyTool()

    registry.register(tool)
    fetched_tool = registry.get("dummy")

    assert fetched_tool is tool
    assert registry.list_tools() == ("dummy",)


def test_tool_registry_duplicate_registration():
    registry = ToolRegistry()
    registry.register(DummyTool())

    with pytest.raises(ValueError):
        registry.register(DummyTool())


def test_tool_registry_unknown():
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.get("missing")


@pytest.mark.asyncio
async def test_builtin_tool_registration():
    registry = ToolRegistry()
    register_builtin_tools(registry)

    tools = set(registry.list_tools())
    assert {"data_fetcher", "data_processor", "calculator", "chart_generator"}.issubset(tools)


@pytest.mark.asyncio
async def test_data_processor_tool_operations():
    register_builtin_tools(tool_registry)
    processor = tool_registry.get("data_processor")

    result = await processor.execute(operation="sum", values=[1, 2, 3])
    assert result["operation"] == "sum"
    assert result["result"] == 6

    with pytest.raises(ValueError):
        await processor.execute(operation="unknown", values=[1])


@pytest.mark.asyncio
async def test_calculator_tool_divide_and_error():
    register_builtin_tools(tool_registry)
    calculator = tool_registry.get("calculator")

    result = await calculator.execute(operation="divide", values=[8, 2])
    assert result["result"] == 4

    with pytest.raises(ValueError):
        await calculator.execute(operation="divide", values=[5, 0])
