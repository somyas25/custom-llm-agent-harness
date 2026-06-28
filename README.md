# Building a Custom LLM Agent Harness from Scratch

This repository contains an implementation of a containerized Large Language Model (LLM) agent designed to autonomously parse emails, generate summaries, and maintain a prioritized task database. 

Rather than leveraging high-level orchestration frameworks (e.g., LangChain), this project is built using native Python to explore the foundational engineering principles underlying autonomous agents.

---

## INSPIRATION

The primary goal of this project is to demystify agentic workflows by implementing core architectural components manually. Through building this harness from scratch, I will gain hands-on experience with:
* **LLM Tool Utilization:** Constructing system prompts and function definitions that instruct a model to reliably select and format tool execution requests.
* **The [ReAct](https://arxiv.org/abs/2210.03629) Loop:** Implementing the *Thought → Action → Observation* execution loop where the model programmatically evaluates state and determines its next execution step.
* **State Preservation & Memory Management:** Explicitly appending tool outputs (Observations) back into the conversation thread to preserve context across multiple execution steps.
* **Defensive Output Parsing:** Building robust text-parsing logic to handle malformed model responses, tool hallucinations, or logic loops without crashing the underlying software execution.

---

## Core Design Decisions

### 1. Frameworkless Orchestration
All interactions with the LLM API and execution components are managed via native Python code. This explicit approach ensures absolute clarity regarding how tokens travel through the system, how state is modified, and how inputs are structured.

### 2. Environment Isolation via Docker
Granting an LLM engine access to file manipulation or database execution creates security vectors and operational risks (e.g., infinite API loops or unexpected file modifications). Sandboxing the entire application inside a Docker container establishes an isolated runtime environment, securing the host machine from the agent's execution boundaries.

### 3. Persistent Storage with SQLite
To ensure that the agent's task state survives across multiple runtime sessions, data is stored in an embedded SQLite database inside the container rather than in volatile application memory. This replicates a production pattern where state management is entirely decoupled from the core execution engine.

---

## 📁 Repository Layout

```text
docker-email-task-agent/
├── app/
│   ├── __init__.py
│   ├── config.py         # Strongly-typed environment variable validator
│   ├── database.py       # SQLite database initialization and CRUD operations
│   ├── main.py           # Core ReAct execution loop and orchestration engine
│   └── tools.py          # Defined Python functions exposed as tools to the LLM
├── data/                 # Mounted local directory for persistent SQLite data
├── .env.example          # Configuration template for environmental variables
├── .gitignore            # Version control exclusions for sensitive keys and cache
└── Dockerfile            # Multi-layer build file for the containerized runtime