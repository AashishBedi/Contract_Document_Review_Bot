# 📄 ContractBot — AI Contract Analyzer

An AI-powered contract analysis tool that reads PDF or pasted contract text and returns a structured breakdown of key terms, risk flags, and unusual clauses — powered by **Claude AI**, **FastAPI**, **Streamlit**, and **PyMuPDF**.

---

## 🚀 Quick Start

### 1. Clone / Navigate to the project

```bash
cd ContractBot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API key

Copy the example env file and add your Anthropic API key:

```bash
copy .env.example backend\.env
```

Then open `backend/.env` and replace `your-anthropic-api-key-here` with your real key from [console.anthropic.com](https://console.anthropic.com/).

### 4. Start the backend (Terminal 1)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 5. Start the frontend (Terminal 2)

```bash
cd frontend
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧠 How It Works

```
User (PDF or Text)
        │
        ▼
  Streamlit Frontend  ──POST──►  FastAPI Backend
                                      │
                              PyMuPDF (PDF parsing)
                                      │
                              Claude AI (Analysis)
                                      │
                              Structured JSON Response
                                      │
                        ◄─────────────┘
                    Streamlit renders results
```

---

## 📁 Project Structure

```
ContractBot/
├── backend/
│   ├── main.py        # FastAPI app — /analyze/text and /analyze/pdf endpoints
│   ├── analyzer.py    # Claude API integration
│   ├── parser.py      # PyMuPDF PDF text extraction
│   └── models.py      # Pydantic request/response models
├── frontend/
│   └── app.py         # Streamlit UI
├── .env.example       # API key template
├── requirements.txt   # All dependencies
└── README.md
```

---

## ⚙️ Configuration

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | *(required)* | Your Anthropic API key |
| `CLAUDE_MODEL` | `claude-haiku-4-5` | Claude model to use |

To switch to a smarter model, edit `backend/.env`:
```
CLAUDE_MODEL=claude-sonnet-4-5
```

---

## 📊 What the Analysis Covers

- **Plain-English Summary** — What this contract is about, in simple language
- **Key Parties** — Identifying all parties and their roles
- **Contract Duration** — Start/end date, renewal terms, auto-renewal status
- **Payment Terms** — Amounts, schedule, late fees, refund policy
- **Termination Clauses** — For convenience, for cause, notice periods
- **Confidentiality** — Obligations and duration
- **Intellectual Property** — Who owns what
- **Liability & Indemnity** — Caps, exclusions, obligations
- **Risk Flags** — Color-coded 🔴 High / 🟡 Medium / 🟢 Low risks
- **Unusual Clauses** — Highlighted potentially harmful terms

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/health` | Status |
| `POST` | `/analyze/text` | Analyze contract text (JSON body) |
| `POST` | `/analyze/pdf` | Analyze PDF upload (multipart form) |

### Example: Analyze via curl

```bash
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d "{\"contract_text\": \"SERVICE AGREEMENT\\nThis Agreement is entered into...\"}"
```

---

## ⚠️ Disclaimer

ContractBot is for **informational purposes only** and does not constitute legal advice. Always consult a qualified legal professional for binding decisions.
