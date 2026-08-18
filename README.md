# 🚀 Nova AI

> A modular Agentic AI framework that reasons, remembers, retrieves knowledge, analyzes data, executes code safely, and uses external tools through local LLMs.

Nova AI is an extensible AI Agent built with Python and local LLMs. Instead of relying only on language generation, Nova AI can reason about a user's request, decide whether external tools are required, execute them, observe the results, and generate accurate, grounded responses.

The project is being developed incrementally to understand and implement the core building blocks of modern AI agents from first principles.

---

## ✨ Current Features

### 🌤️ Weather Tool

Ask for the weather of one or multiple cities.

#### Examples - Weather Tool

```text
What's the weather in Ahmedabad?
```

```text
Compare the weather of Mumbai, Delhi and Bangalore.
```

The agent automatically:

- Identifies the requested cities
- Calls the weather API
- Synthesizes the response into natural language

---

### 🌐 Web Search Tool

Nova AI can search the web whenever real-time or external information is required.

Powered by the Tavily Search API, the agent retrieves relevant sources and generates grounded responses.

#### Examples - Web Search Tool

```text
Latest AI news
```

```text
Who won the latest Formula 1 race?
```

```text
Summarize today's NVIDIA announcements.
```

The agent automatically:

- Detects when internal knowledge is insufficient
- Performs a web search
- Retrieves relevant sources
- Produces a concise, factual response

---

### 🧠 Persistent Memory

Nova AI remembers important information from previous conversations using SQLite, allowing it to retain relevant information across sessions.

Instead of treating every interaction as brand new, the agent can recall previously stored information whenever it is relevant.

#### Examples - Persistent Memory

```text
Remember that my favorite programming language is Python.
```

```text
What's my favorite programming language?
```

```text
Remember that I'm preparing for AI Engineer interviews.
```

The agent automatically:

- Extracts important long-term information
- Stores it in a SQLite database
- Retrieves relevant memories when needed
- Uses retrieved memories to produce personalized responses

---

### 📁 Shared File Workspace & Data Analysis

Nova AI provides a dedicated `nova_workspace` directory for working with user-provided files.

The workspace is created and managed automatically by the `WorkspaceManager`, allowing file-related operations to remain inside a dedicated workspace.

The workspace system provides:

- A dedicated `nova_workspace` directory
- Safe relative-path resolution
- Protection against path traversal
- Workspace file discovery and metadata inspection
- CSV and TSV schema inspection
- PDF content inspection
- Integration with the Local RAG Engine for semantic document retrieval
- Integration with the Python Code Execution Engine for data analysis

#### Workspace File Discovery

The `list_workspace_files` tool allows Nova AI to inspect the contents of the workspace and identify available files.

For each file, the agent can determine:

- Filename
- File extension
- File size

#### CSV / TSV Inspection

The `inspect_csv_schema` tool processes CSV and TSV files using Pandas and provides the LLM with:

- Column names
- Data types
- Sample rows

The inspected dataset can then be passed to the Code Execution Engine for further calculations, analysis, and visualization.

#### Examples - Shared File Workspace & Data Analysis

```text
You:
What files are in my workspace?

Nova AI:
The files in the workspace are:

- users.csv (67 B)
- happy.csv (5.7 KB)
```

```text
You:
Can you inspect happy.csv?

Nova AI:
The happy.csv file contains the following columns and data types:

- country: str
- happiness: int64
- gdp: int64
- social_support: int64
- life_expectancy: int64
- freedom_to_make_life_choices: int64
- generosity: int64
- corruption: int64
```

After inspecting the dataset, Nova AI can use the Code Execution Engine to perform calculations, statistical analysis, and visualizations.

---

### 👀 Workspace Auto-Ingestion

Nova AI now includes a workspace file watcher that monitors the `nova_workspace` directory for newly added or modified files.

The `WorkspaceWatcher` automatically detects workspace changes and can trigger the document ingestion pipeline without requiring manual ingestion commands for every new file.

This creates a more seamless workflow:

```text
User Adds File
      │
      ▼
nova_workspace/
      │
      ▼
Workspace Watcher
      │
      ▼
File Type Detection
      │
      ├── CSV / TSV
      │       ↓
      │   Data Analysis
      │
      └── PDF / Document
              ↓
          RAG Ingestion
              │
              ▼
          Vector Database
```

