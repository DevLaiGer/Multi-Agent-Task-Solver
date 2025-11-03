# Multi-Agent Task Solver (MATS)

A production-ready orchestration platform that enables specialized AI agents to collaborate through configurable workflows. The system delivers resilient execution with retries, per-agent timeouts, dependency-aware scheduling, and a pluggable tool ecosystem — all accessible through a FastAPI service and a command-line interface.

---

## 📌 Highlights

- **47 automated tests** covering agents, workflows, tools, execution engine, CLI, and API
- **Zero warnings** — Pydantic v2 compliant (`ConfigDict`), clean lint status
- **Comprehensive documentation** for developers and operators
- **Extensible architecture** for adding new agents, tools, and workflow templates

---

## 🧱 Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│     Clients     │───▶│    FastAPI       │───▶│  Execution Engine │
└─────────────────┘    └──────────────────┘    └──────────────────┘
          │                        │                     │
          ▼                        ▼                     ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Agent Registry │    │  Workflow  DAG   │    │   Tool Registry   │
└─────────────────┘    └──────────────────┘    └──────────────────┘
          │                        │                     │
          ▼                        ▼                     ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Built-in Agents │    │  Execution Tasks │    │  Built-in Tools  │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

**Core modules**:

| Module            | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `src/models/`     | Pydantic schemas for agents, workflows, and execution results           |
| `src/agents/`     | Base agent class, registry, and built-in agent implementations          |
| `src/core/`       | Workflow DAG builder and async execution engine                         |
| `src/tools/`      | Tool interface, registry, and built-in tools                            |
| `src/api/`        | FastAPI routes exposing workflow orchestration                          |
| `src/main.py`     | CLI entry point for running servers, workflows, and registry inspection |

---

## 📂 Project Structure

```
src/
├── main.py                     # CLI entry point
├── agents/
│   ├── base_agent.py           # BaseAgent with retry & timeout
│   ├── builtin_agents.py       # Tool-backed agent implementations
│   └── registry.py             # AgentRegistry and global singleton
├── api/
│   └── routes.py               # FastAPI application factory & routes
├── core/
│   ├── workflow.py             # DAG construction & validation
│   └── execution_engine.py     # Layered async execution engine
├── models/
│   └── schemas.py              # Pydantic data models (ConfigDict based)
└── tools/
    ├── base_tool.py            # Tool abstraction
    ├── builtin_tools.py        # Fetcher, processor, calculator, chart tools
    └── registry.py             # ToolRegistry & global instance

tests/
├── test_agents.py              # Agent registry & retry logic
├── test_api.py                 # ASGI integration tests
├── test_builtin_agents.py      # Tool-backed agent behaviour
├── test_cli.py                 # CLI command coverage
├── test_execution_engine.py    # Execution engine workflows
├── test_models.py              # Schema validation & serialization
├── test_tools.py               # Tool registry & operations
└── test_workflow.py            # DAG validation and layering
```

---

## 🛠️ Installation & Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx  # optional dev deps
```

---

## ⚙️ Command-Line Interface

All runtime operations are available via the CLI:

```bash
# Launch the FastAPI server
python -m src.main runserver --host 0.0.0.0 --port 8000 [--reload]

# Inspect registered components
python -m src.main list-agents
python -m src.main list-tools

# Execute a workflow from a JSON definition
python -m src.main run-workflow --config path/to/workflow.json
```

The CLI bootstraps built-in tools and agents automatically before executing commands (other than `runserver`, which delegates to FastAPI initialization).

---

## 🌐 API Overview

`create_app()` builds a FastAPI application registered with all routes listed below.

| Method | Route                              | Description                                  |
|--------|------------------------------------|----------------------------------------------|
| GET    | `/`                                | Application metadata                          |
| GET    | `/health`                          | Health check                                  |
| GET    | `/agents`                          | List registered agent types                   |
| GET    | `/tools`                           | List registered tools                         |
| POST   | `/workflows`                       | Execute a workflow (body: `WorkflowRequest`)  |
| GET    | `/workflows/{workflow_id}`         | Retrieve workflow status                      |
| POST   | `/workflows/{workflow_id}/cancel`  | Cancel a running workflow                     |
| GET    | `/workflows/templates/{template}`  | Fetch built-in workflow templates             |

### Sample `WorkflowRequest`

```json
{
  "workflow_id": "example_pipeline",
  "initial_input": {"counter": 1},
  "agents": [
    {
      "agent_id": "step_a",
      "agent_type": "data_fetcher",
      "inputs": [],
      "config": {"source": "static"}
    },
    {
      "agent_id": "step_b",
      "agent_type": "data_processor",
      "inputs": ["step_a"],
      "config": {"operation": "sum"}
    }
  ]
}
```

---

## 🤖 Built-in Agents & Tools

| Agent Type          | Backing Tool     | Purpose                                   |
|---------------------|------------------|-------------------------------------------|
| `data_fetcher`      | `data_fetcher`   | Retrieves payloads from static/configured sources |
| `data_processor`    | `data_processor` | Aggregates or transforms numeric lists     |
| `calculator`        | `calculator`     | Performs arithmetic (add/subtract/multiply/divide) |
| `chart_generator`   | `chart_generator`| Produces chart-ready series structures     |

Tool registry can be extended by registering new `BaseTool` implementations; agents can be added by subclassing `ToolBackedAgent` or `BaseAgent` directly.

---

## 🧮 Workflow Engine Features

- Directed Acyclic Graph validation (cycles rejected)
- Automatic calculation of execution layers for parallelism
- Dependency checking (`is_ready`) before agent invocation
- Async execution with configurable retries and exponential backoff
- Per-agent timeouts enforced via `asyncio.wait_for`
- Cancellation support for active workflows

---

## ✅ Testing

```bash
python -m pytest -v
```

**Test suites:** 47 total tests spanning agents, workflows, tools, API, CLI, and models. All tests pass with no warnings.

---

## 📦 Requirements

- Python 3.8+
- `fastapi==0.104.1`
- `uvicorn==0.24.0`
- `pydantic==2.5.0`
- `networkx==3.2.1`
- `python-multipart==0.0.6`

Dev/testing (optional): `pytest`, `pytest-asyncio`, `httpx`

---

## 🧭 Development Notes

- All Pydantic models use `ConfigDict`, ensuring compatibility with Pydantic v2
- `.gitignore` excludes bytecode caches, build artifacts, and virtual environments
- CLI and API share the same execution engine and registries for consistency
- Project status and verification details available in `PROJECT_STATUS.md`

---

## 📈 Roadmap Ideas

- Pluggable authentication for the API
- Persistent workflow history storage
- Additional built-in tools (LLM integration, data exporters)
- Front-end dashboard consuming the API

---

## 🛡️ License

> Replace with your chosen license text.

---

**Version:** 1.0.0  
**Maintainers:** Multi-Agent Task Solver Team
