# AI Agent Platform

> A complete, from-scratch agent execution platform with SDK, Gateway, Harness, and Docker Sandbox — built to teach and extend.

---

##  What Problem Does This Solve?

Agent frameworks are powerful, but they hide the mechanics. You call `agent.run()` and hope for the best. When something breaks, you're debugging a black box.

This project exists to **make every layer visible and hackable**:

| Problem | How This Solves It |
|---------|-------------------|
| **"How does the agent loop actually work?"** | The Harness implements the full ReAct loop: prompt → parse tool calls → dispatch → collect results → iterate. Every step is explicit code you can trace and modify. |
| **"How do I safely run AI-generated code?"** | The Docker Sandbox isolates code execution with memory, CPU, and timeout limits — verified by automated OOM and timeout tests. |
| **"How do I serve agents to other apps?"** | The Gateway exposes REST and WebSocket APIs so any client (mobile, web, CLI) can create agents and watch them think in real time. |
| **"How do I test without burning API credits?"** | The Mock LLM Backend simulates deterministic tool-call sequences so you can build and test end-to-end flows locally before connecting a real model. |
| **"How do I add new capabilities?"** | Tools are just async Python functions wrapped in a `Tool` class. Register them in the Gateway and they become available to any agent instantly. |

---

##  Architecture

```
┌─────────────────┐       HTTP / WebSocket       ┌──────────────────┐
│     Client      │◄────────────────────────────►│     Gateway      │
│  (SDK / CLI)    │   REST API + Live Streaming  │    (FastAPI)     │
└─────────────────┘                              └────────┬─────────┘
                                                          │
                    ┌─────────────────────────────────────┼────────────────────┐
                    │                                     │                    │
                    ▼                                     ▼                    ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐   ┌──────────────────┐
│         Harness             │   │         Harness             │   │    Docker        │
│      (AgentRunner)          │   │      (ToolRegistry)         │   │    Sandbox       │
│                             │   │                             │   │                  │
│  1. Prompt LLM with context │   │  math_tool    ── fibonacci  │   │  tmp script file │
│  2. Parse tool_calls        │   │  code_tool     ── Python    │   │  docker run --rm │
│  3. Dispatch via registry   │   │  calculator    ── eval      │   │  memory limits   │
│  4. Feed results back       │   │  shell_tool    ── sh        │   │  CPU limits      │
│  5. Repeat or answer        │   │  fetch_tool    ── HTTP      │   │  network none    │
│                             │   │  read_file     ── I/O       │   │  stdout capture  │
│  Supports Mock + OpenAI     │   │  write_file    ── I/O       │   │                  │
│  (swap by config)           │   │  plot_tool     ── charts    │   │                  │
└─────────────────────────────┘   └─────────────────────────────┘   └──────────────────┘
```

### Data Flow: A Single Request

```
Client ──POST /agents/{id}/run──► Gateway
                                      │
                                      ▼
                              AgentRunner.run()
                                      │
                        ┌─────────────┼─────────────┐
                        ▼             ▼             ▼
                LLM.generate()   ToolRegistry.get()  Events collected
                        │             │                   │
                        ▼             ▼                   ▼
              "Call math_tool"   math_tool.execute()   RunResult
                        │             │                   │
                        ▼             ▼                   ▼
              Tool result fed     Returns "55"         Gateway
              back to LLM                              responds
```

---

##  Installation

### Prerequisites

- Python 3.10+
- Docker (for sandboxed tools)

### 1. Clone / Navigate

```bash
cd ai-agent-platform
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- `pydantic` v2 (data modeling)
- `fastapi` + `uvicorn` (Gateway)
- `httpx` (SDK client + fetch tool)
- `pytest` + `pytest-asyncio` (testing)
- `matplotlib` + `numpy` (plot tool)

### 4. Verify Docker

```bash
docker ps
```

If Docker is not running, start it before using sandboxed tools.

---

##  Quickstart

### Start the Gateway

```bash
PYTHONPATH=. uvicorn gateway.main:app --host 0.0.0.0 --port 8000
```

You should see:

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Run the Demo

In a **second terminal**:

```bash
cd ai-agent-platform
PYTHONPATH=. python demo.py
```

**Expected output:**

```
Created agent: multi (92d10728-7580-4a97-824f-e67ee447fe49)

Status: completed
Result: The 10th Fibonacci number is 55.

