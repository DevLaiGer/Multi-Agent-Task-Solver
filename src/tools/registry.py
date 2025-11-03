"""Registry for managing tool implementations."""

from __future__ import annotations

from typing import Dict, Iterable

from .base_tool import BaseTool


class ToolRegistry:
    """Global registry for tool instances."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""

        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """Remove a tool from the registry."""

        self._tools.pop(name, None)

    def get(self, name: str) -> BaseTool:
        """Retrieve a registered tool."""

        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Unknown tool '{name}'")
        return tool

    def list_tools(self) -> Iterable[str]:
        """List names of registered tools."""

        return tuple(sorted(self._tools.keys()))


tool_registry = ToolRegistry()
