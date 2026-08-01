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

### 🧮 Basic Calculator

Perform arithmetic operations using a dedicated tool.

Supported operations:

- Addition
- Subtraction
- Multiplication
- Division
- Maximum
- Minimum

#### Examples - Basic Calculator Tool

```text
25 + 89
```

```text
Multiply 12 and 18
```

```text
Maximum of 15, 82, 33 and 50
```

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
   ├── Needs Tool?
   │       │
   │      Yes
   │       │
   ▼       ▼
Tool Execution
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
- Docker (preparing for future execution environment)

---

## 📂 Project Structure

```text
nova-ai/
├── app/
│   ├── agent.py
│   ├── config.py
│   └── models.py
│   ├── prompts.py
│   ├── tools.py
│   └── utils.py
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
Maximum of 25, 78, 11 and 45

Nova AI:
The maximum number is 78.
```

---

## 📌 Roadmap

### ✅ Version 0.1

- [x] Tool Calling
- [x] Weather Tool
- [x] Basic Calculator
- [x] Multiple City Support
- [x] Multiple Number Support

---

### 🚧 Version 0.2 (Coming Soon)

#### Code Interpreter

A major upgrade that enables Nova AI to:

- Generate Python code automatically
- Execute code safely inside Docker
- Solve complex mathematical problems
- Analyze datasets
- Create graphs
- Work with CSV and Excel files
- Eliminate the need for many manually written tools

This update moves Nova AI from using predefined tools toward autonomous problem solving.

---

### Future Vision

- Memory
- RAG
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
