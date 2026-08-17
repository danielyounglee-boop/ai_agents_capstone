# 5-Day AI Agents Intensive Capstone

An autonomous AI agent built with Google Gemini and Python.

## Features
- Multi-turn conversational agent with function calling / tools
- Structured outputs with Pydantic
- Modular tool architecture

## Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 2. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd <repo-folder>

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
# or using uv:
# uv pip install -e .
```

### 3. Configuration
Copy `.env.example` to `.env` and fill in your API key:
```bash
cp .env.example .env
```

### 4. Running the Agent
```bash
python main.py
```
