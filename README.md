# 🚀 Nova AI

> An end-to-end, production-grade Agentic AI platform featuring asynchronous
> Server-Sent Events (SSE) streaming, Docker-sandboxed execution, multi-agent
> collaboration, hybrid RAG with HyDE and Reciprocal Rank Fusion (RRF),thread-safe
> Human-in-the-Loop (HITL) controls, and an interactive Next.js 15 interface.

Nova AI is an extensible AI Agent framework built from first principles using
Python, FastAPI, and local LLMs (via Ollama). Rather than relying on rigid
abstractions or wrapping simple prompt chains, Nova AI directly implements
reasoning, dynamic tool selection, multi-agent supervision, safe code execution,
persistent cross-session memory, and live stream coordination.

---

## 🏗️ System Architecture & Data Flow

Nova AI connects an asynchronous web layer, an event bus, persistent memory,
and isolated execution sandboxes across a clean client-server boundary:

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
│   ├── routes/conversations.py ─► SQLiteMemory (Persistent Sessions)         │
│   └── HITLManager ────────────► threading.Event (Approval Interlock)        │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ asyncio.to_thread
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MultiAgentOrchestrator (Supervisor Loop)                    │
│                                                                             │
│   Shared Context / Blackboard Bus ◄─────────► Plan & Decompose Engine       │
└──────┬──────────────────────┬──────────────────────┬────────────────────────┘
       │                      │                      │
       ▼                      ▼                      ▼
