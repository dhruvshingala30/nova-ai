# 🚀 Nova AI

> An extensible AI Agent that thinks, decides, and uses tools to solve problems.

Nova AI is a lightweight Agentic AI built with Python and local LLMs. Instead of relying only on language generation, Nova AI can decide when to use external tools, execute them, observe the results, and generate accurate responses.

This project is being developed incrementally, with every update introducing more powerful agent capabilities.

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

- Identifies the cities
- Calls the weather API
- Returns a natural language response

---

### 🐍 Code Execution Engine

Nova AI includes a Docker-powered Code Execution Engine that enables the LLM to generate and execute Python code safely,

eliminating the need for dozens of manually implemented computational tools.

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
- Returns a natural language response

---

## 🧠 How Nova AI Works

```text
User
   │
   ▼
Local LLM (Qwen / Ollama)
   │
   ▼
Reasoning
   │
   ├───────────────┐
   │               │
Needs Tool?        │
   │               │
  Yes             No
   │               │
   ▼               ▼
Tool Selection   Final Answer
   │
   ├───────────────┐
   │               │
Weather API   Python Interpreter
   │               │
   └───────┬───────┘
           │
           ▼
      Observation
           │
           ▼
      Final Answer
```

The LLM is responsible for:

- Understanding user intent
- Choosing the correct tool
- Passing structured arguments
- Receiving observations
- Producing the final response

---

## 🛠️ Current Tech Stack

- Python
- Ollama
- Qwen 2.5
- Weather API
- Docker Sandbox

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
│   ├── calculator.py
│   ├── weather.py
│   └── ...
│
├── main.py
│
├── requirements.txt
│
└── README.md
```

---

## 🚀 Getting Started

### Clone Repository

```bash
git clone https://github.com/dhruvshingala30/nova-ai.git
cd nova-ai
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Pull the LLM

Example:

```bash
ollama pull qwen2.5:7b
```

---

### Run

```bash
python main.py
```

---

## Example Conversation

```text
You:
Weather in Ahmedabad

Nova AI:
The current weather in Ahmedabad is 31°C with light rain.
```

---

```text
You:
What is the determinant of
[[2,5],[3,4]] ?

Nova AI:
The determinant is -7.
```

---

## 📌 Roadmap

### ✅ Version 0.1

- [x] Tool Calling
- [x] Weather Tool
- [x] Multiple City Support
- [x] Code Execution Engine
- [x] Docker-based Code Execution

---

### 🚧 Version 0.2 (Coming Soon)

- Memory
- RAG

This update enables Nova AI to remember users over time and retrieve relevant information from external knowledge bases, making responses more personalized, context-aware, and factually grounded.

---

### Future Vision

- Web Search
- Image Understanding
- File Upload
- PDF Analysis
- Multi-Agent Architecture
- Planning & Reflection
- Long-Term Memory
- Voice Interaction
- Browser Automation

---

## 🎯 Goal

Nova AI is a learning-focused project that documents the journey of building an AI Agent from simple tool calling to a fully capable autonomous agent.

Every feature is added step by step to understand the foundations of Agentic AI instead of relying on large frameworks.

---

## 🤝 Contributing

Suggestions, ideas, and improvements are always welcome.

If you find the project interesting, consider giving it a ⭐.

---

## 📄 License

MIT License
