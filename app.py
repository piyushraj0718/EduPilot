import base64
import hashlib
import html
import os

import requests
import streamlit as st
import streamlit.components.v1 as components

from dotenv import load_dotenv

from quiz.generator import Quiz
from quiz.evaluator import evaluate_quiz

from quiz.state import (
    initialize_quiz_state,
    reset_quiz_state,
)


load_dotenv()

st.set_page_config(
    page_title="EduPilot — AI Study Companion",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DEFAULTS = {
    "file_hash": None,
    "file_name": None,
    "pdf_bytes": None,
    "messages": [],
    "page_count": 0,
    "chunk_count": 0,
    "topics": [],
    "topics_file_hash": None,
    "quiz": None,
    "quiz_result": None,
    "learner_analysis": None,
    "quiz_topic": "Entire Document",
    "quiz_difficulty": "Medium",
    "active_section": "Learn",
    "pdf_visible": True,
    "pdf_page": 1,
    "agent_source": "Auto",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

initialize_quiz_state()

API_URL = os.getenv("EDUPILOT_API_URL", "http://127.0.0.1:8000")

st.markdown(
    """
<style>
    /* ---------- Global ---------- */
    :root {
        --ep-bg: #f3f4f8;
        --ep-surface: #ffffff;
        --ep-surface-soft: #f3f5fa;
        --ep-border: #e5e7ef;
        --ep-text: #171923;
        --ep-muted: #687086;
        --ep-primary: #635bff;
        --ep-primary-dark: #5148e8;
        --ep-success: #168a55;
        --ep-warning: #b7791f;
        --ep-danger: #c53030;
        --ep-radius: 16px;
    }

    .stApp {
        background: var(--ep-bg);
        color: var(--ep-text);
    }

    .main .block-container {
        max-width: 1500px;
        padding: 1.2rem 1.4rem 2.5rem 1.4rem;
    }

    /* Hide default Streamlit chrome while keeping accessibility. */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { background: transparent !important; }

    /* ---------- Typography ---------- */
    .ep-brand {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: var(--ep-text);
        margin-bottom: 0.15rem;
    }

    .ep-brand-mark {
        display: inline-flex;
        width: 34px;
        height: 34px;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        background: #eceaff;
        color: var(--ep-primary);
        margin-right: 8px;
        vertical-align: middle;
        font-size: 1rem;
    }

    .ep-tagline {
        color: var(--ep-muted);
        font-size: 0.82rem;
        line-height: 1.35;
        margin-bottom: 1.25rem;
    }

    .ep-section-title {
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -0.035em;
        color: var(--ep-text);
        margin: 0;
    }

    .ep-section-subtitle {
        color: var(--ep-muted);
        font-size: 0.9rem;
        margin-top: 0.3rem;
        margin-bottom: 1.15rem;
    }

    /* ---------- Layout surfaces ---------- */
    .ep-panel {
        background: var(--ep-surface);
        border: 1px solid var(--ep-border);
        border-radius: var(--ep-radius);
        padding: 1.15rem;
        box-shadow: 0 6px 24px rgba(20, 25, 45, 0.045);
    }

    .ep-panel-tight {
        background: var(--ep-surface);
        border: 1px solid var(--ep-border);
        border-radius: 14px;
        padding: 0.85rem 0.95rem;
    }

    .ep-eyebrow {
        color: var(--ep-primary);
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.35rem;
    }

    .ep-muted {
        color: var(--ep-muted);
    }

    /* ---------- Navigation ---------- */
    .ep-nav-label {
        color: #9097aa;
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin: 1.3rem 0 0.55rem;
    }

    .ep-doc-mini {
        background: var(--ep-surface);
        border: 1px solid var(--ep-border);
        border-radius: 13px;
        padding: 0.75rem;
        margin-top: 0.8rem;
    }

    .ep-doc-name {
        font-size: 0.78rem;
        font-weight: 700;
        overflow-wrap: anywhere;
        line-height: 1.3;
    }

    .ep-doc-meta {
        color: var(--ep-muted);
        font-size: 0.7rem;
        margin-top: 0.22rem;
    }

    /* ---------- Hero / empty state ---------- */
    .ep-hero {
        background: linear-gradient(135deg, #ffffff 0%, #f1f0ff 100%);
        border: 1px solid #e4e1ff;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1rem;
    }

    .ep-hero-title {
        font-size: 2rem;
        line-height: 1.05;
        font-weight: 850;
        letter-spacing: -0.045em;
        margin-bottom: 0.65rem;
    }

    .ep-hero-copy {
        color: var(--ep-muted);
        max-width: 680px;
        line-height: 1.55;
    }

    .ep-feature {
        background: rgba(255,255,255,0.8);
        border: 1px solid rgba(220,221,235,0.9);
        border-radius: 13px;
        padding: 0.85rem;
        height: 100%;
    }

    .ep-feature-title {
        font-weight: 750;
        font-size: 0.86rem;
        margin-bottom: 0.2rem;
    }

    .ep-feature-copy {
        color: var(--ep-muted);
        font-size: 0.74rem;
        line-height: 1.4;
    }

    /* ---------- Stats ---------- */
    .ep-stat {
        background: var(--ep-surface-soft);
        border: 1px solid var(--ep-border);
        border-radius: 13px;
        padding: 0.8rem;
        text-align: center;
    }

    .ep-stat-value {
        font-size: 1.25rem;
        font-weight: 850;
        letter-spacing: -0.03em;
    }

    .ep-stat-label {
        color: var(--ep-muted);
        font-size: 0.66rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.12rem;
    }

    /* ---------- Topic pills ---------- */
    .ep-topic-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.7rem;
    }

    .ep-topic {
        display: inline-block;
        background: #f0efff;
        border: 1px solid #dfdcff;
        color: #5148c7;
        border-radius: 999px;
        padding: 0.38rem 0.65rem;
        font-size: 0.72rem;
        line-height: 1.2;
    }

    /* ---------- Tool / source badges ---------- */
    .ep-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        border-radius: 999px;
        padding: 0.28rem 0.55rem;
        font-size: 0.68rem;
        font-weight: 750;
        background: #f1f2f7;
        border: 1px solid #e3e5ed;
        color: #596174;
        margin-bottom: 0.45rem;
    }

    .ep-source-title {
        color: var(--ep-muted);
        font-size: 0.72rem;
        font-weight: 750;
        margin-top: 0.7rem;
        margin-bottom: 0.35rem;
    }

    /* ---------- Quiz ---------- */
    .ep-quiz-header {
        background: #171923;
        color: white;
        border-radius: 17px;
        padding: 1.25rem 1.35rem;
        margin-bottom: 1rem;
    }

    .ep-quiz-eyebrow {
        color: #b9b5ff;
        font-size: 0.67rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 800;
    }

    .ep-quiz-title {
        font-size: 1.25rem;
        font-weight: 800;
        margin-top: 0.3rem;
    }

    .ep-question-card {
        background: white;
        border: 1px solid var(--ep-border);
        border-radius: 17px;
        padding: 1.4rem;
        box-shadow: 0 7px 28px rgba(20, 25, 45, 0.055);
    }

    .ep-question-number {
        color: var(--ep-primary);
        font-size: 0.68rem;
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.55rem;
    }

    .ep-question {
        font-size: 1.2rem;
        line-height: 1.45;
        font-weight: 760;
        letter-spacing: -0.02em;
    }

    .ep-result-score {
        font-size: 3.3rem;
        line-height: 1;
        font-weight: 900;
        letter-spacing: -0.06em;
        color: var(--ep-text);
    }

    .ep-result-label {
        color: var(--ep-muted);
        font-size: 0.82rem;
        margin-top: 0.35rem;
    }

    /* ---------- PDF ---------- */
    .ep-pdf-shell {
        background: #e9eaf0;
        border: 1px solid #dfe1e9;
        border-radius: 16px;
        overflow: hidden;
        position: sticky;
        top: 0.8rem;
    }

    .ep-pdf-head {
        background: white;
        border-bottom: 1px solid #e2e3ea;
        padding: 0.85rem 0.9rem;
    }

    .ep-pdf-title {
        font-size: 0.82rem;
        font-weight: 800;
    }

    .ep-pdf-file {
        color: var(--ep-muted);
        font-size: 0.68rem;
        overflow-wrap: anywhere;
        margin-top: 0.2rem;
    }

    .ep-pdf-note {
        color: var(--ep-muted);
        font-size: 0.7rem;
        line-height: 1.4;
        padding: 0.7rem 0.9rem;
        background: #f7f7fa;
        border-top: 1px solid #e2e3ea;
    }

    /* ---------- Streamlit widget polish ---------- */
    /* Streamlit inherits the user's theme for native widgets.  Force the
       light product palette so text never lands on a same-color surface. */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stSidebar"] {
        color: var(--ep-text) !important;
    }

    div[data-testid="stButton"] > button {
        border-radius: 10px;
        min-height: 2.55rem;
        font-weight: 700;
        border: 1px solid var(--ep-border) !important;
        background: #ffffff !important;
        color: #171923 !important;
        box-shadow: none !important;
        transition: all 0.15s ease;
    }

    div[data-testid="stButton"] > button:hover {
        background: #f5f4ff !important;
        border-color: #c9c6ff !important;
        color: var(--ep-primary-dark) !important;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        background: var(--ep-primary) !important;
        border-color: var(--ep-primary) !important;
        color: #ffffff !important;
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: var(--ep-primary-dark) !important;
        border-color: var(--ep-primary-dark) !important;
        color: #ffffff !important;
    }

    /* Native controls need explicit foreground/background colors too. */
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label p,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] small,
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p {
        color: #4b5565 !important;
    }

    div[data-testid="stRadio"] [role="radiogroup"] label {
        color: #171923 !important;
    }

    div[data-testid="stRadio"] [role="radiogroup"] label p {
        color: #171923 !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: #ffffff !important;
        color: #171923 !important;
        border-color: var(--ep-border) !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #8a91a3 !important;
        opacity: 1 !important;
    }

    /* File uploader: keep its native dropzone readable in the light UI. */
    div[data-testid="stFileUploader"] section {
        background: #ffffff !important;
        border-color: #cfd2df !important;
    }

    div[data-testid="stFileUploader"] section * {
        color: #4b5565 !important;
    }

    div[data-testid="stFileUploader"] button {
        background: #ffffff !important;
        color: #171923 !important;
        border-color: #d9dbe5 !important;
    }

    /* Streamlit status/info boxes should retain readable text. */
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span {
        color: inherit !important;
    }

    /* Prevent accidental dark text on dark native containers. */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #ffffff !important;
        color: #171923 !important;
    }

    [role="option"] {
        color: #171923 !important;
        background: #ffffff !important;
    }

    [role="option"]:hover {
        background: #f3f4f8 !important;
    }

    div[data-testid="stFileUploader"] {
        background: white;
        border: 1px dashed #cfd2df;
        border-radius: 14px;
        padding: 0.35rem;
    }

    div[data-testid="stProgress"] > div > div {
        border-radius: 99px;
    }

    .stRadio > div {
        gap: 0.35rem;
    }

    .stTextInput input,
    .stNumberInput input {
        border-radius: 10px;
    }

    /* ---------- Chat input readability ---------- */
    div[data-testid="stChatInput"] {
        padding-top: 0.65rem;
    }

    div[data-testid="stChatInput"] textarea {
        color: #171923 !important;
        background-color: #ffffff !important;
        caret-color: #171923 !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #6b7280 !important;
        opacity: 1 !important;
    }

    div[data-testid="stChatInput"] textarea:focus {
        color: #171923 !important;
        background-color: #ffffff !important;
    }
    /* ---------- Chat message readability ---------- */
    div[data-testid="stChatMessage"] {
        color: #171923 !important;
    }

    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] span {
        color: #171923 !important;
    }

    div[data-testid="stChatMessage"] strong,
    div[data-testid="stChatMessage"] em {
        color: #171923 !important;
    }
    /* ---------- Responsive ---------- */
    @media (max-width: 1050px) {
        .main .block-container {
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .ep-hero {
            padding: 1.35rem;
        }

        .ep-hero-title {
            font-size: 1.65rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


def esc(value):
    return html.escape(str(value))


def clean_ai_math(text):
    """Make common inline LaTeX symbols readable in normal Streamlit Markdown."""
    replacements = {
        r"\\beta_0": "β₀",
        r"\\beta_1": "β₁",
        r"\\beta_2": "β₂",
        r"\\beta": "β",
        r"\\varepsilon": "ε",
        r"\\epsilon": "ε",
        r"\\alpha": "α",
        r"\\gamma": "γ",
        r"\\delta": "δ",
        r"\\theta": "θ",
        r"\\lambda": "λ",
        r"\\mu": "μ",
        r"\\sigma": "σ",
        r"\\rho": "ρ",
        r"\\pi": "π",
        r"\\sqrt": "√",
        r"\\times": "×",
        r"\\leq": "≤",
        r"\\geq": "≥",
        r"\\neq": "≠",
        r"\\pm": "±",
    }
    cleaned = str(text)
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)
    return cleaned


def tool_badge(tool):
    labels = {
        "PDF": "📚  PDF",
        "CALCULATOR": "🧮  Calculator",
        "WEB": "🌐  Web",
    }
    return labels.get(tool, f"✦  {tool}")


def upload_document_to_backend(file_bytes, file_name):
    """Upload PDF to backend for processing."""
    try:
        files = {'file': (file_name, file_bytes, 'application/pdf')}
        
        response = requests.post(
            f"{API_URL}/documents/upload",
            files=files,
            timeout=120
        )
        
        if response.status_code != 200:
            error_detail = response.json().get('detail', 'Upload failed')
            raise Exception(f"Backend upload failed: {error_detail}")
        
        data = response.json()
        
        return {
            'file_hash': data['file_hash'],
            'file_name': data['file_name'],
            'page_count': data['page_count'],
            'chunk_count': data['chunk_count'],
            'topics': data['topics']
        }
    except requests.exceptions.Timeout:
        raise Exception("Upload timed out. The document may be too large or the server is busy.")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to backend server. Make sure the API is running.")
    except Exception as e:
        raise Exception(f"Upload failed: {str(e)}")


def render_pdf_viewer(pdf_bytes, filename, page_number):
    if not pdf_bytes:
        st.info("Upload a PDF to open your study material here.")
        return

    encoded = base64.b64encode(pdf_bytes).decode("ascii")
    safe_name = esc(filename)
    page_number = max(1, int(page_number))

    viewer_html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
      <style>
        * {{ box-sizing: border-box; }}
        html, body {{
          margin: 0;
          padding: 0;
          background: #e9eaf0;
          font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}
        .toolbar {{
          height: 46px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
          padding: 7px 9px;
          background: #ffffff;
          border-bottom: 1px solid #dedfe7;
        }}
        .toolbar-group {{
          display: flex;
          align-items: center;
          gap: 6px;
        }}
        button {{
          border: 1px solid #d9dbe5;
          background: #ffffff;
          color: #2d3140;
          border-radius: 8px;
          height: 31px;
          min-width: 31px;
          padding: 0 9px;
          font-weight: 700;
          cursor: pointer;
        }}
        button:hover {{ background: #f4f4f8; }}
        input {{
          width: 58px;
          height: 31px;
          border: 1px solid #d9dbe5;
          border-radius: 8px;
          text-align: center;
          font-weight: 700;
        }}
        .page-label {{
          color: #687086;
          font-size: 12px;
          white-space: nowrap;
        }}
        .viewer {{
          height: 720px;
          overflow: auto;
          padding: 18px 14px 24px;
          background: #e9eaf0;
          text-align: center;
        }}
        canvas {{
          display: block;
          margin: 0 auto;
          max-width: 100%;
          height: auto;
          background: white;
          box-shadow: 0 5px 18px rgba(20, 25, 45, 0.13);
        }}
        .status {{
          min-height: 18px;
          color: #687086;
          font-size: 11px;
          margin-top: 8px;
        }}
        @media (max-width: 700px) {{
          .viewer {{ height: 560px; padding: 10px 7px 18px; }}
        }}
      </style>
    </head>
    <body>
      <div class="toolbar">
        <div class="toolbar-group">
          <button id="prev" title="Previous page">‹</button>
          <input id="page" type="number" min="1" value="{page_number}" aria-label="Page number">
          <span class="page-label">/ <span id="total">—</span></span>
          <button id="next" title="Next page">›</button>
        </div>
        <div class="toolbar-group">
          <button id="zoomOut" title="Zoom out">−</button>
          <button id="zoomIn" title="Zoom in">+</button>
        </div>
      </div>
      <div class="viewer">
        <canvas id="canvas"></canvas>
        <div class="status" id="status">Loading {safe_name}…</div>
      </div>

      <script>
        pdfjsLib.GlobalWorkerOptions.workerSrc =
          "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

        const raw = atob("{encoded}");
        const bytes = new Uint8Array(raw.length);
        for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);

        let pdf = null;
        let currentPage = {page_number};
        let scale = 1.15;
        let rendering = false;
        let pending = null;

        const canvas = document.getElementById("canvas");
        const ctx = canvas.getContext("2d");
        const pageInput = document.getElementById("page");
        const total = document.getElementById("total");
        const status = document.getElementById("status");

        async function renderPage(num) {{
          if (!pdf) return;

          if (rendering) {{
            pending = num;
            return;
          }}

          rendering = true;

          try {{
            const page = await pdf.getPage(num);
            const viewport = page.getViewport({{ scale }});

            canvas.width = viewport.width;
            canvas.height = viewport.height;

            await page.render({{
              canvasContext: ctx,
              viewport: viewport
            }}).promise;

            currentPage = num;
            pageInput.value = num;
            status.textContent = "Page " + num + " of " + pdf.numPages;
          }} catch (error) {{
            status.textContent = "Unable to render this page.";
          }} finally {{
            rendering = false;
            if (pending !== null) {{
              const nextPage = pending;
              pending = null;
              renderPage(nextPage);
            }}
          }}
        }}

        document.getElementById("prev").onclick = () => {{
          if (pdf && currentPage > 1) renderPage(currentPage - 1);
        }};

        document.getElementById("next").onclick = () => {{
          if (pdf && currentPage < pdf.numPages) renderPage(currentPage + 1);
        }};

        pageInput.onchange = () => {{
          if (!pdf) return;
          let target = parseInt(pageInput.value || "1", 10);
          target = Math.max(1, Math.min(pdf.numPages, target));
          renderPage(target);
        }};

        document.getElementById("zoomIn").onclick = () => {{
          scale = Math.min(2.2, scale + 0.15);
          renderPage(currentPage);
        }};

        document.getElementById("zoomOut").onclick = () => {{
          scale = Math.max(0.65, scale - 0.15);
          renderPage(currentPage);
        }};

        pdfjsLib.getDocument({{ data: bytes }}).promise.then((loadedPdf) => {{
          pdf = loadedPdf;
          total.textContent = pdf.numPages;
          renderPage(Math.max(1, Math.min({page_number}, pdf.numPages)));
        }}).catch(() => {{
          status.textContent = "PDF could not be displayed in the viewer.";
        }});
      </script>
    </body>
    </html>
    """

    components.html(viewer_html, height=775, scrolling=False)


def reset_document_state():
    st.session_state.messages = []
    st.session_state.quiz = None
    st.session_state.quiz_result = None
    st.session_state.learner_analysis = None
    st.session_state.topics = []
    st.session_state.topics_file_hash = None
    st.session_state.pdf_page = 1
    reset_quiz_state()


def render_navigation():
    st.markdown(
        '<div class="ep-brand"><span class="ep-brand-mark">✦</span>EduPilot</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ep-tagline">AI Study & Assessment Assistant</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ep-nav-label">Workspace</div>', unsafe_allow_html=True)

    for label, icon in [
        ("Learn", "💬"),
        ("Practice", "✓"),
        ("Progress", "◔"),
    ]:
        is_active = st.session_state.active_section == label
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{label}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_section = label
            st.rerun()

    st.markdown('<div class="ep-nav-label">Study material</div>', unsafe_allow_html=True)

    if st.session_state.file_name:
        st.markdown(
            f"""
            <div class="ep-doc-mini">
                <div class="ep-doc-name">📄 {esc(st.session_state.file_name)}</div>
                <div class="ep-doc-meta">
                    {st.session_state.page_count} pages
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.caption("No document loaded yet.")

    st.markdown("<div style='height:0.65rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.72rem;font-weight:750;color:#687086;margin-bottom:0.35rem;">ADD DOCUMENT</div>',
        unsafe_allow_html=True,
    )

    return st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        key="pdf_uploader",
        label_visibility="visible",
        help="Upload a study PDF to use with EduPilot.",
    )


def render_document_header():
    st.markdown(
        f"""
        <div class="ep-panel">
            <div class="ep-eyebrow">Study material</div>
            <div style="font-size:1.08rem;font-weight:800;margin-bottom:0.85rem;">
                {esc(st.session_state.file_name or "Your document")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    stats = [
        (st.session_state.page_count, "Pages"),
        (len(st.session_state.topics), "Topics"),
    ]
    for col, (value, label) in zip((c1, c2), stats):
        with col:
            st.markdown(
                f"""
                <div class="ep-stat">
                    <div class="ep-stat-value">{esc(value)}</div>
                    <div class="ep-stat-label">{esc(label)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_topics():
    with st.expander("Explore document topics", expanded=False):
        topics = st.session_state.topics
        if topics:
            pills = "".join(
                f'<span class="ep-topic">{esc(topic)}</span>'
                for topic in topics
            )
            st.markdown(
                f'<div class="ep-topic-wrap">{pills}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("No major topics were detected.")


def render_learn():
    st.markdown(
        '<div class="ep-section-title">Ask EduPilot</div>'
        '<div class="ep-section-subtitle">Understand your material, solve calculations, or look up current information.</div>',
        unsafe_allow_html=True,
    )

    render_document_header()
    render_topics()

    top_left, top_right = st.columns([1, 1])
    with top_left:
        st.markdown(
            '<div class="ep-eyebrow">Answer source</div>',
            unsafe_allow_html=True,
        )
    with top_right:
        if st.button(
            "Clear conversation",
            key="clear_chat",
            use_container_width=True,
        ):
            st.session_state.messages = []
            st.rerun()

    st.session_state.agent_source = st.radio(
        "Answer source",
        ["Auto", "PDF", "Web"],
        horizontal=True,
        label_visibility="collapsed",
        key="agent_source_radio",
    )

    if not st.session_state.messages:
        st.markdown(
            """
            <div class="ep-hero">
                <div class="ep-hero-title">What would you like to learn?</div>
                <div class="ep-hero-copy">
                    Ask a question about your document, request a calculation,
                    or switch to Web when you need current information.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            content = message["content"]
            if message["role"] == "assistant":
                content = clean_ai_math(content)
            st.markdown(content)

            if message["role"] == "assistant" and message.get("tool"):
                st.markdown(
                    f'<span class="ep-badge">{tool_badge(message["tool"])}</span>',
                    unsafe_allow_html=True,
                )

                sources = message.get("sources", [])
                if sources:
                    st.markdown(
                        '<div class="ep-source-title">Referenced pages</div>',
                        unsafe_allow_html=True,
                    )
                    source_cols = st.columns(min(len(sources), 4))
                    for index, page in enumerate(sources):
                        with source_cols[index % len(source_cols)]:
                            if st.button(
                                f"Page {page}",
                                key=f"source_{id(message)}_{page}",
                                use_container_width=True,
                            ):
                                st.session_state.pdf_page = int(page)
                                st.session_state.pdf_visible = True
                                st.rerun()

    question = st.chat_input(
        "Ask anything about your document…",
        key="ask_input",
    )

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        try:
            with st.spinner("EduPilot is thinking…"):
                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question,
                        "file_hash": st.session_state.file_hash,
                        "source": st.session_state.agent_source.upper(),
                    },
                    timeout=120,
                )

            if response.status_code != 200:
                raise Exception(
                    response.json().get(
                        "detail",
                        "FastAPI request failed.",
                    )
                )

            data = response.json()
            answer = clean_ai_math(data["answer"])
            tool = data["tool"]
            sources = data.get("sources", [])

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "tool": tool,
                    "sources": sources,
                }
            )

            if tool == "PDF" and sources:
                st.session_state.pdf_page = int(sources[0])
                st.session_state.pdf_visible = True

            st.rerun()

        except Exception as e:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Sorry, I couldn't process that request.",
                    "tool": None,
                    "sources": [],
                }
            )
            st.error("EduPilot couldn't process that request.")
            with st.expander("Technical details"):
                st.code(str(e))


