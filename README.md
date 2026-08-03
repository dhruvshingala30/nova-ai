# 🚀 Nova AI

> A modular Agentic AI framework that reasons, selects tools, executes code safely, and retrieves real-time information using local LLMs.

Nova AI is an extensible AI Agent built with Python and local LLMs. Instead of relying only on language generation, Nova AI can reason about a user's request, decide whether external tools are required, execute them, observe the results, and generate accurate, grounded responses.

The project is being developed incrementally to understand and implement the core building blocks of modern AI agents from first principles.

---

## ✨ Current Features

### 🌤️ Weather Tool

Ask for the weather of one or multiple cities.

#### Examples

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

### 🐍 Code Execution Engine

Nova AI includes a Docker-powered Code Execution Engine that enables the LLM to generate and execute Python code safely, eliminating the need for dozens of manually implemented computational tools.

#### Examples - Code Execution Engine

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

The agent automatically:

- Determines when computation is required
- Generates Python code
- Executes the code inside Docker
- Observes the output
- Returns the final answer

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
 ┌────────┼────────────┐
 │        │            │
 ▼        ▼            ▼
Weather  Web      Code Execution
 API    Search       Engine
                     (Docker)
 │        │            │
 └────────┴──────┬─────┘
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

- Python
- Ollama
- Qwen 2.5
- Docker
- Tavily API
- wttr.in API
- Pydantic
- Rich Logging

---

## 📂 Project Structure

```text
nova-ai/
├── app/
│   ├── agent.py
│   ├── config.py
│   ├── models.py
│   ├── prompts.py
│   ├── tools.py
│   ├── utils.py
│   └── ...
│
├── classes/
│   ├── code_interpreter.py
│   ├── weather.py
│   ├── web_search.py
│   └── ...
│
├── main.py
├── requirements.txt
└── README.md
```

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
2. Sign up for a free account.
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

## 🚀 Development Roadmap

### ✅ Phase 1: Foundation & Tools (Complete)

- [x] Weather Tool (wttr.in)
- [x] Python Code Execution Engine (Docker Sandbox)
- [x] Web Search Tool (Tavily API)
- [x] Tool Calling
- [x] Pydantic Input Validation
- [x] Structured Logging

Nova AI can already reason about user requests, choose the appropriate tool, execute it, observe the results, and synthesize a final response.

---

### 🚧 Phase 2: Memory & Data Ingestion (Current)

- [ ] SQLite Persistent Memory
- [ ] Shared File Workspace & Data Analysis
- [ ] PDF Parsing
- [ ] Local RAG Engine

This phase enables Nova AI to remember previous interactions, analyze user-provided files, and retrieve relevant knowledge from local documents.

---

### 🔮 Phase 3: Autonomous Intelligence

- [ ] ReAct Planning & Reflection Loop
- [ ] Vision / Image Understanding
- [ ] Multi-Agent Collaboration Protocol

The goal of this phase is to transform Nova AI from a tool-using assistant into an autonomous reasoning system capable of planning, self-correction, and collaborative problem solving.

---

## 🎯 Project Vision

Nova AI is an open-source journey of building a production-style AI agent from first principles.

Rather than relying heavily on agent frameworks, Nova AI implements reasoning, tool calling, code execution, memory, retrieval, and autonomous planning step by step to understand how modern AI agents actually work.

The long-term vision is to build an AI system capable of:

- Remembering previous conversations
- Understanding documents and images
- Executing code safely
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
