# Multi-Agent Task Solver

A flexible agent orchestration system that enables multiple specialized AI agents to work together to solve complex tasks through coordinated execution with proper concurrency handling, retries, and timeout management.

## 🚀 Getting Started

Create a robust backend system where isolated agents can pass results to each other in a coordinated workflow, handling real-world challenges like failures, timeouts, and complex dependency chains.

## 🏗️ System Architecture

### Core Components

1. **Client API** – Entry point for external requests
2. **Orchestrator** – Coordinates workflows and agent execution
3. **Agent Registry** – Manages available agent implementations
4. **Workflow Manager** – Maintains DAG definitions and validation
5. **Execution Engine** – Handles scheduling, concurrency, retries, and timeouts
6. **Tool System** – Provides shared tools agents can invoke
7. **CLI & API** – Unified interface for triggering workflows and running the service

### Running Tests

```bash
python -m pytest
```

### Command Line Interface

The project ships with a CLI entrypoint that lets you inspect registries, run workflows from disk, or start the API server.

```bash
# List agents/tools
python -m src.main list-agents
python -m src.main list-tools

# Execute workflow defined in a JSON file
python -m src.main run-workflow --config path/to/workflow.json

# Run the FastAPI server
python -m src.main runserver --host 0.0.0.0 --port 8000
```

### API Endpoints

Key routes exposed by the FastAPI application:

- `GET /` – Application metadata
- `GET /health` – Health check
- `GET /agents` – Registered agent types
- `GET /tools` – Registered tools
- `POST /workflows` – Execute a workflow request
- `GET /workflows/{id}` – Retrieve workflow status
- `POST /workflows/{id}/cancel` – Cancel a running workflow
- `GET /workflows/templates/{name}` – Retrieve template definitions

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client API    │───▶│  Orchestrator    │───▶│  Agent Registry │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Workflow      │    │   Execution      │    │   Tool System   │
│   Manager       │    │   Engine         │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   DAG Builder   │    │   Task Queue     │    │   Tool Registry │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🕒 Development Phases

### Phase 1: Core Framework
- Agent base class & registry
- Workflow DAG structure
- Message bus for data propagation

### Phase 2: Execution Engine
- Concurrent execution
- Retry & timeout mechanisms
- Result management and tracing

### Phase 3: API & Tool System
- REST API endpoints
- Pluggable tool system
- Example tools

### Phase 4: Polish & Documentation
- Error handling & validation
- Documentation
- Demo preparation