The watcher allows the workspace to behave more like a continuously available knowledge and data environment rather than a static directory.

The runtime logs confirm that workspace monitoring is active:

```text
[Workspace Watcher] Auto-ingestion active on: /app/nova_workspace
```

---

### 📄 PDF Inspection & Parsing

Nova AI can inspect PDF files stored inside the shared workspace and extract useful document-level information.

The `inspect_pdf_schema` tool provides the LLM with structured information about a PDF, including:

- Total page count
- PDF metadata
- Document title
- Author information
- Creator information
- Sample text extracted from selected pages

PDF inspection forms the document-processing layer of Nova AI, while the Local RAG Engine builds on this capability to index PDF content and retrieve relevant information semantically.

#### Example - PDF Inspection

```text
You:
Inspect Trading in the Zone by Mark Douglas.pdf

Nova AI:
The file 'Trading in the zone by Mark Douglas.pdf' contains the following details:

- Total Pages: 143
- Metadata:
  - Title: Trading in the Zone
  - Author: MaVeRiCk
  - Creator: calibre (5.17.0)
- Sample Text from Page 1:
  TRADING IN THE ZONE
- Sample Text from Page 2:
  MASTER THE MARKET WITH CONFIDENCE, DISCIPLINE AND A WINNING ATTITUDE...
```

The PDF inspection feature handles document-level metadata and text extraction, while the Local RAG Engine handles semantic indexing and retrieval from processed PDF content.

---

### 🔎 Local RAG Engine

Nova AI includes a local Retrieval-Augmented Generation (RAG) pipeline for querying indexed PDF documents.

The RAG engine uses:

- ChromaDB for persistent vector storage
- Sentence Transformers for semantic embeddings
- LangChain Text Splitters for document chunking
- pdfplumber for PDF text extraction

The `ingest_pdf.py` pipeline extracts text from PDF documents, splits the content into manageable chunks, generates embeddings, and stores the resulting vectors in a local ChromaDB collection.

The `search_knowledge_base` tool performs semantic similarity search against the indexed knowledge base and provides the most relevant document context to the LLM.

The initial RAG implementation uses dense semantic retrieval with ChromaDB.
This foundation has been extended with hybrid retrieval using BM25, RRF,
and HyDE.

---

### 🔬 Advanced RAG Retrieval

Nova AI's RAG architecture uses a hybrid retrieval pipeline that combines
dense semantic retrieval, BM25 lexical search, Reciprocal Rank Fusion (RRF),
and HyDE.

The enhanced retrieval architecture combines:

- Dense semantic retrieval using ChromaDB
- BM25 lexical retrieval
- Reciprocal Rank Fusion (RRF)
- HyDE (Hypothetical Document Embeddings)

The enhanced retrieval pipeline combines semantic similarity with
keyword-based relevance, improving retrieval quality for both conceptual
questions and queries containing specific terminology.

The enhanced retrieval flow is:

```text
                          User Query
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
                   HyDE            Original Query
                    │                   │
                    ▼                   ▼
          Hypothetical Document        BM25
                    │                   │
                    ▼                   │
             Dense Retrieval            │
                    │                   │
                 ChromaDB               │
                    │                   │
                    └─────────┬─────────┘
                              ▼
                    Reciprocal Rank Fusion
                            (RRF)
                              │
                              ▼
                        Ranked Context
                              │
                              ▼
                          Local LLM
                              │
                              ▼
                        Grounded Answer
```

#### Example - RAG Response

```text
You:
What does Mark Douglas say about market probabilities and risk?

Nova AI:
Mark Douglas emphasizes that trading requires a different mindset compared
to other aspects of life where we typically rely on skills learned over time.
He explains that traders must learn to think in terms of probabilities and
be willing to surrender conventional skills they have acquired in their
daily lives.
```

Nova AI retrieves relevant context from the locally indexed PDF before generating the answer.

The RAG engine allows Nova AI to answer questions using information retrieved from locally indexed documents rather than relying solely on the LLM's pre-trained knowledge.

---

### 🐍 Code Execution Engine

Nova AI includes a Docker-powered Code Execution Engine that enables the LLM to generate and execute Python code inside an isolated sandbox.

Instead of relying on dozens of manually implemented mathematical tools, Nova AI can generate Python code dynamically whenever a complex computational task is required.

The engine supports:

