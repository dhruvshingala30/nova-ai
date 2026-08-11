# 🚀 Nova AI

> A modular Agentic AI framework that reasons, remembers, selects tools, executes code safely, and retrieves real-time information using local LLMs.

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

### 📄 PDF Inspection & Parsing

Nova AI can inspect PDF files stored inside the shared workspace and extract useful document-level information before the RAG layer is introduced.

The `inspect_pdf_schema` tool can inspect a PDF and provide the LLM with:

- Total page count
- PDF metadata
- Document title
- Author information
- Creator information
- Sample text extracted from selected pages

This provides Nova AI with structured information about a PDF and establishes the document-processing foundation required for the upcoming Local RAG Engine.

#### Example

```text
You:
Inspect Trading in the Zone by Mark Douglas.pdf

Nova AI:
The file 'Trading in the Zone by Mark Douglas.pdf' contains the following details:

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

The current PDF functionality focuses on document inspection and text extraction. Semantic retrieval and question answering over the document will be introduced as part of the upcoming Local RAG Engine.

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

## 🧠 How Nova AI Works

```text
                         User
                           │
                           ▼
                  Local LLM (Qwen)
                           │
                     Reason & Plan
                           │
                  ┌────────┴────────┐
                  │                 │
             Needs Tool?        Final Answer
                  │
                  ▼
              Tool Router
                  │
       ┌──────────┼───────────┬──────────────┐
       │          │           │              │
       ▼          ▼           ▼              ▼
    Weather     Web      Workspace      SQLite
      API      Search       Tools         Memory
                            │
                            ▼
                       CSV / TSV
                       Inspection
                            │
                            ▼
                    Python Code Engine
                            │
                            ▼
                    Docker Sandbox
                            │
                            ▼
                       Observation
                            │
                            ▼
                       Final Answer
```

The LLM is responsible for:

- Understanding user intent
- Selecting the appropriate tool
- Passing structured arguments
- Observing tool outputs
- Producing the final response

---

## 🛠️ Tech Stack

### Core

- Python
- Ollama
- Qwen 2.5
- Pydantic
- Rich Logging

### APIs & Services

- Tavily API
- wttr.in API
- SQLite

### Execution & Data Analysis

- Docker
- Pandas
- NumPy
- Matplotlib
- Seaborn
- SymPy
- SciPy

---

## 📂 Project Structure

```text
nova-ai/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── memory.py
│   │   └── workspace_manager.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── code_interpreter.py
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
│   └── nova_memory.db
│
├── nova_workspace/
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

> `nova_workspace` is created dynamically at runtime and is used as Nova AI's dedicated file workspace.
> `data/nova_memory.db` stores Nova AI's persistent SQLite memory.

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

### Run Nova AI

```bash
python main.py
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

### 🚧 Phase 2: Memory & Data Ingestion (In Progress)

- [x] SQLite Persistent Memory
- [x] Shared File Workspace & Data Analysis
- [ ] PDF Parsing
- [ ] Local RAG Engine

Nova AI now supports persistent memory and can work with user-provided datasets through a dedicated file workspace.

The workspace provides safe file handling, CSV/TSV inspection, and integration with the Docker-based Python execution engine for computational and data-analysis tasks.

The remaining goals of this phase focus on PDF parsing and building a local Retrieval-Augmented Generation (RAG) engine.

---

### 🔮 Phase 3: Autonomous Intelligence

- [ ] ReAct Planning & Reflection Loop
- [ ] Vision / Image Understanding
- [ ] Multi-Agent Collaboration Protocol

The goal of this phase is to transform Nova AI from a tool-using assistant into an autonomous reasoning system capable of planning, self-correction, and collaborative problem solving.

---

## 🎯 Project Vision

Nova AI is an open-source journey of building a production-style AI agent from first principles.

Rather than relying heavily on agent frameworks, Nova AI implements reasoning, tool calling, code execution, memory, data ingestion, retrieval, and autonomous planning step by step to understand how modern AI agents actually work.

The long-term vision is to build an AI system capable of:

- Remembering previous conversations
- Working with user-provided files
- Understanding documents and images
- Executing code safely
- Performing complex mathematical and scientific computations
- Analyzing datasets and generating visualizations
- Retrieving knowledge from local and online sources
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