Events (6):
  [Tool Call] Calling math_tool -> args: {'n': 10}
  [Tool Result] 55...
  [Tool Call] Calling code_tool -> args: {'code': 'def fib(n)...'}
  [Tool Result] 55...
  [message] The 10th Fibonacci number is 55.
  [Final] The 10th Fibonacci number is 55.
```

### Explore the API

```bash
# Health check
curl http://localhost:8000/health

# Create an agent
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "my_agent", "tools": ["math_tool"], "llm_backend": "mock"}'

# Run a task (replace <agent_id> with the ID from above)
curl -X POST "http://localhost:8000/agents/<agent_id>/run" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "<agent_id>", "task": "Calculate fib(10)"}'
```

---

##  Components in Detail

### SDK (`sdk/`)

The SDK is the **client-side library**. It lets any Python application create and run agents without knowing HTTP internals.

```python
from sdk import AgentClient, AgentBuilder

client = AgentClient("http://localhost:8000")

agent = (
    AgentBuilder()
    .name("my_agent")
    .tool("math_tool")
    .tool("calculator_tool")
    .llm_backend("mock")
    .build()
)

created = client.create_agent(agent)
result = client.run_task(created.id, "Calculate sqrt(144)")
print(result.result)  # 12.0
```

**Key classes:**
- `AgentBuilder` — Fluent API for constructing agent configs
- `AgentClient` — HTTP client with 120-second default timeout for long-running tasks

---

### Gateway (`gateway/`)

The Gateway is the **API entry point**. It routes requests from the SDK (or any HTTP client) into the Harness.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | `GET` | Verify Gateway is running |
| `/agents` | `POST` | Create a new agent configuration |
| `/agents/{id}/run` | `POST` | Execute a task synchronously |
| `/agents/{id}/runs/{run_id}` | `GET` | Retrieve run status and results |
| `/agents/{id}/stream` | `WebSocket` | Stream events in real time |

**Why synchronous `POST /run`?**
For simplicity. The entire agent loop executes in one HTTP call. For production workloads, you'd return a `run_id` immediately and poll or use the WebSocket stream.

**WebSocket Streaming:**

```javascript
const ws = new WebSocket("ws://localhost:8000/agents/<id>/stream");
ws.send(JSON.stringify({task: "Calculate fib(10)"}));
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === "final") console.log("Done:", msg.result);
  else console.log("Event:", msg.type, msg.content);
};
```

---

### Harness (`harness/`)

The Harness is the **execution engine**. It implements the agent reasoning loop.

```
User Message
     │
     ▼
MockBackend.generate([user_msg], [available_tools])
     │
     ▼
LLMResponse:
  content: null
  tool_calls: [ToolCall(name="math_tool", arguments={"n": 10})]
     │
     ▼
ToolRegistry.get("math_tool").execute(n=10)
     │
     ▼
"55"
     │
     ▼
Feed back to LLM as "tool" message
     │
     ▼
MockBackend.generate([user_msg, tool_call, tool_result], ...)
     │
     ▼
LLMResponse:
  content: "The 10th Fibonacci number is 55."
  tool_calls: []
     │
     ▼
Final answer returned as RunResult
```

**Key classes:**
- `AgentRunner` — Orchestrates the loop with `max_iterations` guard
- `ConversationState` — Tracks messages and events for a single run
- `ToolRegistry` — Discovers and dispatches tools by name
- `LLMBackend` — Abstract interface with `MockBackend` (deterministic) and `OpenAIBackend` (real API)

---

### Sandbox (`sandbox/`)

The Sandbox runs **untrusted code inside Docker containers**.

Every sandboxed execution gets:

| Resource | Default | Why It Matters |
|----------|---------|----------------|
| Memory | 128m | Prevents OOM crashes on host |
| CPU | 1.0 | Limits CPU hogging |
| Swap | 128m (matching memory) | Prevents swap escape |
| Network | Disabled | Blocks outbound connections |
| Filesystem | Read-only mount | Script can't modify host files |
| Timeout | 30s | Kills runaway code |

**What's tested:**
- ✅ Hello World execution
- ✅ Timeout enforcement (kills infinite loops)
- ✅ Python error propagation
- ✅ OOM kill (allocates 256MB inside 32MB container)

---

##  Built-in Tools

| Tool | Category | What It Does | Security |
|------|----------|-------------|----------|
| `math_tool` | Safe | Calculate Fibonacci numbers | Pure Python, no I/O |
| `calculator_tool` | Safe | Eval math expressions (`log(100)`, `sqrt(16) + 5`) | Restricted `eval()` with no builtins |
| `code_tool` | Docker | Execute arbitrary Python scripts | Isolated container |
| `shell_tool` | Docker | Execute shell commands | Isolated container with `alpine` |
| `fetch_tool` | Safe | Fetch web pages via HTTP GET | Timeout + size limit |
| `read_file` | Safe | Read files from sandbox directory | Path traversal prevention |
| `write_file` | Safe | Write files to sandbox directory | Path traversal prevention |
| `plot_tool` | Safe | Generate matplotlib plots as base64 PNG | Runs locally with numpy/matplotlib |

### Adding a New Tool

Create a file in `harness/tools/my_tool.py`:

```python
from harness.registry import Tool