- Complex mathematical calculations
- Statistical and scientific computations
- Data manipulation and analysis
- Mathematical operations using SymPy
- Numerical computations using NumPy and SciPy
- Data analysis using Pandas
- Data visualization using Matplotlib and Seaborn
- Processing data from the shared workspace

#### Examples - Mathematical & Computational Tasks

```text
What is (245 × 97) / 13?
```

```text
Find the factorial of 100.
```

```text
Generate the first 50 Fibonacci numbers.
```

```text
Calculate the determinant of this matrix:
[[3, 5], [7, 2]]
```

```text
Solve this system of equations:

2x + 3y = 12
4x - y = 5
```

The agent automatically:

- Determines when computation is required
- Generates Python code
- Executes the code inside Docker
- Observes the output
- Returns the final answer

#### Docker Sandbox

The Code Execution Engine executes generated Python code inside a dedicated Docker image named `nova-sandbox:latest`.

The sandbox includes commonly used Python and data-science libraries pre-installed, including:

- Pandas
- NumPy
- Matplotlib
- Seaborn
- SymPy
- SciPy

Pre-installing these libraries allows generated code to execute without installing packages at runtime.

The execution environment also provides additional restrictions around generated code and system access, while the Docker container provides the primary isolation boundary for untrusted execution.

Generated code is executed inside the sandbox and the execution environment is removed after the task completes.

#### How the Code Execution Engine Is Used

The Code Execution Engine can be used directly for computational tasks or together with the Shared File Workspace for data-analysis tasks.

```text
User Request
     │
     ├── "Calculate determinant"
     │          ↓
     │    Code Execution Engine
     │
     ├── "Solve equations"
     │          ↓
     │    Code Execution Engine
     │
     ├── "Analyze happy.csv"
     │          ↓
     │    Workspace → Code Execution Engine
     │
     └── "Plot GDP vs Happiness"
                ↓
          Workspace → Code Execution Engine
```

This allows the same execution engine to handle both general-purpose computation and analysis of user-provided datasets.

---

#### Smart Execution Output

Nova AI applies output controls to prevent large Python executions from overwhelming the LLM context.

The Code Execution Engine can intelligently cap:

- Excessive stdout output
- Large DataFrame displays
- Oversized tabular results
- Unnecessary intermediate execution output

This allows Nova AI to work with large datasets and verbose Python programs while keeping the information passed back to the LLM compact and useful.

Instead of returning an entire dataset or thousands of printed lines, the execution layer provides a controlled representation of the result.

---

### 📋 Multi-Step Planning

Decomposes complex, multi-action queries into structured subtasks before calling tools.

---

### 💡 Autonomous Reflection & Error Recovery

Self-corrects when tool executions fail (e.g., missing data, syntax errors, or schema mismatches).

---

### 🛡️ Dynamic Human-in-the-Loop (HITL)

Automatically intercepts destructive disk writes, deletions, or file updates and requests human confirmation before proceeding.

---

## 🧠 How Nova AI Works

```text
┌─────────────────────────────────────────────────────────────────────┐
│                                 USER                                │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           LOCAL LLM · QWEN                          │
│                        Reason • Plan • Decide                       │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           TOOL ROUTER                               │
└───────┬───────────┬───────────┬───────────┬───────────────┬─────────┘
        │           │           │           │               │
        ▼           ▼           ▼           ▼               ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────────┐ ┌─────────────┐
   │ WEATHER │ │   WEB   │ │ MEMORY  │ │  WORKSPACE │ │ KNOWLEDGE   │
   │   API   │ │ SEARCH  │ │ SQLite  │ │   TOOLS    │ │    BASE     │
   └─────────┘ └─────────┘ └─────────┘ └─────┬──────┘ └──────┬──────┘
                                             │               │
                              ┌──────────────┴──────┐        │
                              ▼                     ▼        ▼
                         ┌─────────┐           ┌─────────┐ ┌──────────┐
                         │ CSV/TSV │           │   PDF   │ │   HyDE   │
                         │ Analysis│           │Parsing  │ │  Query   │
                         └────┬────┘           └────┬────┘ │Expansion │
                              │                     │      └────┬─────┘
                              │                     │           │
                              ▼                     ▼           ▼
                         ┌─────────────────┐   ┌──────────────────────┐
                         │ PYTHON CODE     │   │    HYBRID SEARCH     │
                         │  INTERPRETER    │   │                      │
                         │                 │   │ Dense + BM25 → RRF   │
                         └────────┬────────┘   └──────────┬───────────┘
                                  │                       │
                                  ▼                       ▼
                         ┌─────────────────┐       ┌─────────────┐
                         │ DOCKER SANDBOX  │       │   RANKED    │
                         │                 │       │   CONTEXT   │
                         │ Math • Science  │       └──────┬──────┘
                         │ Data • Charts   │              │
                         └────────┬────────┘              │
                                  │                       │
                                  └───────────┬───────────┘
                                              │
                                              ▼
                                ┌───────────────────────────┐
                                │        OBSERVATION        │
                                │   Tool Results + Context  │
                                └─────────────┬─────────────┘
                                                │
                                                ▼
                                ┌───────────────────────────┐
                                │     LOCAL LLM · QWEN      │
                                │    Reason • Synthesize    │
                                │   Combine Tool Results    │
                                └─────────────┬─────────────┘
                                                │
                                                ▼
                                ┌───────────────────────────┐
                                │         FINAL ANSWER      │
                                └───────────────────────────┘
```

