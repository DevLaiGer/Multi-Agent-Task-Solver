"""API tests for the Multi-Agent Task Solver."""

import httpx
import pytest
import pytest_asyncio

from src.agents import BaseAgent, agent_registry, register_builtin_agents
from src.api import create_app


class IncrementAgent(BaseAgent):
    async def execute(self, input_data):
        value = input_data.get("value", 0)
        return {"value": value + 1}


@pytest.fixture(autouse=True)
def reset_agent_registry():
    existing = list(agent_registry.list_agents())
    for agent_type in existing:
        agent_registry.unregister(agent_type)
    register_builtin_agents()
    yield
    for agent_type in list(agent_registry.list_agents()):
        agent_registry.unregister(agent_type)


@pytest.fixture
def app():
    agent_registry.register("increment", IncrementAgent)
    return create_app()


@pytest_asyncio.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["application"] == "Multi-Agent Task Solver"


@pytest.mark.asyncio
async def test_list_agents_endpoint(client):
    response = await client.get("/agents")
    assert response.status_code == 200
    payload = response.json()
    assert "increment" in payload["agents"]


@pytest.mark.asyncio
async def test_execute_workflow_endpoint(client):
    workflow_payload = {
        "workflow_id": "wf_api",
        "initial_input": {"value": 1},
        "agents": [
            {"agent_id": "step1", "agent_type": "increment", "inputs": []},
            {"agent_id": "step2", "agent_type": "increment", "inputs": ["step1"]},
        ],
    }

    response = await client.post("/workflows", json=workflow_payload)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["results"]["step2"]["output"] == {"value": 2}


@pytest.mark.asyncio
async def test_cancel_unknown_workflow(client):
    response = await client.post("/workflows/unknown/cancel")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_template_endpoint(client):
    response = await client.get("/workflows/templates/linear_two_step")
    assert response.status_code == 200
    payload = response.json()
    assert payload["workflow_id"] == "linear_example"
