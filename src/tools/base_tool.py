"""Base tool abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Abstract base class for reusable tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier."""

    @property
    def description(self) -> str:
        """Short description of the tool."""

        return self.__class__.__doc__ or self.name

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool logic and return result payload."""

    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        """Convenience wrapper invoking :meth:`execute`."""

        return await self.execute(**kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