async def my_tool(query: str) -> str:
    return f"You asked: {query}"

my_tool_def = Tool(
    name="my_tool",
    description="Describe what the tool does.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The input"}
        },
        "required": ["query"],
    },
    handler=my_tool,
)
```

Then add the import and registration in:
- `gateway/routes.py`
- `gateway/websocket.py`

---

##  Configuration

### LLM Backends

| Backend | How to Enable | Default? |
|---------|---------------|----------|
| **Mock** | Set `"llm_backend": "mock"` on agent | ✅ Yes |
| **OpenAI** | Set `"llm_backend": "openai"` + `OPENAI_API_KEY` env var | Optional |

```bash
export OPENAI_API_KEY="sk-..."
```

The backend is selected **per agent**, so you can have one agent using Mock and another using OpenAI at the same time.

---

##  Testing

Run everything:

```bash
PYTHONPATH=. pytest tests/ -v
```

**Current suite:** 40 tests covering SDK, Gateway, Harness, Sandbox, Integration, WebSocket, and all 7 tools.

### Test Categories

| Suite | Coverage |
|-------|----------|
| `test_sdk.py` | Client/Builder fluent API |
| `test_harness.py` | Agent loop with MockBackend |
| `test_sandbox.py` | Docker execution, timeout, OOM |
| `test_gateway.py` | REST endpoints via TestClient |
| `test_integration.py` | Full stack with Docker sandbox |
| `test_websocket.py` | Real-time streaming |
| `test_calculator_tool.py` | Math evaluation |
| `test_fetch_tool.py` | HTTP mocking |
| `test_file_tools.py` | Read/write + path traversal |
| `test_shell_tool.py` | Docker shell execution |
| `test_plot_tool.py` | Matplotlib base64 output |

---

##  Project Structure

```
ai-agent-platform/
├── common/
│   └── models.py              # Shared Pydantic v2 types
├── sdk/
│   ├── __init__.py
│   ├── client.py              # AgentClient (httpx)
│   └── builder.py             # AgentBuilder (fluent API)
├── gateway/
│   ├── main.py                # FastAPI app entrypoint
│   ├── routes.py              # REST endpoints
│   ├── websocket.py           # WebSocket streaming
│   └── dependencies.py        # In-memory stores
├── harness/
│   ├── state.py               # ConversationState
│   ├── registry.py            # ToolRegistry + Tool class
│   ├── llm.py                 # LLMBackend (Mock + OpenAI)
│   ├── runner.py              # AgentRunner (the loop)
│   └── tools/
│       ├── math_tool.py       # Fibonacci calculator
│       ├── code_tool.py       # Docker Python executor
│       ├── calculator_tool.py # Safe math evaluator
│       ├── fetch_tool.py      # HTTP fetcher
│       ├── file_tools.py      # Sandboxed read/write
│       ├── shell_tool.py      # Docker shell executor
│       └── plot_tool.py       # Matplotlib plot generator
├── sandbox/
│   └── docker_sandbox.py      # Docker container manager
├── tests/
│   ├── test_sdk.py
│   ├── test_harness.py
│   ├── test_sandbox.py
│   ├── test_gateway.py
│   ├── test_integration.py
│   ├── test_websocket.py
│   ├── test_calculator_tool.py
│   ├── test_fetch_tool.py
│   ├── test_file_tools.py
│   ├── test_shell_tool.py
│   └── test_plot_tool.py
├── demo.py                    # End-to-end demo script
├── README.md                  # This file
└── pyproject.toml             # Dependencies
```

---

##  License

MIT
