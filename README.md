# Interview Agent 🤖

An agentic AI mock interviewer that conducts full multi-round interviews, evaluates answers in real time, and generates a personalised feedback report.

## What it does

- Conducts a full mock interview across 3 rounds — Technical, HR, and Case Study
- Evaluates every answer with a score and constructive feedback
- Accepts resume uploads and tailors questions to your actual experience and projects
- Generates a complete feedback report at the end with strong areas, weak areas, and suggestions

## Why it's an agent and not just a chatbot

A plain LLM just responds to messages. This agent maintains state across the entire interview — tracking which round you're in, what questions have been asked, your scores, and weak areas — and makes decisions based on that state. It evaluates your answer, decides whether to move to the next round, generates a contextually relevant next question, and produces a structured report at the end. That loop is what makes it agentic.

## Tech Stack

- **Backend** — Python, Flask
- **LLM** — LLaMA 3.3 70B via Groq API
- **Resume parsing** — pdfplumber
- **Frontend** — HTML, CSS, JavaScript

## How to run locally

1. Clone the repo
```bash
   git clone https://github.com/IshitaSharma865/Interview-Agent.git
   cd Interview-Agent
```

2. Install dependencies
```bash
   pip install flask groq pdfplumber python-dotenv werkzeug
```

3. Create a `.env` file and add your Groq API key

GROQ_API_KEY=your_key_here

Get a free API key at [console.groq.com](https://console.groq.com)

4. Run the app
```bash
   python app.py
```

5. Open `http://127.0.0.1:5000` in your browser

## Project Structure
interview-agent/
├── app.py          # Flask server and route logic
├── agent.py        # State management, prompts, PDF parsing
├── templates/
│   └── index.html  # Frontend UI
├── .env            # API key (not pushed to GitHub)
└── .gitignore

