import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

try:
    import fitz
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

# ══════════════════════════════════════════════════════
# YOUR GROQ API KEY
# ══════════════════════════════════════════════════════
GROQ_API_KEY = "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"
GROQ_MODEL   = "llama-3.3-70b-versatile"
# ══════════════════════════════════════════════════════

DEFAULT_POLICY = """"""


def groq_chat(system_msg: str, user_msg: str, max_tokens: int = 1000) -> str:
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg}
        ]
    )
    return response.choices[0].message.content.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    if not PDF_SUPPORT:
        raise RuntimeError("PDF support requires PyMuPDF. Run: pip install pymupdf")
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def summarise_policy(text: str) -> dict:
    system = (
        "You are a policy analyst. Always respond with valid JSON only. "
        "No markdown, no code fences, no explanation. Just the raw JSON object."
    )
    user = f"""Analyse this policy document and return a JSON object with exactly these keys:
- "goals": 2-3 sentences describing the main goals.
- "measures": 2-3 sentences describing key measures and strategies.
- "direction": 2-3 sentences describing the overall vision and direction.
- "tags": an array of 5-8 short keyword strings.

Policy text:
{text[:6000]}"""

    raw = groq_chat(system, user, max_tokens=1000)
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def generate_scenario_draft(summary: dict, title: str, audience: str, focus: str, constraint: str) -> str:
    system = (
        "You are a senior policy drafter. Write formal government policy documents. "
        "Use plain text only. No markdown, no asterisks, no bullet symbols."
    )
    user = f"""Write an adapted formal policy draft based on the summary below.

BASE POLICY SUMMARY:
Goals: {summary['goals']}
Measures: {summary['measures']}
Direction: {summary['direction']}

SCENARIO:
- Title: {title}
- Target Audience: {audience}
- Primary Focus: {focus}
- Key Constraints: {constraint}

Write approximately 300-350 words including:
1. Policy title and preamble
2. Adapted goals for the target audience
3. Four to five specific strategic measures
4. An implementation note
Use formal policy language. Plain text only."""

    return groq_chat(system, user, max_tokens=1000)


@app.route("/")
def index():
    return render_template("index.html", default_policy=DEFAULT_POLICY)


@app.route("/api/test")
def test_api():
    try:
        result = groq_chat("You are helpful.", "Say hello in one sentence.", max_tokens=30)
        return jsonify({"success": True, "response": result})
    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e), "trace": traceback.format_exc()})


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    filename   = file.filename.lower()
    file_bytes = file.read()
    try:
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        elif filename.endswith(".txt"):
            text = file_bytes.decode("utf-8", errors="replace")
        else:
            return jsonify({"error": "Unsupported file type. Use PDF or TXT."}), 400
        if not text.strip():
            return jsonify({"error": "Could not extract text from file."}), 400
        return jsonify({"text": text, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/summarise", methods=["POST"])
def summarise():
    data = request.get_json()
    text = (data or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "No policy text provided."}), 400
    try:
        summary = summarise_policy(text)
        return jsonify({"summary": summary})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-scenario", methods=["POST"])
def generate_scenario():
    data       = request.get_json() or {}
    summary    = data.get("summary")
    title      = data.get("title", "").strip()
    audience   = data.get("audience", "").strip()
    focus      = data.get("focus", "").strip()
    constraint = data.get("constraint", "").strip()
    if not summary:
        return jsonify({"error": "No policy summary provided. Generate a summary first."}), 400
    if not title or not audience or not focus or not constraint:
        return jsonify({"error": "All scenario fields are required."}), 400
    try:
        draft = generate_scenario_draft(summary, title, audience, focus, constraint)
        return jsonify({"draft": draft})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)