"""Tests for workflow DAG management."""

import pytest

from src.core import WorkflowDAG
from src.models import AgentDefinition, WorkflowRequest


def build_workflow(agents):
    return WorkflowRequest(workflow_id="wf", agents=agents)


def test_workflow_builds_layers():
    agents = [
        AgentDefinition(agent_id="a", agent_type="t", inputs=[]),
        AgentDefinition(agent_id="b", agent_type="t", inputs=["a"]),
        AgentDefinition(agent_id="c", agent_type="t", inputs=["a"]),
        AgentDefinition(agent_id="d", agent_type="t", inputs=["b", "c"]),
    ]
    dag = WorkflowDAG(build_workflow(agents))

    layers = dag.get_execution_layers()
    assert layers[0] == ["a"]
    assert set(layers[1]) == {"b", "c"}
    assert layers[2] == ["d"]


def test_workflow_detects_missing_dependency():
    agents = [
        AgentDefinition(agent_id="a", agent_type="t", inputs=["missing"])
    ]

    with pytest.raises(ValueError):
        WorkflowDAG(build_workflow(agents))


def test_workflow_detects_cycle():
    agents = [
        AgentDefinition(agent_id="a", agent_type="t", inputs=["b"]),
        AgentDefinition(agent_id="b", agent_type="t", inputs=["a"]),
    ]

    with pytest.raises(ValueError):
        WorkflowDAG(build_workflow(agents))


def test_dependencies_and_dependents():
    agents = [
        AgentDefinition(agent_id="a", agent_type="t", inputs=[]),
        AgentDefinition(agent_id="b", agent_type="t", inputs=["a"]),
        AgentDefinition(agent_id="c", agent_type="t", inputs=["a", "b"]),
    ]
    dag = WorkflowDAG(build_workflow(agents))

    assert dag.get_dependencies("c") == ["a", "b"]
    assert set(dag.get_dependents("a")) == {"b", "c"}
    assert dag.is_ready("b", {"a"}) is True
    assert dag.is_ready("c", {"a"}) is False
    assert dag.is_ready("c", {"a", "b"}) is True
