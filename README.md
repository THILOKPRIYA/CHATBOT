# PolicyLens — Flask Edition

A Flask-based AI Policy Adaptation Studio powered by Claude.

## Project Structure

```
policylens/
├── app.py              # Flask backend (routes + AI helpers)
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Single-page frontend (HTML/CSS/JS)
└── README.md
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
# Linux / macOS
export ANTHROPIC_API_KEY=sk-ant-...

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run the app
```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Main app page |
| POST | `/api/upload` | Upload PDF/TXT → returns extracted text |
| POST | `/api/summarise` | Summarise policy text → JSON summary |
| POST | `/api/generate-scenario` | Generate adapted scenario draft |

## Notes
- PDF support requires `pymupdf` (listed in requirements). If not installed, PDF uploads will show an error but TXT files will still work.
- The default policy (Sri Lanka Cyber Security Strategy 2019–2023) is pre-loaded on every page load.
