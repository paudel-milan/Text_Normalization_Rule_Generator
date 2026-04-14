# TN Rule Induction Engine — Samsung PRISM

A **production-ready, language-agnostic Rule Factory** that automatically generates Text Normalization (TN) rules (Regex patterns + DFA + SSML templates + Normalization Logic) for TTS systems, supporting languages like **Hindi** and **Nepali**.

---

## 📁 Project Structure

```text
TTS_CHECK/
├── backend/
│   ├── app/
│   │   ├── api/                # REST endpoints (FastAPI)
│   │   ├── core/               # Validation, SSML Gen, Pattern Builder, DFA Builder
│   │   ├── languages/          # Language adapters and configs
│   │   │   └── configs/        # Language specific configs (hi_IN.json, ne_NP.json)
│   │   ├── export/             # Zip/JSON/XML generation
│   │   ├── config.py           # Setup and config
│   │   └── main.py             # Server entry point
│   ├── test_smoke.py           # Integration testing script
│   └── run.py                  # CLI entry point to run the backend server
├── frontend/                   # React dashboard (Vite)
│   ├── src/
│   │   ├── App.jsx             # Main UI
│   │   ├── components/         # Modular panel components (Sandbox, Visualizer, etc.)
│   │   ├── api/                # Fetch wrappers
│   │   ├── main.jsx            # React entry point
│   │   └── index.css           # Global premium styling
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── tests/                      # Unit tests
```

---

## 🚀 How to Run

### Backend (FastAPI Server)

```bash
cd backend
pip install -r requirements.txt
python -X utf8 run.py
```

This will run the FastAPI server on `http://localhost:8000`.
- API endpoints: `/api/...`
- Interactive Docs: `http://localhost:8000/docs`

### Frontend (React Dashboard)

```bash
cd frontend
npm install
npm run dev
```

Then open the URL shown in the terminal (usually `http://localhost:5173`).

---

## 🧠 Core Architecture

Unlike the previous proof-of-concept, the core engine has been completely rewritten and modularized:

1. **Config-Driven**: Language configurations are 100% data-driven JSON files containing regex templates, SSML structures, and normalization rules.
2. **DFA Compiler**: We use a custom parser and Thompson's subset construction algorithm to convert Regex → NFA → DFA on the backend dynamically.
3. **Number-To-Word**: Normalization correctly translates digits to natural spoken forms in Hindi and Nepali.
4. **Interactive Sandbox**: Live text tests showing matches, normalized text, and SSML structure.
5. **DFA Visualization**: Beautiful canvas-powered Deterministic Finite Automata rendering algorithm.
6. **Unified Export**: Export to JSON (DFA mapping), Regex script, XML (SSML), or bundle everything inside a ZIP file.

---

## 🌐 Supported Languages & Categories

| Languages | Categories Supported |
|------------------|--------------------|
| Hindi (`hi_IN`)  | Cardinal, Ordinal, Currency, Date, Time, Units |
| Nepali (`ne_NP`) | Cardinal, Ordinal, Currency, Date, Time, Units |

> To add a new language, create a new config mapping in `backend/app/languages/configs/` (e.g., `ta_IN.json` for Tamil). The engine is **completely language-agnostic** — all language-specific data lives in these locale files.

---

## 📋 Requirements

- **Python 3.10+**
- **Node.js 18+** and **npm**
