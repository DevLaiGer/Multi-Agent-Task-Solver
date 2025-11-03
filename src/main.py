"""Command-line interface for the Multi-Agent Task Solver."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Iterable, List, Optional

import uvicorn

from .api import create_app
from .agents import agent_registry, register_builtin_agents
from .core import ExecutionEngine
from .models import WorkflowRequest
from .tools import register_builtin_tools, tool_registry


def _initialize_runtime() -> None:
    """Ensure built-in tools and agents are available."""

    register_builtin_tools()
    register_builtin_agents()


def _list_items(values: Iterable[str]) -> str:
    return "\n".join(sorted(values))


def _execute_workflow_from_file(config_path: Path) -> str:
    if not config_path.exists():
        raise FileNotFoundError(f"Workflow configuration not found: {config_path}")

    data = json.loads(config_path.read_text())
    request = WorkflowRequest.model_validate(data)

    engine = ExecutionEngine()
    result = asyncio.run(engine.execute_workflow(request))
    return json.dumps(result.model_dump(), indent=2, default=str)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mats",
        description="Multi-Agent Task Solver command-line interface",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    runserver_parser = subparsers.add_parser(
        "runserver", help="Start the FastAPI server using uvicorn"
    )
    runserver_parser.add_argument("--host", default="0.0.0.0")
    runserver_parser.add_argument("--port", type=int, default=8000)
    runserver_parser.add_argument("--reload", action="store_true")

    subparsers.add_parser("list-agents", help="List registered agent types")
    subparsers.add_parser("list-tools", help="List registered tools")

    workflow_parser = subparsers.add_parser(
        "run-workflow", help="Execute a workflow defined in a JSON file"
    )
    workflow_parser.add_argument(
        "--config", required=True, help="Path to the workflow JSON configuration"
    )

    args = parser.parse_args(argv)

    try:
        if args.command == "runserver":
            app = create_app()
            uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)
            return 0

        _initialize_runtime()

        if args.command == "list-agents":
            output = _list_items(agent_registry.list_agents())
            print(output)
            return 0

        if args.command == "list-tools":
            output = _list_items(tool_registry.list_tools())
            print(output)
            return 0

        if args.command == "run-workflow":
            config_path = Path(args.config)
            output = _execute_workflow_from_file(config_path)
            print(output)
            return 0

        parser.error("Unknown command")
    except Exception as exc:  # pragma: no cover - top-level guard
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