The LLM is responsible for:

- Understanding user intent
- Selecting the appropriate tool
- Passing structured arguments
- Observing tool outputs
- Producing the final response

---

## 🛠️ Tech Stack

### 🤖 AI & Agent Core

- Ollama
- Pydantic
- AnyIO
- HTTPX

### 🌐 APIs & External Services

- Tavily Python SDK
- Requests
- python-dotenv

### 🧠 Memory & Retrieval

- SQLite
- ChromaDB
- Sentence Transformers
- rank-bm25

### 📄 Document Processing

- pypdf
- pdfplumber
- LangChain Text Splitters

### 📊 Data Analysis & Visualization

- Pandas
- NumPy
- Matplotlib
- SymPy

### 🐳 Code Execution & Workspace

- Docker
- Watchdog

### 🏗️ Architecture

- Local LLM inference with Ollama
- Tool Calling
- Pydantic Input Validation
- Persistent SQLite Memory
- Local Vector Database
- Hybrid Retrieval
- HyDE
- Reciprocal Rank Fusion (RRF)
- Automatic Workspace File Monitoring
- Docker-isolated Python Code Execution

---

## 🧩 Current Capabilities

Nova AI currently provides:

- 🌤️ Real-time weather information
- 🌐 Web search
- 🧠 Persistent SQLite memory
- 📁 Shared workspace management
- 👀 Automatic workspace file monitoring
- 📊 CSV / TSV inspection and analysis
- 📄 PDF inspection and parsing
- 🔎 Local semantic RAG
- 🔬 Hybrid RAG with Dense + BM25 retrieval
- 🔀 Reciprocal Rank Fusion (RRF)
- 🧠 HyDE query enhancement
- 🧮 General-purpose mathematical problem solving through Python
- 🐍 Dynamic Python code generation and execution
- 🐳 Docker-isolated code execution
- 📉 Smart execution-output capping
- 📚 Local vector knowledge storage
- 🔗 Multi-tool result synthesis
- 🧠 Observation-driven final answer generation
- 📋 Multi-step ReAct task planning and decomposition
- 💡 Autonomous reflection and self-correction on tool failures
- 🛡️ Dynamic Human-in-the-Loop confirmation for workspace modifications
- 🧪 Automated evaluation test suite for agent routing and safety

---

## 🛡️ Reliability & Safety

Nova AI is being designed with reliability and controlled execution as first-class concerns.

Current safeguards include:

- Docker-isolated Python execution
- Workspace path traversal protection
- Controlled Python execution output
- DataFrame output capping
- Structured tool inputs using Pydantic
- Workspace monitoring and controlled ingestion
- Automated agent evaluation
- Human-in-the-loop approval for sensitive operations
- Planning and reflection
- Tool execution validation

---

## 📂 Project Structure

```text
nova-ai/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── hyde.py                 # HyDE query generation
│   │   ├── memory.py               # Persistent SQLite memory
│   │   ├── workspace_manager.py    # Workspace management
│   │   └── workspace_watcher.py    # Automatic workspace monitoring
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── code_interpreter.py
│   │   ├── knowledge_base_search.py
│   │   ├── weather.py
│   │   ├── web_search.py
│   │   └── workspace_tools.py
│   │
│   ├── agent.py
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   ├── prompts.py
│   └── utils.py
│
├── data/
│   ├── vector_db/
│   └── nova_memory.db
│
├── nova_workspace/
│
├── rag/
│   └── ingest_pdf.py
│
├── tests/
│   └── test_eval_suite.py              # Automated evaluation benchmark harness
│
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── dockerfile
├── requirements.txt
├── sandbox.dockerfile
└── README.md
```

