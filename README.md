# 🚀 Nova AI

> An end-to-end, production-grade Agentic AI platform featuring asynchronous
> Server-Sent Events (SSE) streaming, sandboxed code execution, multi-agent
> collaboration, hybrid RAG with HyDE and Reciprocal Rank Fusion (RRF),
> thread-safe Human-in-the-Loop (HITL) controls, OpenRouter-powered multimodal
> model orchestration, ephemeral session-aware file handling, and an interactive
> Next.js 15 interface.

Nova AI is an extensible AI Agent framework built from first principles using
Python, FastAPI, and OpenRouter-powered models. Rather than relying on rigid
abstractions or wrapping simple prompt chains, Nova AI directly implements
reasoning, dynamic tool selection, dependency-aware multi-agent supervision,
safe code execution, document retrieval, session-aware artifact handling, and
live UI stream coordination.

---

## 🏗️ System Architecture & Data Flow

Nova AI connects an asynchronous web layer, event streaming, persistent
conversation memory, an ephemeral session store, and isolated execution
sandboxes across a clean client-server boundary.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Frontend: Next.js 15 + Tailwind CSS                    │
│                      (Hosted at http://localhost:3000)                      │
└──────────────┬──────────────────────────────┬───────────────────────────────┘
               │ POST /api/chat               │ GET /api/chat/:id/events (SSE)
               ▼                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Application Gateway                          │
│                        (Hosted at http://localhost:8000)                    │
│                                                                             │
│   ├── routes/chat.py ─────────► SessionEventManager (asyncio.Queue)         │
│   ├── routes/conversations.py ─► SQLiteMemory (Conversation Memory)         │
│   ├── Session Store ───────────► Ephemeral File / Artifact Buffers          │
│   └── HITLManager ────────────► threading.Event (Approval Interlock)        │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ asyncio.to_thread
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MultiAgentOrchestrator (Supervisor Loop)                    │
│                                                                             │
│   Shared Context / Blackboard Bus ◄─────────► Plan & Decompose Engine       │
│                     │                                                       │
│                     └──── Dependency-Aware Task Graph                       │
└───────┬──────────────────────┬──────────────────────┬───────────────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌──────────────┐       ┌───────────────┐       ┌───────────────────────────────┐
│ResearchAgent │       │  DataAnalyst  │       │DocVisionAgent                 │
│(Web/Weather) │       │(Python/Pandas)│       │(ChromaDB RAG / Multimodal LLM)│
└──────┬───────┘       └──────┬────────┘       └─────────────┬─────────────────┘
       │                      │                              │
       ▼                      ▼                              ▼
┌──────────────┐       ┌──────────────┐       ┌───────────────────────────────┐
│Tavily / wttr │       │Docker / E2B  │       │ChromaDB + BM25 (RRF + HyDE)   │
│Search Tools  │       │Code Sandbox  │       │OpenRouter Multimodal Models   │
└──────────────┘       └──────────────┘       └───────────────────────────────┘

                         ┌──────────────────────────┐
                         │      Session Store       │
                         │  Uploaded Files          │
                         │  Generated Charts        │
                         │  Generated CSV Artifacts │
                         │  Base64 Buffers          │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                              artifact_generated
                                      │
                                      ▼
                         Inline UI Rendering + Download
```

### Runtime Architecture Principles

- **Provider Decoupling**: LLM orchestration is routed through OpenRouter rather
  than being tied to a single model provider.
- **Session-Aware File Handling**: Uploaded files and generated artifacts are
  associated with the active session instead of a physical shared workspace.
- **Stateless Deployment**: The agent/file pipeline is designed without
  dependence on a persistent `nova_workspace/` directory, making it suitable
  for stateless environments such as Railway and Vercel.
- **Sandboxed Execution**: Python workloads can run in isolated Docker or E2B
  environments.
- **Event-Driven UI**: Agent progress, approvals, tool results, completion
  states, and artifacts are streamed to the frontend through SSE.

---

## ✨ Key Features & Architectural Highlights

### 🧠 OpenRouter-Powered Reasoning & Multimodal Models

- **OpenRouter Integration**: Centralizes model access behind the OpenRouter API,
  reducing provider lock-in and allowing Nova to use specialized models.
- **Primary Reasoning Model**: Standardized on
  `deepseek/deepseek-v4.1-flash` for text reasoning, decomposition, and planning.
- **Dynamic Multimodal Fallback**: Model selection can fall back to multimodal
  models for chart and image inspection when required.
- **Structured Tool Contracts**: Pydantic-backed tool definitions constrain
  model-generated tool inputs and outputs.

### ⚡️ Asynchronous Server-Sent Events (SSE) Streaming

- **Non-Blocking Task Dispatch**: Dispatches long-running agent workflows via
  `asyncio.to_thread` and `asyncio.create_task`, allowing the API to return
  immediate acknowledgments (`status: "started"`).
- **Live Event Streaming**: Bridges internal `NovaEvent` objects into an
  in-memory `asyncio.Queue`, pushing planning, task dispatch, tool execution,
  agent completion, reflection, and final-answer events over
  `text/event-stream`.
- **Artifact Streaming**: Generated charts and CSV files are emitted through
  `artifact_generated` events as base64 payloads.
- **Compact UI Context**: Bulky UI event history is truncated/sanitized before
  being fed back into the supervisor context.

### 🛡️ Human-in-the-Loop (HITL) Concurrency Bridge

- **Thread-Safe Pause & Resume**: When an agent attempts an action flagged as
  sensitive or destructive, its worker thread pauses using a `threading.Event`.
- **Zero Event-Loop Blockage**: The FastAPI async event loop remains responsive
  while the worker waits for approval.
- **UI Approval Flow**: Operators can approve or deny pending actions directly
  from the UI through the approval endpoint.
- **Automatic Denial**: Pending approvals default to denial after the configured
  timeout.

### 🤝 Multi-Agent Supervision & Dependency-Aware Execution

- **Supervisor Agent (`MultiAgentOrchestrator`)**: Performs intent
  classification, decomposes complex requests, and delegates subtasks to
  specialized workers.
- **Dependency Graph Sequencing**: Downstream tasks are dispatched only when
  their required upstream dependencies are available.
- **Dependency Safeguards**: Failed or blocked upstream tasks prevent dependent
  subtasks from executing.
- **Research Agent**: Collects live external knowledge via Tavily web search
  and structured `wttr.in` weather data.
- **Data Analyst Agent**: Generates Python scripts and executes data workflows
  with Pandas, NumPy, Matplotlib, and SymPy inside a sandbox.
- **Document & Vision Specialist**: Retrieves knowledge through hybrid RAG and
  inspects generated images/charts using multimodal models.

### 🔬 Advanced Hybrid RAG Engine

- **HyDE (Hypothetical Document Embeddings)**: Generates a hypothetical answer
  to map ambiguous queries into the embedding document space.
- **Dense Vector Search**: Powered by ChromaDB and SentenceTransformers
  (`all-MiniLM-L6-v2`).
- **Lexical Keyword Search**: Powered by Rank-BM25 for exact keyword matching.
- **Reciprocal Rank Fusion (RRF)**: Combines dense and sparse rankings to
  produce stronger grounded context.
- **Hardened PDF Ingestion**: Uses PyMuPDF (`fitz`) for browser-uploaded PDFs,
  avoiding fragile stream decompression and catalog parsing failures.
- **Validated Background Ingestion**: Documents are validated before being
  ingested into the ChromaDB vector store.

### 🗂️ Ephemeral Session Store & Filesystem Decoupling

- **No Physical `nova_workspace` Dependency**: Nova no longer requires a local
  `nova_workspace/` directory for uploaded files or generated outputs.
- **Centralized Session Store**: Uploaded files and sandbox artifacts are managed
  as ephemeral, session-scoped base64 buffers.
- **Sandbox Output Capture**: Docker and E2B execution paths capture generated
  figures and datasets directly from execution results/stdout.
- **No Host-Disk Artifact Saves**: Generated charts and CSV outputs can flow
  directly from sandbox → session store → SSE → frontend.
- **Deployment Friendly**: Removing filesystem assumptions makes the runtime
  better suited to stateless hosting environments.

### 🐳 Sandboxed Code Execution

- **Docker Runtime**: Executes Python workloads inside the custom
  `nova-sandbox:latest` image with resource and timeout controls.
- **E2B Runtime**: Supports remote sandbox execution for environments where
  isolated cloud execution is preferred.
- **Safe Output Handling**: Large stdout and DataFrame representations are
  capped before model ingestion.
- **Artifact Extraction**: Figures and datasets are extracted from execution
  results instead of requiring persistent host filesystem paths.

### 🎨 Frontend Artifact Rendering & UX

- **Inline Chart Rendering**: Generated chart artifacts are rendered directly
  inside the chat turn.
- **One-Click Downloads**: Users can download generated charts and CSV artifacts
  directly from the conversation.
- **Optimistic File List Updates**: The session file list updates immediately
  after user uploads instead of waiting for a full refresh.
- **Live Activity Timeline**: The UI surfaces planning, task breakdown,
  dispatch, tool calls, approvals, agent completion, and artifact events.
- **Session-Aware Uploads**: CSV, PDF, and TXT files are attached to the active
  session without relying on a shared local directory.

---

## 📡 API Reference

Nova AI's FastAPI gateway exposes the following REST and streaming endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health-check endpoint verifying API server status. |
| `POST` | `/api/chat` | Dispatches a query asynchronously to the agent orchestrator and returns a session acknowledgment. |
| `GET` | `/api/chat/{session_id}/events` | Real-time SSE stream yielding planning, tool, agent, approval, artifact, and final-answer events. |
| `POST` | `/api/chat/{session_id}/approval` | Resolves a pending HITL confirmation (`approved=true/false`). |
| `GET` | `/api/conversations` | Lists available conversation sessions and metadata from the conversation store. |
| `GET` | `/api/conversations/{session_id}` | Retrieves full turn-by-turn chat history for a session. |

Interactive Swagger documentation is automatically hosted at:

```text
http://localhost:8000/docs
```

---

## 📂 Project Directory Structure

```text
nova-ai/
├── api/                            # FastAPI HTTP & Real-Time Gateway
│   ├── core/                       # Concurrency managers (HITL, session event queues)
│   │   ├── __init__.py
│   │   ├── hitl_manager.py
│   │   └── session_events.py       
│   │
│   ├── routes/                     # Route handlers (/chat, /conversations)
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── conversations.py
│   │   └── workspace.py
│   │
│   ├── schemas/                    # Pydantic request/response validation schemas
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── conversations.py
│   │   └── workspace.py
│   │
│   ├── services/                   # Orchestrator and persistent memory service bridges
│   │   ├── __init__.py
│   │   ├── conversation_service.py
│   │   ├── nova_services.py
│   │   └── workspace_service.py
│   │
│   ├── __init__.py
│   └── main.py                     # FastAPI entry point & CORS configuration
│
├── app/                            # Core Agent Engine & Logic
│   ├── agents/                     # Multi-agent worker nodes (BaseAgent, Specialists)
│   │   ├── __init__.py
│   │   ├── base_agent.py           # Base specialist abstraction
│   │   └── specialists.py          # ResearchAgent, DataAnalystAgent, DocVisionAgent
│   │
│   ├── core/                       # Memory (SQLite), EventBus, SharedContext, Workspace
│   │   ├── __init__.py
│   │   ├── event_bus.py
│   │   ├── event.py
│   │   ├── hyde.py                 # HyDE query generation
│   │   ├── memory.py               # Persistent SQLite memory
│   │   ├── session_store.py
│   │   ├── shared_context.py       # Inter-agent blackboard memory bus
│   │   ├── workspace_manager.py    # Workspace sandbox management
│   │
│   ├── tools/                      # CodeInterpreter, WebSearch, Inspection, RAG Search
│   │   ├── __init__.py
│   │   ├── code_interpreter.py
│   │   ├── knowledge_base_search.py
│   │   ├── weather.py
│   │   ├── web_search.py
│   │   └── workspace_tools.py
│   │
│   ├── config.py                   # Environment settings and model constants
│   ├── main.py
│   ├── models.py                   # Structured Pydantic tools and agent models
│   ├── orchestrator.py             # Multi-Agent Supervisor / Orchestration loop
│   ├── prompts.py
│   ├── single_agent.py             # Standalone ReAct Single-Agent Loop
│   └── utils.py
│
├── data/
│   ├── vector_db/
│   └── nova_memory.db
│
├── frontend/
│   └── app/
│
├── rag/
│   └── ingest_pdf.py
│
├── tests/
│   ├── test_eval_suite.py          # Single-agent evaluation benchmark
│   └── test_multi_agent.py         # Multi-agent collaboration benchmark
│
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
└── sandbox.dockerfile
```

> `nova_workspace/` and the legacy `workspace_watcher.py` are deprecated.
> Runtime uploads and generated artifacts are now handled by the centralized
> session store rather than a physical shared workspace.
>
> `data/nova_memory.db` stores Nova AI's conversation/persistent memory.
>
> `data/vector_db/` contains the local ChromaDB vector store used by Nova AI's
> RAG pipeline.

---

## 🛠️ Tech Stack

### AI & Agent Core

- **LLM Provider**: OpenRouter
- **Primary Reasoning Model**: `deepseek/deepseek-v4.1-flash`
- **Multimodal Model Access**: OpenRouter multimodal model routing/fallback
- **Agent Orchestration**: Custom Python Multi-Agent Supervisor
- **Tool Contracts**: Pydantic v2
- **Prompting**: Supervisor, Specialist, and Synthesis system prompts with
  closed-world tool compliance and dependency sequencing

### Backend & Streaming

- **Python**: 3.11+
- **API**: FastAPI + Uvicorn
- **Async Runtime**: asyncio + AnyIO
- **Streaming**: Server-Sent Events (SSE)
- **Event Coordination**: In-memory `asyncio.Queue`
- **Human Approval**: Thread-safe `threading.Event`

### Frontend

- **Next.js**: 15
- **React**: 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Artifact UX**: Inline base64 chart rendering + client-side downloads

### RAG & Document Processing

- **Vector Database**: ChromaDB
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **Lexical Search**: Rank-BM25
- **Retrieval**: HyDE + Dense Search + BM25 + RRF
- **PDF Extraction**: PyMuPDF (`fitz`)
- **Text Splitting**: LangChain Text Splitters

### Data Science & Sandboxing

- **Execution**: Docker + E2B
- **Data**: Pandas + NumPy
- **Visualization**: Matplotlib + Seaborn
- **Symbolic Math**: SymPy

### Storage & Runtime State

- **Conversation Memory**: SQLite-backed memory layer
- **Session File State**: Ephemeral in-memory session store
- **Artifacts**: Base64 buffers streamed over SSE

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ & npm
- Docker Desktop (required for Docker-based isolated execution)
- OpenRouter API key
- Tavily API key
- E2B API key if the E2B execution backend is enabled

### 1. Clone the Repository

```bash
git clone https://github.com/dhruvshingala30/nova-ai.git
cd nova-ai
```

### 2. Configure Environment Variables

Create `.env` in the project root:

```text
ENVIRONMENT=development

OPENROUTER_API_KEY=your_openrouter_api_key
MODEL_NAME=deepseek/deepseek-v4.1-flash

TAVILY_API_KEY=your_tavily_api_key
E2B_API_KEY=your_e2b_api_key
```

If E2B is not enabled in your configuration, its API key is not required.

---

To obtain a Tavily API key:

1. Visit <https://tavily.com>
2. Sign up for an account.
3. Generate an API key from the dashboard.
4. Copy it into your `.env` file.

---

To obtain a OpenRouter API key:

1. Visit <https://openrouter.ai>
2. Sign up for an account.
3. Go to the API Keys section.
4. Click Create Key / Create API Key.
5. Give it a name, for example:

```text
NovaAI Development
```

- Set a spending/credit limit if offered. OpenRouter recommends setting a limit on keys so a leaked key or runaway agent cannot consume your entire balance. GitHub
- Create the key.
- Copy it immediately and store it somewhere safe. OpenRouter's API documentation says the plaintext key is only returned when it is created. OpenRouter
It will look roughly like:

```text
sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx
```

Put it in Nova's .env

```text
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx
MODEL_NAME=deepseek/deepseek-v4.1-flash
```

Your OpenRouter endpoint is:
<https://openrouter.ai/api/v1>

---

To obtain a OpenRouter API key:

1. Visit <https://e2b.dev>
2. Sign up / log in.
3. Open your E2B Console/Dashboard.
4. Find the API Keys section.
5. Create a new API key.
6. Give it a useful name, e.g.:

```text
NovaAI Development
```

- Copy the generated key.
E2B's documentation/examples use the environment variable:

```env
E2B_API_KEY=your_e2b_api_key
``` :chatgpt-content-reference{index="8"}


---

# 3. Your Nova `.env` should now look like this

```env
ENVIRONMENT=development

# LLM
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
MODEL_NAME=deepseek/deepseek-v4.1-flash

# Web Search
TAVILY_API_KEY=xxxxxxxxxxxxxxxx

# Cloud Code Sandbox
E2B_API_KEY=xxxxxxxxxxxxxxxx
```

---

The Weather Tool uses the free `wttr.in` service and does not require an API key.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The first RAG query may download the configured SentenceTransformers
embedding model from Hugging Face. Subsequent runs use the locally cached model.

### 4. Build the Docker Execution Sandbox

Build the container image used for isolated script execution:

```bash
docker build -f sandbox.dockerfile -t nova-sandbox:latest .
```

### 5. Ingest Knowledge Base Documents (Optional RAG Setup)

Provide reference PDFs through Nova's session/file-upload pipeline and run the
vector ingestion workflow:

```bash
python rag/ingest_pdf.py
```

The ingestion pipeline uses PyMuPDF (`fitz`) and validation guards before
routing extracted content into ChromaDB.

---

## 💻 Running the Application

### Option A: Local Development

#### Terminal 1 — FastAPI Backend Gateway

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

uvicorn api.main:app --reload --port 8000
```

#### Terminal 2 — Next.js Frontend UI

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

to interact with Nova AI.

### Option B: Docker Compose

```bash
docker compose up --build
```

> Nova's application runtime no longer requires a persistent
> `nova_workspace/` directory for user uploads or generated artifacts.

---

## 💬 Interactive Query Examples

### 1. Data Analysis & Chart Generation

```text
You:
Inspect happy.csv from my session and compare GDP, happiness,
and life expectancy. Generate a chart and explain the result.

Nova AI:
1. Inspected the CSV schema.
2. Planned the required analysis and dependent subtasks.
3. Generated and executed Python code inside a sandbox.
4. Captured the generated chart as a session artifact.
5. Streamed the chart through SSE.
6. Rendered the chart inline in the chat with a download option.
7. Used a multimodal model to inspect the generated chart.
```

### 2. Multi-Agent Cross-Domain Collaboration

```text
You:
Find the current weather in Tokyo and Berlin, calculate the
temperature delta in Python, and tell me which is colder.

Nova AI:
Supervisor formulated dependent subtasks:
  - ResearchAgent: Retrieve live weather for both cities.
  - DataAnalystAgent: Calculate the temperature delta.
  - Supervisor: Synthesize the final answer.

Result:
Berlin is currently colder than Tokyo by the calculated delta.
```

### 3. Human-in-the-Loop Approval

```text
You:
Generate a chart and save the resulting image artifact.

Nova AI:
⚠️ HUMAN APPROVAL REQUIRED

Action:
Generate / save a chart artifact using run_python_code.

UI:
[ Approve ]    [ Deny ]

After approval:
  approval_granted
      ↓
  tool_result
      ↓
  agent_completed
      ↓
  artifact_generated
      ↓
  Inline chart rendering + download
```

### 4. Document + Vision Workflow

```text
You:
Search my uploaded PDF for the relevant section,
then inspect the generated chart and explain its visual trends.

Nova AI:
1. Ingests the uploaded PDF.
2. Retrieves relevant context using HyDE + vector search + BM25 + RRF.
3. Generates the requested analysis.
4. Produces a chart artifact in the sandbox.
5. Inspects the chart with a multimodal model.
6. Synthesizes the document and visual findings into one answer.
```

---

## 🔄 Runtime Event Flow

Nova's frontend receives a live event stream representing the lifecycle of
an agent workflow:

```text
session_created
      ↓
plan_created
      ↓
subtask_dispatched
      ↓
tool_invocation
      ↓
tool_result
      ↓
reflection
      ↓
agent_completed
      ↓
artifact_generated
      ↓
synthesis_started
      ↓
final_answer
```

When a sensitive operation requires user intervention:

```text
tool_invocation
      ↓
approval_required
      ↓
      ├── approval_granted ──► tool_result
      │
      └── approval_denied ───► subtask_skipped / failure handling
```

The event pipeline allows the UI to expose Nova's execution process rather than
only showing the final response.

---

## 🛡️ Reliability & Safety Matrix

- **Closed-World Tool Compliance**: Agent prompts and Pydantic tool contracts
  restrict models to the tools and inputs explicitly available to them.
- **Dependency Graph Safeguards**: Dependent subtasks are skipped when required
  upstream work fails or is blocked.
- **Prompt Sanitization**: Supervisor, specialist, and synthesis prompts no
  longer contain obsolete local-directory assumptions.
- **Planner Context Sanitization**: Supervisor planning history is compacted
  before reuse to preserve reasoning context.
- **Event Log Truncation**: Bulky UI event payloads are capped before entering
  model context.
- **Session Isolation**: Uploaded files and generated artifacts are scoped to
  the active session.
- **Sandbox Isolation**: Code executes inside isolated Docker and/or E2B
  environments.
- **Artifact Isolation**: Generated files are returned through the session
  pipeline rather than requiring persistent host paths.
- **Output Truncation**: Stdout and large DataFrame representations are capped
  before model ingestion.
- **HITL Fail-Safe**: Pending approval requests default to denial after timeout.

---

## ☁️ Stateless Deployment Readiness

Nova's latest architecture removes the assumption that an agent session needs
a persistent local workspace.

The runtime now follows:

```text
User Upload
    ↓
Session Store
    ↓
Agent / RAG / Sandbox
    ↓
Base64 Artifact
    ↓
SSE artifact_generated Event
    ↓
Next.js UI
    ↓
Inline Render / Client Download
```

This architecture is designed to simplify deployment to stateless platforms
such as **Railway** and **Vercel**, where relying on a durable local filesystem
is fragile or unavailable.

The conversation-memory layer remains separate from the ephemeral session
artifact layer, keeping file handling and long-lived conversation state
decoupled.

---

## 🤝 Contributing

Contributions, suggestions, and ideas are always welcome.

If you find this project interesting, consider giving it a ⭐ to support its
development.

---

## 📄 License

This project is licensed under the MIT License.
