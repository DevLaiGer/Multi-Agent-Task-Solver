"""CLI tests for the Multi-Agent Task Solver."""

import json
from types import SimpleNamespace

import pytest

from src import main as cli


@pytest.mark.parametrize(
    "command, registry_attr, expected",
    [
        ("list-agents", "agent_registry", ["beta", "alpha"]),
        ("list-tools", "tool_registry", ["processor", "fetcher"]),
    ],
)
def test_cli_list_commands(monkeypatch, capsys, command, registry_attr, expected):
    monkeypatch.setattr(cli, "_initialize_runtime", lambda: None)
    registry = SimpleNamespace(
        list_agents=lambda: expected,
        list_tools=lambda: expected,
    )
    monkeypatch.setattr(cli, registry_attr, registry)

    exit_code = cli.main([command])

    assert exit_code == 0
    captured = capsys.readouterr()
    for value in sorted(expected):
        assert value in captured.out


def test_cli_run_workflow(monkeypatch, capsys, tmp_path):
    workflow_data = {"workflow_id": "wf", "agents": [], "initial_input": {}}
    workflow_file = tmp_path / "workflow.json"
    workflow_file.write_text(json.dumps(workflow_data))

    def fake_execute(path):
        assert path == workflow_file
        return "{\"status\": \"completed\"}"

    monkeypatch.setattr(cli, "_initialize_runtime", lambda: None)
    monkeypatch.setattr(cli, "_execute_workflow_from_file", fake_execute)

    exit_code = cli.main(["run-workflow", "--config", str(workflow_file)])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "completed" in captured.out


def test_cli_runserver(monkeypatch):
    app_instance = object()
    monkeypatch.setattr(cli, "create_app", lambda: app_instance)

    run_calls = {}

    def fake_run(app, host, port, reload):
        run_calls["args"] = (app, host, port, reload)

    monkeypatch.setattr(cli, "uvicorn", SimpleNamespace(run=fake_run))

    exit_code = cli.main(["runserver", "--host", "127.0.0.1", "--port", "9000"])

    assert exit_code == 0
    assert run_calls["args"] == (app_instance, "127.0.0.1", 9000, False)