> `nova_workspace/` is created dynamically at runtime and is used as Nova AI's shared file workspace.
> `data/nova_memory.db` stores Nova AI's persistent SQLite memory.
> `data/vector_db/` contains the local ChromaDB vector store used by Nova AI's RAG pipeline.

---

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/dhruvshingala30/nova-ai.git
cd nova-ai
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root.

```text
TAVILY_API_KEY=your_tavily_api_key
```

To obtain a Tavily API key:

1. Visit <https://tavily.com>
2. Sign up for an account.
3. Generate an API key from the dashboard.
4. Copy it into your `.env` file.

> **Note:** The Weather Tool uses the free `wttr.in` service and does not require an API key.

### Pull the Model

```bash
ollama pull qwen2.5:7b
```

> **Note:** The first RAG query may download the configured Sentence Transformers embedding model from Hugging Face. Subsequent runs use the locally cached model.

### Run Nova AI

```bash
python main.py
```

### Workspace

Nova AI automatically creates and monitors the `nova_workspace/` directory.

Place supported files inside this directory and the Workspace Watcher will detect changes and trigger the appropriate ingestion or inspection workflow.

```text
nova-ai/
└── nova_workspace/
    ├── data.csv
    ├── report.pdf
    └── ...
```

---

## 💬 Example Conversations

### Weather

```text
You:
What's the weather in Ahmedabad?

Nova AI:
The current weather in Ahmedabad is 31°C with light rain.
```

---

### Web Search

```text
You:
Latest OpenAI announcements

Nova AI:
Here are the latest updates...
```

---

### Code Execution

```text
You:
What is the determinant of [[2,5],[3,4]]?

Nova AI:
The determinant is -7.
```

---

### Memory

```text
You:
Remember that my favorite IDE is VS Code.

Nova AI:
Got it! I'll remember that your favorite IDE is VS Code.

You:
What's my favorite IDE?

Nova AI:
Your favorite IDE is VS Code.
```

---

### Data Analysis

```text
You:
What files are in my workspace?

Nova AI:
The files in the workspace are:

- users.csv (67 B)
- happy.csv (5.7 KB)
```

```text
You:
Can you inspect happy.csv?

Nova AI:
The happy.csv file contains the following columns and data types:

- country: str
- happiness: int64
- gdp: int64
- social_support: int64
- life_expectancy: int64
- freedom_to_make_life_choices: int64
- generosity: int64
- corruption: int64
```

After inspecting the dataset, Nova AI can pass the relevant information to the Code Execution Engine for further calculations and visualization.

---

### PDF Inspection

```text
You:
Inspect Trading in the Zone by Mark Douglas.pdf

Nova AI:
The file contains:

- Total Pages: 143
- Title: Trading in the Zone
- Author: MaVeRiCk
- Creator: calibre (5.17.0)
- Sample text extracted from the document
```

The PDF inspection layer extracts document metadata and text that can subsequently be indexed by the RAG pipeline.

---

### Local RAG

```text
You:
What does Mark Douglas say about market probabilities and risk?

Nova AI:
Mark Douglas emphasizes that trading requires a different mindset compared
to other aspects of life where we typically rely on skills learned over time.
He explains that traders must learn to think in terms of probabilities and
be willing to surrender conventional skills they have acquired in their
daily lives.
```

Nova AI retrieves relevant context from the locally indexed PDF before generating the answer.

---

### Hybrid RAG

```text
You:
What does Mark Douglas say about market probabilities and risk?

Nova AI:
Mark Douglas emphasizes that trading requires a different mindset compared
to other aspects of life where we typically rely on skills learned over time.
He explains that traders must learn to think in terms of probabilities and
be willing to surrender conventional skills they have acquired in their
daily lives.
```

---

### Workspace Auto-Ingestion

```text
[Workspace Watcher] Auto-ingestion active on: /app/nova_workspace
```

Once a supported file is added or modified inside the workspace, Nova AI can detect the change and make the updated content available to its workspace and knowledge workflows.

---

### Knowledge Retrieval