def render_quiz_setup():
    st.markdown(
        '<div class="ep-section-title">Practice</div>'
        '<div class="ep-section-subtitle">Turn your study material into a focused practice session.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="ep-quiz-header">
            <div class="ep-quiz-eyebrow">Build your quiz</div>
            <div class="ep-quiz-title">Choose what you want to practice</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.35, 0.65])

    with c1:
        topic_options = ["Entire Document"] + st.session_state.topics
        selected_topics = st.multiselect(
            "Topics",
            topic_options,
            default=["Entire Document"],
        )

        if "Entire Document" in selected_topics:
            quiz_topic = "Entire Document"
        elif selected_topics:
            quiz_topic = ", ".join(selected_topics)
        else:
            quiz_topic = None

    with c2:
        number_of_questions = st.number_input(
            "Questions",
            min_value=1,
            max_value=15,
            value=5,
            step=1,
        )

        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            index=1,
        )

    st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)

    if st.button(
        "Generate Quiz →",
        use_container_width=True,
        type="primary",
        key="generate_quiz",
    ):
        if not quiz_topic:
            st.warning("Please select at least one topic.")
            return

        with st.spinner("Creating your quiz from the document…"):
            try:
                response = requests.post(
                    f"{API_URL}/quiz/generate",
                    json={
                        "file_hash": st.session_state.file_hash,
                        "number_of_questions": number_of_questions,
                        "difficulty": difficulty,
                        "topic": quiz_topic,
                    },
                    timeout=120,
                )

                if response.status_code != 200:
                    raise Exception(
                        response.json().get(
                            "detail",
                            "Quiz generation failed.",
                        )
                    )

                quiz = Quiz.model_validate(response.json())

                st.session_state.quiz = quiz
                st.session_state.quiz_topic = quiz_topic
                st.session_state.quiz_difficulty = difficulty
                st.session_state.quiz_result = None
                st.session_state.learner_analysis = None
                reset_quiz_state()
                st.rerun()

            except Exception as e:
                st.error("Unable to generate the quiz right now.")
                with st.expander("Technical details"):
                    st.code(str(e))


