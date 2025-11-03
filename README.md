# Multi-Agent Task Solver

A flexible agent orchestration system that enables multiple specialized AI agents to work together to solve complex tasks through coordinated execution with proper concurrency handling, retries, and timeout management.

## 🎯 Main Goal

Create a robust backend system where isolated agents can pass results to each other in a coordinated workflow, handling real-world challenges like failures, timeouts, and complex dependency chains.

## 🏗️ System Architecture

### Core Components

1. **Client API** – Entry point for external requests
2. **Orchestrator** – Coordinates workflows and agent execution
3. **Agent Registry** – Manages available agent implementations
4. **Workflow Manager** – Maintains DAG definitions and validation
5. **Execution Engine** – Handles scheduling, concurrency, retries, and timeouts
6. **Tool System** – Provides shared tools agents can invoke

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
