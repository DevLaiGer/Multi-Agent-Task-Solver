"""Workflow execution engine for coordinating agent execution."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from ..agents import agent_registry
from ..models import (
    AgentDefinition,
    AgentResult,
    AgentStatus,
    WorkflowRequest,
    WorkflowResponse,
    WorkflowStatus,
)
from .workflow import WorkflowDAG


class ExecutionEngine:
    """Executes workflows composed of registered agents."""

    def __init__(self) -> None:
        self._active_workflows: Dict[str, asyncio.Task] = {}
        self._workflow_results: Dict[str, WorkflowResponse] = {}

    async def execute_workflow(self, workflow_request: WorkflowRequest) -> WorkflowResponse:
        """Execute the workflow defined by ``workflow_request``."""

        workflow_id = workflow_request.workflow_id
        workflow_dag = WorkflowDAG(workflow_request)

        response = WorkflowResponse(
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            results={},
            created_at=datetime.now(),
        )
        self._workflow_results[workflow_id] = response

        current_task = asyncio.current_task()
        if current_task:
            self._active_workflows[workflow_id] = current_task

        start_time = datetime.now()
        all_results: Dict[str, AgentResult] = {}
        completed_agents = set()
        initial_input = workflow_request.initial_input or {}

        try:
            for layer in workflow_dag.get_execution_layers():
                tasks = []
                agent_ids = []

                for agent_id in layer:
                    agent_def = workflow_dag.agents[agent_id]

                    try:
                        input_data = self._gather_input_data(
                            agent_def, all_results, initial_input
                        )
                    except ValueError as exc:
                        all_results[agent_id] = AgentResult(
                            agent_id=agent_id,
                            status=AgentStatus.FAILED,
                            error=str(exc),
                        )
                        completed_agents.add(agent_id)
                        continue

                    if not workflow_dag.is_ready(agent_id, completed_agents):
                        # Dependencies are not complete yet; defer execution
                        continue

                    tasks.append(self._execute_agent(agent_def, input_data))
                    agent_ids.append(agent_id)

                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for agent_id, result in zip(agent_ids, results):
                        if isinstance(result, Exception):
                            agent_result = AgentResult(
                                agent_id=agent_id,
                                status=AgentStatus.FAILED,
                                error=f"Execution failed: {result}",
                            )
                        else:
                            agent_result = result

                        all_results[agent_id] = agent_result
                        completed_agents.add(agent_id)

            response.results = all_results
            response.total_duration = (datetime.now() - start_time).total_seconds()

            if any(res.status is AgentStatus.FAILED for res in all_results.values()):
                response.status = WorkflowStatus.FAILED
            else:
                response.status = WorkflowStatus.COMPLETED

        except asyncio.CancelledError:
            response.status = WorkflowStatus.CANCELLED
            response.results = all_results
            response.total_duration = (datetime.now() - start_time).total_seconds()
            raise
        except Exception as exc:  # pragma: no cover - defensive catch all
            response.status = WorkflowStatus.FAILED
            response.results = all_results
            response.total_duration = (datetime.now() - start_time).total_seconds()
            response.error = str(exc)
            raise
        finally:
            self._active_workflows.pop(workflow_id, None)
            self._workflow_results[workflow_id] = response

        return response

    async def _execute_agent(
        self, agent_def: AgentDefinition, input_data: Dict[str, Any]
    ) -> AgentResult:
        """Instantiate and execute an agent with retry handling."""

        agent = agent_registry.create_agent(
            agent_def.agent_id, agent_def.agent_type, agent_def.config
        )
        return await agent.run_with_retries(input_data)

    def _gather_input_data(
        self,
        agent_def: AgentDefinition,
        all_results: Dict[str, AgentResult],
        initial_input: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the input payload for ``agent_def``."""

        input_data = dict(initial_input)

        for dependency_id in agent_def.inputs:
            result = all_results.get(dependency_id)
            if result is None:
                raise ValueError(
                    f"Dependency agent '{dependency_id}' has not produced a result"
                )
            if result.status is not AgentStatus.COMPLETED or result.output is None:
                raise ValueError(
                    f"Dependency agent '{dependency_id}' did not complete successfully"
                )
            input_data[dependency_id] = result.output

        return input_data

    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResponse]:
        """Return the latest known status for ``workflow_id``."""

        return self._workflow_results.get(workflow_id)

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Attempt to cancel a running workflow."""

        task = self._active_workflows.get(workflow_id)
        if task is None:
            return False
        task.cancel()
        return True

    def list_active_workflows(self) -> Iterable[str]:
        """List identifiers of workflows currently tracked as active."""

        return tuple(self._active_workflows.keys())
