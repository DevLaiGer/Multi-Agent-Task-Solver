"""Agent registry for managing agent implementations."""

from __future__ import annotations

from typing import Dict, List, Optional, Type

from .base_agent import BaseAgent


class AgentRegistry:
    """Registry for tracking available agent implementations."""

    def __init__(self) -> None:
        self._agents: Dict[str, Type[BaseAgent]] = {}

    def register(self, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """Register a new agent type.

        Args:
            agent_type: Unique identifier for the agent type.
            agent_class: Concrete subclass of :class:`BaseAgent`.

        Raises:
            ValueError: If the agent type is already registered or agent_class
                is not a subclass of :class:`BaseAgent`.
        """

        if agent_type in self._agents:
            raise ValueError(f"Agent type '{agent_type}' already registered")

        if not issubclass(agent_class, BaseAgent):
            raise TypeError("agent_class must be a subclass of BaseAgent")

        self._agents[agent_type] = agent_class

    def unregister(self, agent_type: str) -> None:
        """Remove an agent type from the registry."""

        self._agents.pop(agent_type, None)

    def get_agent_class(self, agent_type: str) -> Optional[Type[BaseAgent]]:
        """Retrieve the agent class for the specified type."""

        return self._agents.get(agent_type)

    def create_agent(self, agent_id: str, agent_type: str, config: Optional[dict] = None) -> BaseAgent:
        """Instantiate an agent by type.

        Args:
            agent_id: Unique identifier for the agent instance.
            agent_type: Registered agent type to instantiate.
            config: Configuration dictionary passed to the agent.

        Raises:
            ValueError: If the agent type is unknown.
        """

        agent_class = self.get_agent_class(agent_type)
        if agent_class is None:
            raise ValueError(f"Unknown agent type: {agent_type}")

        return agent_class(agent_id, config or {})

    def list_agents(self) -> List[str]:
        """List all registered agent types."""

        return sorted(self._agents.keys())


# Global registry instance used by the application
agent_registry = AgentRegistry()
