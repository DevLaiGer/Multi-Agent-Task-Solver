"""Built-in agent implementations."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from ..tools import tool_registry
from .base_agent import BaseAgent
from .registry import AgentRegistry, agent_registry


def _merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for data in dicts:
        for key, value in data.items():
            merged[key] = value
    return merged


def _extract_sequence(values: Iterable[Any] | Any) -> Iterable[Any]:
    if isinstance(values, (list, tuple)):
        return values
    return [values]


class ToolBackedAgent(BaseAgent):
    """Base agent that delegates execution to a registered tool."""

    tool_name: str

    def _prepare_params(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        params = _merge_dicts(input_data, self.config)
        return params

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        tool = tool_registry.get(self.tool_name)
        params = self._prepare_params(input_data)
        return await tool.execute(**params)


class DataFetcherAgent(ToolBackedAgent):
    """Agent that fetches data using the data_fetcher tool."""

    tool_name = "data_fetcher"

    def _prepare_params(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return _merge_dicts(self.config, input_data)


class DataProcessorAgent(ToolBackedAgent):
    """Agent that processes data from dependency outputs."""

    tool_name = "data_processor"

    def _prepare_params(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        params = dict(self.config)
        if "values" not in params:
            for value in input_data.values():
                if isinstance(value, dict):
                    if "data" in value:
                        params["values"] = value["data"]
                        break
                    if "result" in value:
                        params["values"] = _extract_sequence(value["result"])
                        break
            else:
                if "values" in input_data:
                    params["values"] = input_data["values"]
        params.setdefault("operation", self.config.get("operation", "identity"))
        return params


class CalculatorAgent(ToolBackedAgent):
    """Agent that performs arithmetic using the calculator tool."""

    tool_name = "calculator"

    def _prepare_params(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        params = dict(self.config)
        if "values" not in params:
            for value in input_data.values():
                if isinstance(value, dict) and "result" in value:
                    params["values"] = _extract_sequence(value["result"])
                    break
            else:
                if "values" in input_data:
                    params["values"] = _extract_sequence(input_data["values"])
        return params


class ChartGeneratorAgent(ToolBackedAgent):
    """Agent that produces chart-ready structures via chart_generator tool."""

    tool_name = "chart_generator"

    def _prepare_params(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        params = dict(self.config)
        if "labels" not in params:
            for value in input_data.values():
                if isinstance(value, dict) and "labels" in value:
                    params.setdefault("labels", value["labels"])
                if isinstance(value, dict) and "result" in value:
                    params.setdefault("values", _extract_sequence(value["result"]))
        if "values" not in params and "values" in input_data:
            params["values"] = _extract_sequence(input_data["values"])
        if "labels" not in params and "labels" in input_data:
            params["labels"] = input_data["labels"]
        return params


def register_builtin_agents(registry: AgentRegistry | None = None) -> None:
    """Register the built-in agent types."""

    registry = registry or agent_registry
    agents = {
        "data_fetcher": DataFetcherAgent,
        "data_processor": DataProcessorAgent,
        "calculator": CalculatorAgent,
        "chart_generator": ChartGeneratorAgent,
    }

    for agent_type, agent_cls in agents.items():
        if registry.get_agent_class(agent_type) is None:
            registry.register(agent_type, agent_cls)
