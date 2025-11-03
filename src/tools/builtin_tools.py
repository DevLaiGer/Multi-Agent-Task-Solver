"""Built-in tools for the Multi-Agent Task Solver."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .base_tool import BaseTool
from .registry import ToolRegistry, tool_registry


class DataFetcherTool(BaseTool):
    """Fetch data from a provided source payload."""

    def __init__(self, default_data: Dict[str, Any] | None = None) -> None:
        self._default_data = default_data or {}

    @property
    def name(self) -> str:
        return "data_fetcher"

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        data = kwargs.get("data") or self._default_data
        source = kwargs.get("source", "direct")
        return {"source": source, "data": data}


class DataProcessorTool(BaseTool):
    """Apply simple processing operations to numeric payloads."""

    @property
    def name(self) -> str:
        return "data_processor"

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        operation = kwargs.get("operation", "identity")
        values = kwargs.get("values") or []

        if not isinstance(values, Iterable):
            raise ValueError("values must be iterable")

        result: Any
        if operation == "sum":
            result = sum(values)
        elif operation == "average":
            nums = list(values)
            result = sum(nums) / len(nums) if nums else 0
        elif operation == "max":
            result = max(values)
        elif operation == "min":
            result = min(values)
        elif operation == "identity":
            result = list(values)
        else:
            raise ValueError(f"Unsupported operation '{operation}'")

        return {"operation": operation, "result": result}


class CalculatorTool(BaseTool):
    """Perform arithmetic operations on provided values."""

    @property
    def name(self) -> str:
        return "calculator"

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        operation = kwargs.get("operation", "add")
        values: List[float] = list(kwargs.get("values", []))

        if not values:
            raise ValueError("values must contain at least one number")

        if operation == "add":
            result = sum(values)
        elif operation == "subtract":
            result = values[0] - sum(values[1:])
        elif operation == "multiply":
            result = 1
            for val in values:
                result *= val
        elif operation == "divide":
            result = values[0]
            for val in values[1:]:
                if val == 0:
                    raise ValueError("Division by zero")
                result /= val
        else:
            raise ValueError(f"Unsupported operation '{operation}'")

        return {"operation": operation, "result": result}


class ChartGeneratorTool(BaseTool):
    """Produce chart-ready data structures."""

    @property
    def name(self) -> str:
        return "chart_generator"

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        chart_type = kwargs.get("chart_type", "bar")
        labels = kwargs.get("labels") or []
        values = kwargs.get("values") or []

        if len(labels) != len(values):
            raise ValueError("labels and values must have the same length")

        return {
            "chart_type": chart_type,
            "series": [
                {"label": label, "value": value}
                for label, value in zip(labels, values)
            ],
        }


def register_builtin_tools(registry: ToolRegistry | None = None) -> None:
    """Register the default set of tools."""

    registry = registry or tool_registry

    tools = [
        DataFetcherTool(),
        DataProcessorTool(),
        CalculatorTool(),
        ChartGeneratorTool(),
    ]

    for tool in tools:
        # Avoid re-registering tools if already present
        if tool.name not in registry.list_tools():
            registry.register(tool)
