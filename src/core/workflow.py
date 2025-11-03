"""Workflow DAG management for the Multi-Agent Task Solver."""

from __future__ import annotations

from typing import Dict, Iterable, List, Set

import networkx as nx

from ..models import AgentDefinition, WorkflowRequest


class WorkflowDAG:
    """Constructs and validates the workflow DAG for agent execution."""

    def __init__(self, workflow_request: WorkflowRequest) -> None:
        self.workflow_id: str = workflow_request.workflow_id
        self.agents: Dict[str, AgentDefinition] = {
            agent.agent_id: agent for agent in workflow_request.agents
        }
        self.graph = nx.DiGraph()
        self._build_graph()
        self._validate_graph()

    def _build_graph(self) -> None:
        """Build a directed graph from agent definitions and dependencies."""

        for agent_id in self.agents:
            self.graph.add_node(agent_id)

        for agent_id, agent_def in self.agents.items():
            for dependency in agent_def.inputs:
                if dependency not in self.agents:
                    raise ValueError(
                        f"Input agent '{dependency}' not found for agent '{agent_id}'"
                    )
                self.graph.add_edge(dependency, agent_id)

    def _validate_graph(self) -> None:
        """Ensure the workflow graph is acyclic and dependencies exist."""

        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Workflow contains cycles")

    def get_execution_layers(self) -> List[List[str]]:
        """Return agents grouped in parallelizable execution layers."""

        layers: List[List[str]] = []
        remaining_graph = self.graph.copy()

        while remaining_graph.number_of_nodes() > 0:
            current_layer = [
                node
                for node in remaining_graph.nodes
                if remaining_graph.in_degree(node) == 0
            ]

            if not current_layer:
                raise ValueError("Circular dependency detected in workflow")

            layers.append(current_layer)
            remaining_graph.remove_nodes_from(current_layer)

        return layers

    def get_dependencies(self, agent_id: str) -> List[str]:
        """Return direct dependencies required for an agent to run."""

        if agent_id not in self.agents:
            raise KeyError(f"Unknown agent '{agent_id}'")
        return list(self.graph.predecessors(agent_id))

    def get_dependents(self, agent_id: str) -> List[str]:
        """Return agents that depend on the specified agent."""

        if agent_id not in self.agents:
            raise KeyError(f"Unknown agent '{agent_id}'")
        return list(self.graph.successors(agent_id))

    def is_ready(self, agent_id: str, completed: Set[str]) -> bool:
        """Determine if an agent is ready to execute given completed dependencies."""

        dependencies = self.get_dependencies(agent_id)
        return all(dep in completed for dep in dependencies)

    def iter_agents(self) -> Iterable[AgentDefinition]:
        """Iterate over the agents in the workflow."""

        return self.agents.values()