def render_active_quiz():
    quiz = st.session_state.quiz
    total = len(quiz.questions)
    current_index = st.session_state.quiz_question_index
    current_question = quiz.questions[current_index]

    st.markdown(
        f"""
        <div class="ep-quiz-header">
            <div class="ep-quiz-eyebrow">
                {esc(st.session_state.quiz_difficulty)} · {esc(st.session_state.quiz_topic)}
            </div>
            <div class="ep-quiz-title">Practice session</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress((current_index + 1) / total)

    st.markdown(
        f"""
        <div class="ep-question-card">
            <div class="ep-question-number">Question {current_index + 1} of {total}</div>
            <div class="ep-question">{esc(current_question.question)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    selected_option = st.radio(
        "Choose your answer",
        current_question.options,
        index=None,
        key=f"answer_{current_index}",
    )

    if selected_option is not None:
        st.session_state.quiz_answers[current_index] = (
            current_question.options.index(selected_option)
        )

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        if current_index > 0:
            if st.button(
                "← Previous",
                use_container_width=True,
                key="quiz_previous",
            ):
                st.session_state.quiz_question_index -= 1
                st.rerun()

    with right:
        if current_index < total - 1:
            if st.button(
                "Next →",
                use_container_width=True,
                type="primary",
                key="quiz_next",
            ):
                if current_index not in st.session_state.quiz_answers:
                    st.warning("Please select an answer first.")
                else:
                    st.session_state.quiz_question_index += 1
                    st.rerun()
        else:
            if st.button(
                "Submit Quiz",
                use_container_width=True,
                type="primary",
                key="quiz_submit",
            ):
                if len(st.session_state.quiz_answers) != total:
                    st.warning("Please answer all questions before submitting.")
                else:
                    user_answers = [
                        st.session_state.quiz_answers[i]
                        for i in range(total)
                    ]
                    st.session_state.quiz_result = evaluate_quiz(
                        quiz,
                        user_answers,
                    )
                    st.rerun()


def render_quiz_result():
    quiz = st.session_state.quiz
    result = st.session_state.quiz_result

    score = result["score"]
    total = result["total"]
    percentage = (score / total) * 100

    st.markdown(
        '<div class="ep-section-title">Quiz complete</div>'
        '<div class="ep-section-subtitle">Here is how you performed and what to focus on next.</div>',
        unsafe_allow_html=True,
    )

    score_col, detail_col = st.columns([1, 2])

    with score_col:
        st.markdown(
            f"""
            <div class="ep-panel" style="text-align:center;padding:1.6rem;">
                <div class="ep-result-score">{percentage:.0f}%</div>
                <div class="ep-result-label">{score} of {total} correct</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with detail_col:
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(
                f"""
                <div class="ep-stat">
                    <div class="ep-stat-value">{score}</div>
                    <div class="ep-stat-label">Correct</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with d2:
            st.markdown(
                f"""
                <div class="ep-stat">
                    <div class="ep-stat-value">{total - score}</div>
                    <div class="ep-stat-label">Incorrect</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.progress(percentage / 100)

        if percentage >= 80:
            st.success("Excellent work! You have a strong understanding of the material.")
        elif percentage >= 60:
            st.info("Good job! Review the questions you missed to strengthen your understanding.")
        else:
            st.warning("Keep practicing. Reviewing the explanations can help strengthen your understanding.")

    if st.session_state.learner_analysis is None:
        with st.spinner("Analyzing your performance…"):
            try:
                response = requests.post(
                    f"{API_URL}/quiz/analyze",
                    json={
                        "quiz": quiz.model_dump(),
                        "result": result,
                    },
                    timeout=120,
                )

                if response.status_code != 200:
                    raise Exception(
                        response.json().get(
                            "detail",
                            "Learning analysis failed.",
                        )
                    )

                st.session_state.learner_analysis = response.json()

            except Exception as e:
                st.error("Unable to analyze your performance right now.")
                with st.expander("Technical details"):
                    st.code(str(e))

    analysis = st.session_state.learner_analysis

    if analysis:
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        a1, a2 = st.columns(2)

        with a1:
            st.markdown(
                """
                <div class="ep-panel">
                    <div class="ep-eyebrow">Learning insight</div>
                    <div style="font-size:1.05rem;font-weight:800;">Areas to review</div>
                """,
                unsafe_allow_html=True,
            )

            weak_topics = analysis.get("weak_topics")
            if weak_topics:
                if isinstance(weak_topics, list):
                    pills = "".join(
                        f'<span class="ep-topic">{esc(topic)}</span>'
                        for topic in weak_topics
                    )
                    st.markdown(
                        f'<div class="ep-topic-wrap">{pills}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.write(weak_topics)
            else:
                st.success("No major weak areas were identified.")

            

        with a2:
            st.markdown(
                """
                <div class="ep-panel">
                    <div class="ep-eyebrow">Next step</div>
                    <div style="font-size:1.05rem;font-weight:800;">Recommended action</div>
                """,
                unsafe_allow_html=True,
            )
            st.write(analysis.get("recommendation", "Keep practicing."))

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:1.1rem;font-weight:800;margin-bottom:0.5rem;">Review answers</div>',
        unsafe_allow_html=True,
    )

    for index, answer in enumerate(result["results"]):
        question = quiz.questions[index]

        status = "✓ Correct" if answer["is_correct"] else "✕ Incorrect"
        label = f"{status} · Question {index + 1}"

        with st.expander(label):
            st.markdown(f"**{question.question}**")

            if answer["is_correct"]:
                st.success("Correct")
            else:
                st.error("Incorrect")

            st.write(
                f"**Your answer:** "
                f"{question.options[answer['user_answer']]}"
            )
            st.write(
                f"**Correct answer:** "
                f"{question.options[answer['correct_answer']]}"
            )
            st.info(f"**Explanation:** {answer['explanation']}")

    if st.button(
        "Create another quiz",
        use_container_width=True,
        type="primary",
        key="new_quiz",
    ):
        st.session_state.quiz = None
        st.session_state.quiz_result = None
        st.session_state.learner_analysis = None
        reset_quiz_state()
        st.rerun()


def render_practice():
    if st.session_state.quiz is None:
        render_quiz_setup()
    elif st.session_state.quiz_result is None:
        render_active_quiz()
    else:
        render_quiz_result()


def render_progress():
    st.markdown(
        '<div class="ep-section-title">Progress</div>'
        '<div class="ep-section-subtitle">See your latest quiz performance and what EduPilot recommends next.</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.quiz_result:
        st.markdown(
            """
            <div class="ep-hero">
                <div class="ep-hero-title">Your learning insights will appear here.</div>
                <div class="ep-hero-copy">
                    Complete a quiz to see your score, areas to review,
                    and a personalized next step.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Go to Practice →",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.active_section = "Practice"
            st.rerun()
        return

    render_quiz_result()


def render_pdf_panel():
    if not st.session_state.pdf_visible:
        st.markdown(
            """
            <div class="ep-panel-tight" style="text-align:center;margin-top:0.1rem;">
                <div style="font-size:1.2rem;margin-bottom:0.25rem;">📄</div>
                <div style="font-weight:800;font-size:0.86rem;">Study material</div>
                <div class="ep-muted" style="font-size:0.7rem;margin-top:0.2rem;">
                    PDF panel is hidden.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Show PDF",
            use_container_width=True,
            type="primary",
            key="show_pdf",
        ):
            st.session_state.pdf_visible = True
            st.rerun()
        return

    st.markdown(
        f"""
        <div class="ep-pdf-head">
            <div class="ep-pdf-title">Study Material</div>
            <div class="ep-pdf-file">📄 {esc(st.session_state.file_name or "No document")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Hide PDF",
        use_container_width=True,
        key="hide_pdf",
    ):
        st.session_state.pdf_visible = False
        st.rerun()

    if st.session_state.pdf_bytes:
        render_pdf_viewer(
            st.session_state.pdf_bytes,
            st.session_state.file_name or "study-material.pdf",
            st.session_state.pdf_page,
        )
    else:
        st.info("Upload a PDF to open your study material.")


left_col, center_col, right_col = st.columns(
    [1.0, 3.05, 2.0],
    gap="large",
)

with left_col:
    uploaded_file = render_navigation()

with center_col:
    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        if st.session_state.file_hash != file_hash:
            reset_document_state()

            with st.spinner("Processing your document..."):
                try:
                    result = upload_document_to_backend(file_bytes, uploaded_file.name)
                    
                    st.session_state.file_hash = result['file_hash']
                    st.session_state.file_name = result['file_name']
                    st.session_state.page_count = result['page_count']
                    st.session_state.chunk_count = result['chunk_count']
                    st.session_state.topics = result['topics']
                    st.session_state.topics_file_hash = result['file_hash']
                    st.session_state.pdf_bytes = file_bytes
                    
                    st.success("Document processed successfully!")
                    
                except Exception as e:
                    st.error(f"Failed to process document: {str(e)}")
                    st.info("Make sure the FastAPI backend is running at " + API_URL)

    if not st.session_state.file_hash:
        st.markdown(
            """
            <div class="ep-hero">
                <div class="ep-eyebrow">Welcome to EduPilot</div>
                <div class="ep-hero-title">Learn smarter from your own material.</div>
                <div class="ep-hero-copy">
                    Upload a study PDF to ask grounded questions, practice with
                    AI-generated quizzes, and understand where you need to improve.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        f1, f2, f3 = st.columns(3)
        features = [
            ("💬", "Ask questions", "Get answers grounded in your study material."),
            ("✓", "Practice", "Generate focused quizzes from your document."),
            ("◔", "Improve", "Review performance and identify weak areas."),
        ]
        for col, (icon, title, copy) in zip((f1, f2, f3), features):
            with col:
                st.markdown(
                    f"""
                    <div class="ep-feature">
                        <div style="font-size:1.2rem;margin-bottom:0.35rem;">{icon}</div>
                        <div class="ep-feature-title">{title}</div>
                        <div class="ep-feature-copy">{copy}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        st.info("Upload your PDF from the left panel to begin.")

    else:
        if st.session_state.active_section == "Learn":
            render_learn()
        elif st.session_state.active_section == "Practice":
            render_practice()
        else:
            render_progress()

with right_col:
    if st.session_state.file_hash:
        render_pdf_panel()
    else:
        st.markdown(
            '''
            <div class="ep-panel-tight" style="min-height:190px;display:flex;
                        flex-direction:column;justify-content:center;
                        text-align:center;">
                <div style="font-size:1.35rem;margin-bottom:0.35rem;">📄</div>
                <div style="font-weight:800;font-size:0.9rem;">Your study material</div>
                <div class="ep-muted" style="font-size:0.72rem;margin-top:0.25rem;">
                    Upload a PDF to keep it beside your workspace.
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