┌──────────────┐       ┌──────────────┐       ┌───────────────────────────────┐
│ResearchAgent │       │DataAnalyst   │       │DocVisionAgent                 │
│(Web/Weather) │       │(Python/Pandas│       │(ChromaDB RAG / LLaVA Vision)  │
└──────┬───────┘       └──────┬───────┘       └──────┬────────────────────────┘
       │                      │                      │
       ▼                      ▼                      ▼
┌──────────────┐       ┌──────────────┐       ┌───────────────────────────────┐
│Tavily / wttr │       │Docker Sandbox│       │ChromaDB + BM25 (RRF + HyDE)   │
│Search Tools  │       │(Python 3.11) │       │Ollama Multimodal Engine       │
└──────────────┘       └──────────────┘       └───────────────────────────────┘
```

---

## ✨ Key Features & Architectural Highlights

### ⚡️ Asynchronous Server-Sent Events (SSE) Streaming

- **Non-Blocking Task Dispatch**: Dispatches long-running agent workflows
  via `asyncio.to_thread` and `asyncio.create_task`, allowing the API to
  return immediate acknowledgments (`status: "started"`).
- **Live Token & Event Streaming**: Bridges internal `NovaEvent` objects
  into an in-memory `asyncio.Queue` via `EventCollector`, pushing thoughts,
  tool execution steps, and tokens over a `text/event-stream` connection.

### 🛡️ Human-in-the-Loop (HITL) Concurrency Bridge

- **Thread-Safe Pause & Resume**: When an agent attempts an action flagged as
  sensitive or destructive, it pauses its worker thread using a `threading.Event`.
- **Zero Event-Loop Blockage**: The FastAPI async event loop remains fully responsive
  to incoming health checks and requests while the worker thread awaits approval.
- **UI Resolution & Auto-Denial**: Operators approve or deny operations via
  `POST /api/chat/{session_id}/approval`, with an automatic 300-second
  timeout default to deny unacknowledged tasks.

### 🤝 Multi-Agent Supervision & Worker Network

- **Supervisor Agent (`MultiAgentOrchestrator`)**: Performs intent classification,
  breaks down multi-step tasks into sub-plans, and delegates them to specialized workers.
- **Research Agent**: Collects live external knowledge via Tavily web search and
  structured `wttr.in` weather data.
- **Data Analyst Agent**: Generates Python scripts and executes data science workflows
  with Pandas, NumPy, Matplotlib, and SymPy inside an isolated container.
- **Document & Vision Specialist**: Ingests files, runs hybrid vector-keyword retrieval (RAG),
  and visually inspects images/charts with local vision models.

### 🔬 Advanced Hybrid RAG Engine

- **HyDE (Hypothetical Document Embeddings)**: Generates a theoretical answer to map ambiguous
  queries into the embedding document space.
- **Dense Vector Search**: Powered by ChromaDB and `SentenceTransformers` (`all-MiniLM-L6-v2`).
- **Lexical Keyword Search**: Powered by Rank-BM25 to guarantee exact keyword matches.
- **Reciprocal Rank Fusion (RRF)**: Combines dense vector rankings with sparse keyword
  rankings to deliver grounded context.

### 🐳 Sandboxed Code Execution & Workspace Guardrails

- **Isolated Docker Runtime**: Executes arbitrary code safely inside a custom
  `nova-sandbox:latest` container with memory and timeout limits.
- **Path-Traversal Guards**: `WorkspaceManager` verifies and resolves all relative paths within
  `nova_workspace/` to protect host filesystem integrity.
- **Smart Output Capping**: Truncates large DataFrames and matrix prints to prevent context-window overflow.

### 📡 API Reference

Nova AI's FastAPI gateway exposes the following REST and streaming endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health-check endpoint verifying API server status. |
| `POST` | `/api/chat` | Dispatches query asynchronously to agent orchestrator; returns session acknowledgment. |
| `GET` | `/api/chat/{session_id}/events` | Real-time SSE stream yielding thoughts, tool logs, and agent tokens (`text/event-stream`). |
| `POST` | `/api/chat/{session_id}/approval` | Resolves thread-locked HITL confirmation (`approved=true/false`). |
| `GET` | `/api/conversations` | Lists stored conversation sessions and metadata from SQLite storage. |
| `GET` | `/api/conversations/{session_id}` | Retrieves full turn-by-turn chat history for a session. |

Interactive Swagger documentation is automatically hosted at `http://localhost:8000/docs`.

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
│   │   └── conversations.py
│   │
│   ├── schemas/                    # Pydantic request/response validation schemas
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── conversations.py
│   │
│   ├── services/                   # Orchestrator and persistent memory service bridges
│   │   ├── __init__.py
│   │   ├── conversation_service.py
│   │   └── nova_services.py
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
│   │   ├── hyde.py                 # HyDE query generation
│   │   ├── memory.py               # Persistent SQLite memory
│   │   ├── shared_context.py       # Inter-agent blackboard memory bus
│   │   ├── workspace_manager.py    # Workspace sandbox management
│   │   └── workspace_watcher.py    # Automatic file monitoring
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
├── nova_workspace/
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

> `nova_workspace/` is created dynamically at runtime and is used as Nova AI's shared file workspace.
> `data/nova_memory.db` stores Nova AI's persistent SQLite memory.
> `data/vector_db/` contains the local ChromaDB vector store used by Nova AI's RAG pipeline.

---

## 🛠️ Tech Stack

- **LLM & Vision Runtime**: Ollama (`qwen2.5:7b`, `llava`).
- **Backend Core**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, AnyIO, asyncio.
- **Frontend**: Next.js 15 (App Router, React 19), TypeScript, Tailwind CSS.
- **RAG & Vector Search**: ChromaDB, SentenceTransformers (`all-MiniLM-L6-v2`),
  Rank-BM25, LangChain Text Splitters, pdfplumber.
- **Data Science & Sandboxing**: Docker, Pandas, NumPy, Matplotlib, Seaborn, SymPy, Watchdog.
- **Memory & Storage**: SQLite3.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ & npm
- Docker Desktop (Required for isolated code interpreter)
- Ollama

### 1. Clone the Repository

```bash
git clone https://github.com/dhruvshingala30/nova-ai.git
cd nova-ai
```

### 2. Configure Environment Variables

Create `.env` in the project root:

```text
ENVIRONMENT=development
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=qwen2.5:7b
VISION_MODEL_NAME=llava
TAVILY_API_KEY=your_tavily_api_key
```

To obtain a Tavily API key:

1. Visit <https://tavily.com>
2. Sign up for an account.
3. Generate an API key from the dashboard.
4. Copy it into your `.env` file.

> **Note:** The Weather Tool uses the free `wttr.in` service and does not require an API key.

### 3. Pull Required Models via Ollama

```bash
ollama pull qwen2.5:7b-instruct-q8_0
ollama pull llava
```

> **Note:** The first RAG query may download the configured Sentence Transformers embedding model from Hugging Face. Subsequent runs use the locally cached model.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Build Code Execution Sandbox

Build the container image used for secure script execution:

```bash
docker build -f sandbox.dockerfile -t nova-sandbox:latest .
```

### 6. Ingest Knowledge Base Documents (Optional RAG Setup)

Place reference documents (e.g. `manual.pdf`) into `nova_workspace/` and run the vector ingestion pipeline:

```bash
python rag/ingest_pdf.py
```

---

## 💻 Running the Application

### Option A: Local Development (Recommended)

**Terminal 1 — FastAPI Backend Gateway:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Next.js Frontend UI:**

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser to interact with Nova AI.

### Option B: Docker Compose

Spin up the containerized architecture with a single command:

```bash
docker compose up --build
```

### Run Nova AI

```bash
python main.py
```

---

## 💬 Interactive Query Examples

### 1. Data Analysis & Chart Generation

```text
You: 
Inspect happy.csv from my workspace and plot GDP vs Happiness as a scatter plot.

Nova AI:
1. Inspected schema of happy.csv (Columns: country, gdp, happiness)
2. Generated visualization script using Matplotlib inside Docker sandbox
3. Saved generated chart to nova_workspace/gdp_vs_happiness.png
4. Inspected chart using LLaVA vision model: Confirmed strong positive correlation
```

### 2. Multi-Agent Cross-Domain Collaboration

```text
You: 
Find the current weather in Tokyo and Berlin, calculate the temperature delta in Python, and tell me which is colder.

Nova AI:
Supervisor formulated 2 subtasks:
  - Dispatched ResearchAgent: Tokyo = 24°C, Berlin = 14°C
  - Dispatched DataAnalystAgent: Evaluated abs(24 - 14) = 10°C delta in Docker sandbox
Synthesized Answer: Berlin is currently colder than Tokyo by 10°C.
```

### 3. Human-in-the-Loop File Mutation

```text
You: 
Add a 'verified' boolean column to users.csv and overwrite the original file.

Nova AI:
⚠️ [HITL SAFEGUARD - HUMAN APPROVAL REQUIRED]
Action: Overwrite workspace file 'users.csv'
Tool: run_python_code
Approve action? [Approve / Deny]
```

---

## 🛡️ Reliability & Safety Matrix

- **Path Traversal Guardrails**: Sandboxed workspace utilities enforce strict path resolution inside `nova_workspace/`.
- **Container Isolation**: Code runs exclusively in ephemeral, non-root Docker sandboxes.
- **Output Truncation**: Stdout and DataFrame representations are automatically capped before model ingestion.
- **Deterministic Fail-Safes**: All pending HITL requests automatically default to denial upon timeout.

---

## 🤝 Contributing

Contributions, suggestions, and ideas are always welcome.

If you find this project interesting, consider giving it a ⭐ to support its development.

---

## 📄 License

This project is licensed under the MIT License.
