# LegalEase — AI-Powered Legal Document Generator

LegalEase is a local full-stack application based on the project specification: Streamlit frontend, FastAPI backend, Gemini-powered document generation, editable preview, and TXT/DOCX/PDF exports.

> **Legal notice:** Generated text is a drafting aid, not legal advice. Review documents with a qualified legal professional before signing or relying on them.

## Architecture

```text
Streamlit UI
   │ POST /generate
   ▼
FastAPI API
   │
   ├── Pydantic validation
   ├── GeminiDocumentGenerator
   └── Export services
          ├── TXT
          ├── DOCX
          └── PDF
```

The original specification selected Gemini 1.5 Pro. The implementation uses Google's current `google-genai` SDK and reads the model from `GEMINI_MODEL`, defaulting to a current model. This avoids hard-coding a retired model name.

## Features

- NDA, lease, employment contract, agreement, and custom document types
- Parties, effective date, jurisdiction, and semicolon-separated terms
- Gemini generation with a structured legal drafting prompt
- Editable document text in Streamlit
- Dark HTML preview
- Branded DOCX with optional uploaded logo and terms table
- Branded PDF with optional uploaded logo and footer
- TXT export
- Backend health endpoint
- CORS configuration
- Tests for API validation, formatting, and health endpoint
- AI-disabled fallback mode for local UI/testing when no API key is configured

## Folder structure

```text
LegalEase/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── ai_core/
│   │   ├── __init__.py
│   │   └── gemini_generator.py
│   └── services/
│       ├── __init__.py
│       ├── document_export.py
│       └── text_utils.py
├── frontend/
│   └── app.py
├── assets/
│   └── logo.svg
├── tests/
│   ├── test_api.py
│   └── test_exports.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## VS Code setup

1. Install Python 3.10+.
2. Open this `LegalEase` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

and run commands with `.\.venv\Scripts\python.exe`.

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

5. Install packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

6. Copy `.env.example` to `.env` and put your Gemini API key in `GEMINI_API_KEY`.

## Run

Open two VS Code terminals.

### Terminal 1 — FastAPI

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` to view the interactive API documentation.

### Terminal 2 — Streamlit

```bash
streamlit run frontend/app.py
```

Streamlit normally opens at `http://localhost:8501`.

## Test

With the virtual environment active:

```bash
pytest -q
```

The tests do not call Gemini. They verify API validation, health behavior, and export generation locally.

## AI configuration

Set:

```env
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.8-flash
```

If the key is absent, LegalEase runs in a deterministic demo/fallback mode so you can test the complete UI and export pipeline without making an external AI request. Set a key for real Gemini generation.

## API example

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "document_type":"Non-Disclosure Agreement",
    "parties":"Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
    "terms":"Confidential information must be protected; disclosure is limited to authorized personnel; agreement may be terminated with 15 days notice",
    "effective_date":"2026-10-06",
    "jurisdiction":"Tamil Nadu, India"
  }'
```