```text
You:
According to the Mark Douglas book in my workspace, what is the failure rate percentage for traders?

Nova AI:
According to Mark Douglas in his book 'Trading in the Zone', approximately
95% of futures traders lose all of their money within the first year of trading.
```

---

### Multi-Step Planning & Human-in-the-Loop (HITL)

```text
You:
Add a column 'seniority' to users.csv and save the updated file.

Nova AI:
📋 : First, I need to inspect the schema of 'users.csv' before adding a new column.
   1. Step 1: Inspect the schema of 'users.csv'.
   2. Step 2: Add a new column 'seniority' to the DataFrame.
   3. Step 3: Save the updated file.

🛠️ : inspect_csv_schema
🛠️ : run_python_code

⚠️  [HITL SAFEGUARD - HUMAN APPROVAL REQUIRED]
   Reason: Modifying / writing a CSV file to disk
   Tool: run_python_code
   --- Code Preview ---
   | users_df.to_csv('users.csv', index=False)
   --------------------
👉 Approve this workspace modification? (y/n): n
🚫 Action denied by human operator.

💡 : The operation to modify 'users.csv' on disk was rejected. I will simulate the addition in memory instead.
🤖 : The column 'seniority' has been added in-memory for users.csv...
```

---

## 🚀 Development Roadmap

### ✅ Phase 1: Foundation & Tools (Complete)

- [x] Weather Tool (wttr.in)
- [x] Python Code Execution Engine (Docker Sandbox)
- [x] Web Search Tool (Tavily API)
- [x] Tool Calling
- [x] Pydantic Input Validation
- [x] Structured Logging

Nova AI can reason about user requests, choose the appropriate tool, execute it, observe the results, and synthesize a final response.

---

### ✅ Phase 2: Memory, Data Ingestion & Retrieval (Complete)

- [x] SQLite Persistent Memory
- [x] Shared File Workspace & Data Analysis
- [x] PDF Parsing & Content Inspection
- [x] Local RAG Engine
- [x] Workspace Auto-Ingestion
- [x] Smart Python Execution Output Capping
- [x] Hybrid Search (Dense + BM25)
- [x] Reciprocal Rank Fusion (RRF)
- [x] HyDE Retrieval Enhancement

Nova AI now provides a complete local knowledge and data layer with
persistent memory, automated workspace ingestion, PDF processing, data
analysis, and advanced Retrieval-Augmented Generation. Its hybrid retrieval
pipeline combines dense semantic search, BM25, Reciprocal Rank Fusion (RRF),
and HyDE to improve the relevance of retrieved context.

Phase 2 delivers a complete local knowledge and data layer for Nova AI,
combining persistent memory, automated workspace ingestion, safe code
execution, document processing, hybrid retrieval, and local knowledge
grounding.

---

### 🔮 Phase 3: Autonomous Intelligence

#### Agent Reasoning

- [x] ReAct Planning & Reflection Loop
- [x] Automated Evaluation Test Suite
- [x] Human-in-the-Loop Safeguards

#### Advanced Capabilities

- [ ] Vision / Image Understanding
- [ ] Multi-Agent Collaboration Protocol

The goal of this phase is to evolve Nova AI from a tool-using assistant
into an autonomous and reliable reasoning system capable of planning
multi-step tasks, reflecting on its actions, evaluating its own performance,
handling uncertainty with appropriate human oversight, understanding
multimodal inputs, and collaborating with specialized agents.

---

## 🎯 Project Vision

Nova AI is an open-source journey of building a production-style AI agent from first principles.

Rather than relying heavily on agent frameworks, Nova AI implements reasoning, tool calling, code execution, memory, data ingestion, retrieval, and autonomous planning step by step to understand how modern AI agents actually work.

The long-term vision is to build an AI system capable of:

- Remembering previous conversations
- Working with user-provided files
- Parsing and understanding documents
- Retrieving knowledge from indexed documents
- Understanding images
- Executing code safely
- Performing complex mathematical and scientific computations
- Analyzing datasets and generating visualizations
- Retrieving knowledge from local vector databases and online sources
- Planning complex multi-step tasks
- Collaborating with specialized agents
- Continuously improving through reflection

---

## 🤝 Contributing

Contributions, suggestions, and ideas are always welcome.

If you find this project interesting, consider giving it a ⭐ to support its development.

---

## 📄 License

This project is licensed under the MIT License.
