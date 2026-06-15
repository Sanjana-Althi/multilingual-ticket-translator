
"""
app.py
------
Project : Multilingual Ticket Translator
Module  : Streamlit Frontend — Professional Dashboard
Challenge: Infinite Computer Solutions AI Prototype Challenge
Run with: streamlit run app.py
"""

import os
import pandas as pd
import streamlit as st

from detector import detect_ticket_language
from translator import translate_to_english, translate_from_english
from glossary_handler import load_glossary, protect_terms, restore_terms
from storage import save_ticket_record

# ADDED: AI Agent import — graceful fallback if module missing
try:
    from ai_agent import TicketAgent as _TicketAgent
    _ai_agent_instance = _TicketAgent()
    AI_AGENT_AVAILABLE = True
except Exception:
    AI_AGENT_AVAILABLE = False
    _ai_agent_instance = None


# ADDED: safe wrapper — never raises, always returns a dict
def _run_ai_agent(ticket_text: str) -> dict:
    """Call TicketAgent.process() safely. Returns fallback dict on any failure."""
    if not AI_AGENT_AVAILABLE or _ai_agent_instance is None:
        return {
            "improved_ticket": ticket_text,
            "summary": "AI Agent unavailable — original ticket used.",
            "category": "General",
            "priority": "Medium",
            "error": "TicketAgent module not available.",
        }
    try:
        return _ai_agent_instance.process(ticket_text)
    except Exception as exc:
        return {
            "improved_ticket": ticket_text,
            "summary": "AI Agent error — original ticket used.",
            "category": "General",
            "priority": "Medium",
            "error": str(exc),
        }

SUPPORTED_LANGUAGES = {"Telugu", "Hindi", "Tamil", "Kannada", "English"}
DEFAULT_REPLY = (
    "Thank you for contacting support. We have received your request and are "
    "working on a resolution. We will provide an update as soon as possible."
)
OUTPUT_CSV = os.path.join("output", "tickets.csv")

st.set_page_config(
    page_title="Multilingual Ticket Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Home"

st.markdown("""
<style>
/* ── FORCE DARK BG ── */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container,
[data-testid="stVerticalBlock"] {
    background-color: #0F1420 !important;
    color: #E2E8F0 !important;
}
section[data-testid="stSidebar"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"] { background-color: #0F1420 !important; }

/* ── GLOBAL ── */
*, *::before, *::after {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    box-sizing: border-box;
}
p, span, label, li, td, th { color: #CBD5E1; }
h1,h2,h3,h4,h5,h6 { color: #F1F5F9 !important; }
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="collapsedControl"] { display: none !important; }
.block-container {
    padding: 0 2.5rem 4rem !important;
    max-width: 1180px !important;
    background-color: #0F1420 !important;
}

/* ── NAVBAR HTML DIV ── */
.navbar-outer {
    background: linear-gradient(90deg, #080C14 0%, #0D1117 100%);
    border-bottom: 1px solid #1E2D45;
    padding: 0 32px;
    display: flex;
    align-items: center;
    height: 64px;
    margin: 0 -2.5rem 0.5rem;
    box-shadow: 0 2px 20px rgba(0,0,0,0.5);
}
.navbar-brand {
    font-size: 1.05rem;
    font-weight: 800;
    color: #2DD4BF !important;
    white-space: nowrap;
}

/* ── NAV BUTTONS (column buttons only) ── */
div[data-testid="column"] .stButton > button {
    background: transparent !important;
    color: #64748B !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 6px 10px !important;
    box-shadow: none !important;
    letter-spacing: 0.02em !important;
    white-space: nowrap !important;
    transition: all 0.2s !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: rgba(45,212,191,0.08) !important;
    color: #2DD4BF !important;
    border-color: rgba(45,212,191,0.25) !important;
}

/* ── ALL ACTION BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #0D9488 0%, #4338CA 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 10px 22px !important;
    box-shadow: 0 2px 8px rgba(13,148,136,0.3) !important;
    transition: opacity 0.18s, transform 0.12s !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
.stDownloadButton > button {
    background: linear-gradient(135deg, #0891B2 0%, #0D9488 100%) !important;
    color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; padding: 10px 24px !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: #0D1117 !important;
    border: 1.5px dashed #1E2D45 !important;
    border-radius: 10px !important;
    padding: 8px 12px !important;
}

/* Base style for ALL buttons inside uploader */
[data-testid="stFileUploader"] button {
    background: #1A2440 !important;
    color: #E2E8F0 !important;
    border: 1px solid #1E2D45 !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
    box-shadow: none !important;
    padding: 6px 14px !important;
}

/* ── FIX: Hide Material icon "upload" text bleeding into the browse button only ── */
[data-testid="stFileUploader"] button span[data-testid="stIconMaterial"],
[data-testid="stFileUploader"] button .material-icons,
[data-testid="stFileUploader"] button [class*="Icon"],
[data-testid="stFileUploader"] button span:first-child:not(:last-child) {
    display: none !important;
}

/* ── FIX: Suppress ::before/::after ONLY on the browse/upload button
         (it has no aria-label; the add-more button does) ── */
[data-testid="stFileUploader"] button:not([aria-label])::before,
[data-testid="stFileUploader"] button:not([aria-label])::after {
    content: none !important;
    display: none !important;
}

[data-testid="stFileUploader"] svg {
    display: inline-flex !important;
}

[data-testid="stFileUploader"] section { background: #0D1117 !important; }
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] small { color: #CBD5E1 !important; }

/* ── FILE CHIP delete button ── */
[data-testid="stFileUploaderDeleteBtn"] button {
    background: #EF4444 !important;
    background-image: none !important;
    border-radius: 50% !important;
    width: 20px !important;
    height: 20px !important;
    min-height: unset !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: none !important;
    border: none !important;
    position: relative !important;
    overflow: visible !important;
    transform: none !important;
}

/* ── ADD-MORE FILES button: the small square that appears beside uploaded file chips ──
   Streamlit renders it as a <button> with aria-label="Add files" inside the uploader  ── */
[data-testid="stFileUploader"] button[aria-label="Add files"] {
    background: #1A2440 !important;
    border: 1.5px dashed #2DD4BF !important;
    border-radius: 6px !important;
    width: 36px !important;
    height: 36px !important;
    min-height: unset !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: none !important;
    position: relative !important;
    overflow: visible !important;
    transform: none !important;
    font-size: 0 !important;       /* hide any icon glyph text */
    color: transparent !important;
}
/* Hide any spans/svgs inside it */
[data-testid="stFileUploader"] button[aria-label="Add files"] span,
[data-testid="stFileUploader"] button[aria-label="Add files"] svg {
    display: none !important;
}
/* Inject the "+" via ::after — NOT blocked because we scoped ::after suppression above */
[data-testid="stFileUploader"] button[aria-label="Add files"]::after {
    content: "+" !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    font-size: 1.4rem !important;
    font-weight: 300 !important;
    color: #2DD4BF !important;
    line-height: 1 !important;
    pointer-events: none !important;
    font-family: sans-serif !important;
}
[data-testid="stFileUploader"] button[aria-label="Add files"]:hover {
    background: rgba(45,212,191,0.12) !important;
    border-color: #2DD4BF !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {
    background: #161D2E !important;
    border: 1px solid #1E2D45 !important;
    border-radius: 10px !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] details > summary {
    background: #161D2E !important;
    color: #C8D6E3 !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 14px 18px 14px 42px !important;
    list-style: none !important;
    position: relative !important;
}
[data-testid="stExpander"] summary::-webkit-details-marker { display: none !important; }
[data-testid="stExpander"] summary::marker { content: "" !important; }
[data-testid="stExpander"] summary span[data-testid="stIconMaterial"],
[data-testid="stExpander"] summary [class*="icon"],
[data-testid="stExpander"] summary svg { display: none !important; }
[data-testid="stExpander"] summary::before {
    content: "▶";
    font-size: 0.55rem;
    color: #4E6278;
    position: absolute;
    left: 18px;
    top: 50%;
    transform: translateY(-50%);
    transition: transform 0.2s;
    font-family: sans-serif !important;
}
[data-testid="stExpander"][open] summary::before,
details[open] > summary::before { transform: translateY(-50%) rotate(90deg); }
[data-testid="stExpander"] summary:hover { color: #2DD4BF !important; }
[data-testid="stExpander"] > div { background: #161D2E !important; }

/* ── TEXTAREA / INPUT ── */
.stTextArea textarea {
    background: #0D1117 !important; border: 1px solid #1E2D45 !important;
    border-radius: 8px !important; color: #E2E8F0 !important;
    font-size: 0.9rem !important; caret-color: #2DD4BF !important;
}
.stTextArea textarea::placeholder { color: #2D3748 !important; opacity: 1 !important; }
.stTextArea textarea:focus { border-color: #2DD4BF !important; box-shadow: 0 0 0 3px rgba(45,212,191,0.12) !important; }
.stTextInput input {
    background: #0D1117 !important; border: 1px solid #1E2D45 !important;
    border-radius: 8px !important; color: #E2E8F0 !important;
}
.stTextInput input:focus { border-color: #2DD4BF !important; }

/* ── WIDGET LABELS ── */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] > div,
.stTextArea label, .stTextInput label, .stFileUploader label {
    color: #94A3B8 !important; font-size: 0.84rem !important; font-weight: 600 !important;
}
.stCaption, [data-testid="stCaptionContainer"] p { color: #4E6278 !important; font-size: 0.8rem !important; }
[data-testid="stMarkdownContainer"] p { color: #CBD5E1 !important; }

/* ── PROGRESS ── */
.stProgress > div > div { background: linear-gradient(90deg, #0D9488, #6366F1) !important; border-radius: 4px !important; }
[data-testid="stProgressBar"] { background: #1E2D45 !important; border-radius: 4px !important; }

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: #161D2E !important; border: 1px solid #1E2D45 !important;
    border-radius: 10px !important; padding: 20px 24px !important;
}
[data-testid="stMetricValue"] { color: #2DD4BF !important; font-size: 1.6rem !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] p { color: #4E6278 !important; font-size: 0.72rem !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }

/* ── DIVIDER ── */
.divider { border: none; border-top: 1px solid #1E2D45; margin: 22px 0; }

/* ── CARDS ── */
.info-card { background: #161D2E; border: 1px solid #1E2D45; border-radius: 10px; padding: 16px 20px; margin-bottom: 12px; }
.info-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #2DD4BF !important; margin-bottom: 7px; }
.info-value { font-size: 0.92rem; color: #C8D6E3 !important; line-height: 1.68; }
.lang-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(45,212,191,0.1); border: 1px solid rgba(45,212,191,0.28);
    color: #5EEAD4 !important; border-radius: 20px; padding: 5px 16px;
    font-size: 0.78rem; font-weight: 700; margin: 10px 0 6px;
}
.guidance-box {
    background: rgba(99,102,241,0.12); border-left: 3px solid #6366F1;
    border-radius: 0 8px 8px 0; padding: 14px 18px; margin-bottom: 18px;
    font-size: 0.86rem; color: #C7D2FE !important; line-height: 1.7;
}
.guidance-box strong { color: #E0E7FF !important; }
.guidance-box em { color: #A5B4FC !important; }
.guidance-box code {
    background: rgba(99,102,241,0.25); color: #E0E7FF !important;
    border-radius: 4px; padding: 2px 7px; font-weight: 700;
    border: 1px solid rgba(99,102,241,0.4); font-family: monospace !important;
}
.page-header { margin-bottom: 1.6rem; padding-bottom: 1rem; border-bottom: 1px solid #1E2D45; }
.page-header h2 { font-size: 1.35rem !important; font-weight: 700 !important; color: #F1F5F9 !important; margin: 0 0 4px !important; }
.page-header p { font-size: 0.84rem; color: #4E6278 !important; margin: 0; }

.hero-wrap {
    background: linear-gradient(135deg, #0F2942 0%, #1A1060 55%, #0B2E3A 100%);
    border: 1px solid #1E3A5F; border-radius: 16px; padding: 50px 48px 42px;
    margin-bottom: 2.2rem; position: relative; overflow: hidden;
}
.hero-wrap::before { content:""; position:absolute; top:-100px; right:-100px; width:350px; height:350px; background:radial-gradient(circle,rgba(45,212,191,0.08) 0%,transparent 70%); border-radius:50%; }
.hero-wrap::after  { content:""; position:absolute; bottom:-80px; left:20%; width:280px; height:280px; background:radial-gradient(circle,rgba(99,102,241,0.07) 0%,transparent 70%); border-radius:50%; }
.hero-title { font-size:2.1rem !important; font-weight:800 !important; color:#FFFFFF !important; margin:0 0 8px !important; position:relative; z-index:1; }
.hero-sub   { font-size:1rem; color:#BAC8D9 !important; margin:0 0 14px; font-weight:500; position:relative; z-index:1; }
.hero-desc  { font-size:0.875rem; color:#7D94AD !important; max-width:560px; line-height:1.72; margin:0 0 24px; position:relative; z-index:1; }
.hero-langs { display:flex; gap:8px; flex-wrap:wrap; position:relative; z-index:1; }
.hero-chip  { background:rgba(45,212,191,0.12); border:1px solid rgba(45,212,191,0.28); color:#5EEAD4 !important; border-radius:20px; padding:5px 15px; font-size:0.78rem; font-weight:600; }
.feat-grid  { display:grid; grid-template-columns:repeat(auto-fit,minmax(185px,1fr)); gap:14px; margin-bottom:2.5rem; }
.feat-card  { background:#161D2E; border:1px solid #1E2D45; border-radius:12px; padding:22px 18px; transition:border-color 0.2s,transform 0.15s; }
.feat-card:hover { border-color:#2DD4BF; transform:translateY(-3px); }
.feat-icon  { font-size:1.5rem; margin-bottom:10px; }
.feat-title { font-size:0.875rem; font-weight:700; color:#E8EBF0 !important; margin-bottom:5px; }
.feat-desc  { font-size:0.78rem; color:#4E6278 !important; line-height:1.6; }
.how-card   { background:#161D2E; border:1px solid #1E2D45; border-radius:12px; padding:28px 20px; text-align:center; height:100%; }
.how-num    { font-size:1.8rem; font-weight:800; color:#2DD4BF !important; margin-bottom:10px; opacity:0.7; }
.how-title  { font-size:0.9rem; font-weight:700; color:#E8EBF0 !important; margin-bottom:8px; }
.how-desc   { font-size:0.8rem; color:#4E6278 !important; line-height:1.65; }

/* ── HTML DATA TABLE (replaces st.dataframe) ── */
.data-table-wrap { overflow-x: auto; border-radius: 10px; border: 1px solid #1E2D45; margin-top: 1rem; }
.data-table {
    width: 100%; border-collapse: collapse;
    font-size: 0.82rem; background: #161D2E;
}
.data-table thead tr { background: #0D1117; }
.data-table thead th {
    color: #2DD4BF !important; font-weight: 700; text-transform: uppercase;
    font-size: 0.68rem; letter-spacing: 0.07em;
    padding: 12px 14px; text-align: left;
    border-bottom: 2px solid #1E2D45; white-space: nowrap;
}
.data-table tbody tr { border-bottom: 1px solid #1A2440; transition: background 0.15s; }
.data-table tbody tr:nth-child(even) { background: #111827; }
.data-table tbody tr:hover { background: #1A2847; }
.data-table tbody td {
    color: #CBD5E1 !important; padding: 10px 14px;
    vertical-align: top; line-height: 1.5;
    max-width: 260px; word-break: break-word;
}

/* ── FOOTER ── */
.app-footer {
    border-top: 1px solid #1E2D45;
    margin-top: 32px;
    padding: 16px 0 8px;
    text-align: center;
    font-size: 0.75rem;
    color: #E2E8F0 !important;
    font-weight: 500;
    letter-spacing: 0.02em;
}

[data-testid="stHorizontalBlock"] { gap: 1rem !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def render_df_as_html(df: pd.DataFrame, display_cols: list) -> None:
    """Render dataframe as a styled HTML table — bypasses st.dataframe iframe."""
    col_labels = {
        "ticket_id":         "Ticket ID",
        "timestamp":         "Timestamp",
        "original_language": "Language",
        "original_ticket":   "Original Ticket",
        "english_ticket":    "English Translation",
        "engineer_reply":    "Engineer Reply",
        "translated_reply":  "Translated Reply",
    }
    headers = "".join(
        f"<th>{col_labels.get(c, c)}</th>" for c in display_cols
    )
    rows = ""
    for _, row in df[display_cols].iterrows():
        cells = "".join(
            f"<td>{str(row[c]) if pd.notna(row[c]) else '—'}</td>"
            for c in display_cols
        )
        rows += f"<tr>{cells}</tr>"
    st.markdown(
        f"""<div class="data-table-wrap">
        <table class="data-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{rows}</tbody>
        </table></div>""",
        unsafe_allow_html=True,
    )


def run_detection_and_translation(ticket_text: str, ticket_id: str = "TICKET") -> dict:
    result = {
        "ticket_id": ticket_id, "original_language": None, "language_code": None,
        "original_ticket": ticket_text, "english_ticket": None,
        "term_map": {}, "glossary_terms": [], "error": None,
    }
    # FIXED: wrap detection in try/except so Malayalam/Tamil/Hindi never crash pipeline
    try:
        detection = detect_ticket_language(ticket_text)
    except Exception as exc:
        result["error"] = f"Language detection failed: {exc}"; return result

    if detection.get("error"):
        result["error"] = detection["error"]; return result

    language_name = detection.get("language_name", "") or "unknown"
    language_code = detection.get("language_code", "") or "xx"

    # FIXED: unsupported language → mark as unknown, use ticket text as-is, continue
    if language_name not in SUPPORTED_LANGUAGES:
        result["original_language"] = language_name
        result["language_code"]     = language_code
        result["english_ticket"]    = ticket_text   # best effort: treat as-is
        result["error"]             = None           # not a fatal error — pipeline continues
        # Attempt English translation anyway as a best-effort
        try:
            translation = translate_to_english(ticket_text, source_language="auto")
            if not translation.get("error"):
                result["english_ticket"] = translation.get("translated_text") or ticket_text
        except Exception:
            pass  # silently fall back to original
        return result

    result["original_language"] = language_name
    result["language_code"]     = language_code

    try:
        glossary_terms = load_glossary()
    except (FileNotFoundError, ValueError) as exc:
        result["error"] = f"Glossary error: {exc}"; return result

    # FIXED: wrap protect_terms in try/except for unusual Unicode (Malayalam etc.)
    try:
        protected_ticket, term_map = protect_terms(ticket_text, glossary_terms)
    except Exception:
        protected_ticket, term_map = ticket_text, {}

    result["term_map"]       = term_map
    result["glossary_terms"] = glossary_terms

    if language_name == "English":
        result["english_ticket"] = ticket_text
    else:
        # FIXED: wrap translation in try/except — never crash on any language
        try:
            translation = translate_to_english(protected_ticket, source_language=language_name)
            if translation.get("error"):
                result["error"] = translation["error"]; return result
            result["english_ticket"] = restore_terms(translation["translated_text"], term_map)
        except Exception as exc:
            result["error"] = f"Translation error: {exc}"; return result

    return result


def translate_engineer_reply(engineer_reply: str, language_name: str, glossary_terms: list) -> tuple:
    if language_name == "English":
        return engineer_reply, None
    protected_reply, reply_term_map = protect_terms(engineer_reply, glossary_terms)
    reply_translation = translate_from_english(protected_reply, target_language=language_name)
    if reply_translation.get("error"):
        return None, reply_translation["error"]
    return restore_terms(reply_translation["translated_text"], reply_term_map), None


# ══════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ══════════════════════════════════════════════════════════════════════════════
pages = ["Home", "Single Ticket", "Batch Processing", "Summary", "Export Results"]
active = st.session_state["active_page"]

indicator_colors = {
    "Home": "#2DD4BF", "Single Ticket": "#818CF8",
    "Batch Processing": "#F59E0B", "Summary": "#10B981", "Export Results": "#38BDF8",
}
active_color = indicator_colors.get(active, "#2DD4BF")
active_idx   = pages.index(active)

def go(p):
    st.session_state["active_page"] = p

st.markdown("""
<div class="navbar-outer">
    <span class="navbar-brand">🌐 &nbsp;Multilingual Ticket Translator</span>
</div>""", unsafe_allow_html=True)

# Per-active-button CSS
st.markdown(f"""<style>
div[data-testid="column"]:nth-child({active_idx + 2}) .stButton > button {{
    background: rgba(45,212,191,0.09) !important;
    color: {active_color} !important;
    border: 1px solid {active_color}55 !important;
    font-weight: 700 !important;
}}
</style>""", unsafe_allow_html=True)

spacer, *nav_cols = st.columns([1.6] + [1.0] * len(pages))
for col, p in zip(nav_cols, pages):
    with col:
        label = f"● {p}" if active == p else p
        if st.button(label, key=f"nav_{p}", use_container_width=True):
            go(p); st.rerun()

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
if active == "Home":
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-title">Multilingual Ticket Translator</div>
        <div class="hero-sub">AI-Powered Support Ticket Translation System</div>
        <div class="hero-desc">
            Automatically detect the language of incoming support tickets, translate them to English
            for your engineering team, and send responses back in the customer's native language —
            with glossary protection and automatic CSV storage.
        </div>
        <div class="hero-langs">
            <span class="hero-chip">🇮🇳 Telugu</span>
            <span class="hero-chip">🇮🇳 Hindi</span>
            <span class="hero-chip">🇮🇳 Tamil</span>
            <span class="hero-chip">🇮🇳 Kannada</span>
            <span class="hero-chip">🌍 English</span>
        </div>
    </div>
    <div class="feat-grid">
        <div class="feat-card"><div class="feat-icon">🔍</div><div class="feat-title">Language Detection</div><div class="feat-desc">Auto-identifies Telugu, Hindi, Tamil, Kannada, and English tickets instantly.</div></div>
        <div class="feat-card"><div class="feat-icon">🔄</div><div class="feat-title">Bidirectional Translation</div><div class="feat-desc">Translates tickets to English and replies back to the customer's language.</div></div>
        <div class="feat-card"><div class="feat-icon">🛡️</div><div class="feat-title">Glossary Protection</div><div class="feat-desc">Technical terms like VPN, Azure, and Outlook are never mistranslated.</div></div>
        <div class="feat-card"><div class="feat-icon">📂</div><div class="feat-title">Batch Processing</div><div class="feat-desc">Upload up to 10 ticket files and process them all in one workflow.</div></div>
        <div class="feat-card"><div class="feat-icon">💾</div><div class="feat-title">Auto Storage</div><div class="feat-desc">Every ticket is automatically saved to CSV after processing.</div></div>
        <div class="feat-card"><div class="feat-icon">⬇️</div><div class="feat-title">CSV Export</div><div class="feat-desc">Download all records in a clean CSV for reporting or handoff.</div></div>
    </div>
    <div class="page-header"><h2>How It Works</h2><p>End-to-end pipeline in three simple steps</p></div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, num, title, desc in [
        (c1,"01","Detect & Translate","Upload a ticket. The system detects its language and translates it to English for your engineer."),
        (c2,"02","Engineer Replies","Your engineer reads the English version and writes a reply in English — clear and straightforward."),
        (c3,"03","Translate & Save","The reply is translated back to the customer's language and saved to CSV automatically."),
    ]:
        with col:
            st.markdown(f'<div class="how-card"><div class="how-num">{num}</div><div class="how-title">{title}</div><div class="how-desc">{desc}</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SINGLE TICKET
# ══════════════════════════════════════════════════════════════════════════════
elif active == "Single Ticket":
    st.markdown('<div class="page-header"><h2>✏️ Single Ticket</h2><p>Paste a support ticket, detect its language, and translate it end-to-end.</p></div>', unsafe_allow_html=True)

    # ADDED: AI Agent toggle for single ticket
    ai_mode_single = st.toggle("🤖 Enable AI Agent Mode", value=False, key="ai_toggle_single",
                               help="Lets the AI pre-process the ticket: improve clarity, generate an English summary, and auto-assign category & priority.")

    ticket_input = st.text_area("Support Ticket", placeholder="Paste the customer's support ticket here…", height=130, key="single_ticket_input")

    if st.button("🔍 Detect & Translate", key="detect_btn"):
        if not ticket_input.strip():
            st.warning("Please paste a ticket before clicking Detect & Translate.")
        else:
            with st.spinner("Detecting language and translating…"):
                raw_ticket = ticket_input.strip()
                ai_result  = None

                # ADDED: AI pre-processing when toggle is ON
                if ai_mode_single:
                    with st.spinner("🤖 AI Agent analysing ticket…"):
                        ai_result = _run_ai_agent(raw_ticket)
                    # Use improved ticket for translation; fall back to original on error
                    ticket_for_pipeline = ai_result.get("improved_ticket") or raw_ticket
                    if ai_result.get("error"):
                        st.warning(f"⚠️ AI Agent: {ai_result['error']} — using original ticket.")
                else:
                    ticket_for_pipeline = raw_ticket

                res = run_detection_and_translation(ticket_for_pipeline, ticket_id="SINGLE-001")
                # Always store the true original (pre-AI) as original_ticket for display
                res["original_ticket"] = raw_ticket

                # ADDED: attach AI metadata to result for display
                if ai_result:
                    res["ai_summary"]  = ai_result.get("summary",  "")
                    res["ai_category"] = ai_result.get("category", "General")
                    res["ai_priority"] = ai_result.get("priority", "Medium")
                    res["ai_error"]    = ai_result.get("error")
                else:
                    res["ai_summary"]  = None
                    res["ai_category"] = None
                    res["ai_priority"] = None
                    res["ai_error"]    = None

            if res.get("error"):
                st.error(f"Pipeline error: {res['error']}")
            else:
                st.session_state["single_res"] = res
                st.session_state.pop("single_translated", None)
                st.session_state.pop("single_saved_id", None)

    if "single_res" in st.session_state:
        res = st.session_state["single_res"]
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f'<div class="info-card"><div class="info-label">Original Ticket</div><div class="info-value">{res.get("original_ticket","—")}</div></div>', unsafe_allow_html=True)
        with col_b:
            st.markdown(f'<div class="info-card"><div class="info-label">English Translation</div><div class="info-value">{res.get("english_ticket","—")}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="lang-badge">🌍 {res.get("original_language","—")} &nbsp;·&nbsp; {res.get("language_code","—")}</div>', unsafe_allow_html=True)

        # ADDED: display AI metadata panel when available
        if res.get("ai_summary"):
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.markdown('<div class="page-header" style="border-bottom:none;margin-bottom:0.6rem;"><h2>🤖 AI Analysis</h2></div>', unsafe_allow_html=True)
            ai_col1, ai_col2, ai_col3 = st.columns(3)
            with ai_col1:
                # FIXED: summary always shown — guaranteed English from agent prompt
                st.markdown(f'<div class="info-card"><div class="info-label">Summary (English)</div><div class="info-value">{res.get("ai_summary","—")}</div></div>', unsafe_allow_html=True)
            with ai_col2:
                st.markdown(f'<div class="info-card"><div class="info-label">Category</div><div class="info-value">{res.get("ai_category","—")}</div></div>', unsafe_allow_html=True)
            with ai_col3:
                priority = res.get("ai_priority", "—")
                priority_color = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}.get(priority, "#CBD5E1")
                st.markdown(f'<div class="info-card"><div class="info-label">Priority</div><div class="info-value" style="color:{priority_color};font-weight:700;">{priority}</div></div>', unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown('<div class="page-header" style="border-bottom:none;margin-bottom:0.8rem;"><h2>Engineer Reply</h2></div>', unsafe_allow_html=True)
        st.markdown("""<div class="guidance-box"><strong>Write your reply in English below.</strong> Leave the box empty to use the default response automatically.<br><br><strong>Default:</strong> <em>"Thank you for contacting support. We have received your request and are working on a resolution. We will provide an update as soon as possible."</em></div>""", unsafe_allow_html=True)

        engineer_reply = st.text_area("Engineer Reply (English)", placeholder="Type a custom reply, or leave empty to use the default response…", height=100, key="single_engineer_reply")

        if st.button("🔁 Translate Reply", key="translate_reply_btn"):
            reply_to_use = engineer_reply.strip() if engineer_reply.strip() else DEFAULT_REPLY
            with st.spinner("Translating reply back to customer language…"):
                try:
                    glossary_terms = res.get("glossary_terms") or load_glossary()
                except Exception:
                    glossary_terms = []
                # FIXED: safe .get() for original_language
                translated, err = translate_engineer_reply(reply_to_use, res.get("original_language", "English"), glossary_terms)
            if err:
                st.error(f"Translation error: {err}")
            else:
                st.session_state["single_translated"] = translated
                st.session_state["single_reply_used"] = reply_to_use
                try:
                    saved = save_ticket_record(
                        original_language=res.get("original_language"), original_ticket=res.get("original_ticket"),
                        english_ticket=res.get("english_ticket"), engineer_reply=reply_to_use,
                        translated_reply=translated, ticket_id=res.get("ticket_id"),
                    )
                    st.session_state["single_saved_id"]   = saved["ticket_id"]
                    st.session_state["single_saved_time"] = saved["timestamp"]
                    st.session_state.pop("single_save_err", None)
                except Exception as exc:
                    st.session_state["single_save_err"] = str(exc)

    if "single_translated" in st.session_state:
        reply_used = st.session_state["single_reply_used"]
        translated = st.session_state["single_translated"]
        res        = st.session_state["single_res"]
        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown(f'<div class="info-card"><div class="info-label">Engineer Reply (English)</div><div class="info-value">{reply_used}</div></div>', unsafe_allow_html=True)
        with col_d:
            st.markdown(f'<div class="info-card"><div class="info-label">Translated Reply ({res.get("original_language","—")})</div><div class="info-value">{translated}</div></div>', unsafe_allow_html=True)
        if st.session_state.get("single_save_err"):
            st.error(f"Save error: {st.session_state['single_save_err']}")
        elif st.session_state.get("single_saved_id"):
            st.success(f"✅ Record saved — ID: {st.session_state['single_saved_id']}  |  {st.session_state['single_saved_time']}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BATCH PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
elif active == "Batch Processing":
    st.markdown('<div class="page-header"><h2>📂 Batch Processing</h2><p>Upload multiple ticket files and process them in one workflow.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="guidance-box"><strong>Upload up to 10 TXT files.</strong><br>To upload all files from a folder at once: Open the folder → press <code>Ctrl + A</code> to select all → click <strong>Open</strong>.</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Upload ticket files (.txt)", type=["txt"], accept_multiple_files=True, key="batch_upload")

    # ADDED: AI Agent toggle for batch processing
    ai_mode_batch = st.toggle("🤖 Enable AI Agent Mode (Batch)", value=False, key="ai_toggle_batch",
                              help="AI will pre-process each ticket: improve clarity, generate an English summary, and auto-assign category & priority.")

    if uploaded_files and len(uploaded_files) > 10:
        st.error("Maximum 10 files allowed. Please remove extra files and re-upload.")
        uploaded_files = []

    if uploaded_files:
        st.caption(f"{len(uploaded_files)} file(s) selected and ready to process.")
        if st.button("⚙️ Process Tickets", key="process_tickets_btn"):
            st.session_state.pop("batch_processed", None)
            st.session_state.pop("batch_final", None)
            st.session_state.pop("batch_empty_indices", None)
            processed = []
            progress  = st.progress(0, text="Processing…")
            total     = len(uploaded_files)
            for idx, uf in enumerate(uploaded_files):
                progress.progress(idx / total, text=f"Processing {idx+1}/{total}: {uf.name}")
                try:
                    content = uf.read().decode("utf-8").strip(); uf.seek(0)
                except Exception as exc:
                    processed.append({"filename": uf.name, "error": f"Could not read: {exc}"}); continue
                if not content:
                    processed.append({"filename": uf.name, "error": "File is empty."}); continue

                ticket_id  = os.path.splitext(uf.name)[0].upper()
                raw_ticket = content

                # ADDED: AI pre-processing per ticket when batch AI toggle is ON
                ai_result = None
                if ai_mode_batch:
                    try:
                        ai_result = _run_ai_agent(raw_ticket)
                        ticket_for_pipeline = ai_result.get("improved_ticket") or raw_ticket
                    except Exception:
                        ticket_for_pipeline = raw_ticket  # FIXED: never crash pipeline
                else:
                    ticket_for_pipeline = raw_ticket

                # FIXED: wrap per-ticket pipeline in try/except so one bad ticket never breaks the batch
                try:
                    res = run_detection_and_translation(ticket_for_pipeline, ticket_id=ticket_id)
                except Exception as exc:
                    processed.append({"filename": uf.name, "error": f"Pipeline error: {exc}"}); continue

                # Always preserve the original (pre-AI) text for display
                res["original_ticket"] = raw_ticket
                res["filename"]        = uf.name

                # ADDED: attach AI metadata to each batch result
                if ai_result:
                    res["ai_summary"]  = ai_result.get("summary",  "")
                    res["ai_category"] = ai_result.get("category", "General")
                    res["ai_priority"] = ai_result.get("priority", "Medium")
                    res["ai_error"]    = ai_result.get("error")
                else:
                    res["ai_summary"]  = None
                    res["ai_category"] = None
                    res["ai_priority"] = None
                    res["ai_error"]    = None

                processed.append(res)

            progress.progress(1.0, text="Detection & translation complete.")
            st.session_state["batch_processed"] = processed
            st.success("✅ Tickets processed. Enter engineer replies below.")

    if "batch_processed" in st.session_state:
        processed = st.session_state["batch_processed"]
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown('<div class="page-header" style="border-bottom:none;margin-bottom:1rem;"><h2>Review Tickets &amp; Enter Replies</h2><p>Review each ticket and write an English reply before submitting.</p></div>', unsafe_allow_html=True)

        for idx, res in enumerate(processed):
            ticket_num = idx + 1
            fname      = res.get("filename", f"ticket_{ticket_num}.txt")
            has_error  = bool(res.get("error"))
            icon       = "⚠️" if has_error else "🎫"
            with st.expander(f"{icon}  Ticket {ticket_num}  ·  {fname}", expanded=True):
                if has_error:
                    st.error(f"Error: {res['error']}")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f'<div class="info-card"><div class="info-label">File Name</div><div class="info-value">{fname}</div></div><div class="info-card"><div class="info-label">Original Ticket</div><div class="info-value">{res.get("original_ticket","—")}</div></div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="info-card"><div class="info-label">Detected Language</div><div class="info-value">{res.get("original_language","—")} ({res.get("language_code","—")})</div></div><div class="info-card"><div class="info-label">English Translation</div><div class="info-value">{res.get("english_ticket","—")}</div></div>', unsafe_allow_html=True)
                    # ADDED: show AI metadata row when available
                    if res.get("ai_summary"):
                        ai_c1, ai_c2, ai_c3 = st.columns(3)
                        with ai_c1:
                            # FIXED: summary always English — guaranteed by agent prompt
                            st.markdown(f'<div class="info-card"><div class="info-label">🤖 Summary (English)</div><div class="info-value">{res.get("ai_summary","—")}</div></div>', unsafe_allow_html=True)
                        with ai_c2:
                            st.markdown(f'<div class="info-card"><div class="info-label">🤖 Category</div><div class="info-value">{res.get("ai_category","—")}</div></div>', unsafe_allow_html=True)
                        with ai_c3:
                            priority = res.get("ai_priority","—")
                            priority_color = {"High":"#EF4444","Medium":"#F59E0B","Low":"#10B981"}.get(priority,"#CBD5E1")
                            st.markdown(f'<div class="info-card"><div class="info-label">🤖 Priority</div><div class="info-value" style="color:{priority_color};font-weight:700;">{priority}</div></div>', unsafe_allow_html=True)
                        if res.get("ai_error"):
                            st.caption(f"⚠️ AI note: {res['ai_error']}")
                    st.caption("Enter your reply below. Leave empty to use the default response during submission.")
                    st.text_area("Engineer Reply", placeholder="Type your English reply here…", height=90, key=f"batch_reply_{idx}")

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        if st.button("🚀 Translate & Save All", key="translate_save_all_btn"):
            valid_tickets = []; empty_indices = []
            for idx, res in enumerate(processed):
                if res.get("error"): continue
                reply = st.session_state.get(f"batch_reply_{idx}", "").strip()
                if not reply: empty_indices.append(idx)
                else: valid_tickets.append((idx, res, reply))
            if empty_indices:
                st.session_state["batch_empty_indices"]      = empty_indices
                st.session_state["batch_valid_before_empty"] = valid_tickets
                for i in empty_indices:
                    st.warning(f"⚠️ Ticket {i+1} ({processed[i].get('filename','')}) has no reply.")
            else:
                st.session_state.pop("batch_empty_indices", None)
                st.session_state["batch_ready_to_finalize"]   = True
                st.session_state["batch_tickets_to_finalize"] = valid_tickets

        if "batch_empty_indices" in st.session_state:
            empty_indices = st.session_state["batch_empty_indices"]
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.markdown('<div class="page-header" style="border-bottom:none;margin-bottom:0.8rem;"><h2>⚠️ Some tickets have no reply</h2><p>Choose how to handle tickets with empty reply boxes.</p></div>', unsafe_allow_html=True)
            col_def, col_ret = st.columns(2)
            with col_def:
                if st.button("✅ Use Default Reply for empty tickets", key="use_default_btn"):
                    all_to_finalize = list(st.session_state.get("batch_valid_before_empty", []))
                    for i in empty_indices:
                        res = processed[i]
                        if not res.get("error"): all_to_finalize.append((i, res, DEFAULT_REPLY))
                    st.session_state["batch_tickets_to_finalize"] = all_to_finalize
                    st.session_state["batch_ready_to_finalize"]   = True
                    st.session_state.pop("batch_empty_indices", None)
            with col_ret:
                if st.button("✏️ Return and Edit", key="return_edit_btn"):
                    st.session_state.pop("batch_empty_indices", None)
                    st.session_state.pop("batch_ready_to_finalize", None)
                    st.info("Scroll up and fill in the missing replies, then click Translate & Save All again.")

        if st.session_state.get("batch_ready_to_finalize"):
            tickets_to_finalize = st.session_state.get("batch_tickets_to_finalize", [])
            st.session_state.pop("batch_ready_to_finalize", None)
            st.session_state.pop("batch_tickets_to_finalize", None)
            final_results = []; total_fin = len(tickets_to_finalize)
            fin_progress = st.progress(0, text="Translating & saving…")
            try: glossary_terms = load_glossary()
            except Exception: glossary_terms = []
            for step, (idx, res, reply) in enumerate(tickets_to_finalize):
                fin_progress.progress(step / total_fin, text=f"Saving {step+1}/{total_fin}: {res.get('filename','')}")
                translated_reply, err = translate_engineer_reply(reply, res["original_language"], glossary_terms)
                entry = {**res, "engineer_reply": reply, "translated_reply": None, "save_status": None, "save_error": None}
                if err:
                    entry["save_status"] = "error"; entry["save_error"] = err
                else:
                    entry["translated_reply"] = translated_reply
                    try:
                        saved = save_ticket_record(
                            original_language=res["original_language"], original_ticket=res["original_ticket"],
                            english_ticket=res["english_ticket"], engineer_reply=reply,
                            translated_reply=translated_reply, ticket_id=res["ticket_id"],
                        )
                        entry["save_status"] = "ok"; entry["saved_id"] = saved["ticket_id"]; entry["saved_time"] = saved["timestamp"]
                    except Exception as exc:
                        entry["save_status"] = "error"; entry["save_error"] = str(exc)
                final_results.append(entry)
            fin_progress.progress(1.0, text="Done!")
            st.session_state["batch_final"] = final_results

        if "batch_final" in st.session_state:
            final_results = st.session_state["batch_final"]
            fail_count = sum(1 for r in final_results if r.get("save_status") != "ok")
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            if fail_count == 0: st.success("✅ All Tickets Processed  ·  ✅ Records Saved To CSV  ·  ✅ Ready For Download")
            else: st.warning(f"Completed with {fail_count} error(s). Check individual tickets below.")
            st.markdown('<div class="page-header" style="border-bottom:none;margin-top:1rem;margin-bottom:1rem;"><h2>Final Results</h2></div>', unsafe_allow_html=True)
            for entry in final_results:
                status_icon = "✅" if entry.get("save_status") == "ok" else "❌"
                with st.expander(f"{status_icon}  {entry.get('filename','—')}  ·  {entry.get('original_language','—')}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f'<div class="info-card"><div class="info-label">File Name</div><div class="info-value">{entry.get("filename","—")}</div></div><div class="info-card"><div class="info-label">Original Ticket</div><div class="info-value">{entry.get("original_ticket","—")}</div></div><div class="info-card"><div class="info-label">Engineer Reply</div><div class="info-value">{entry.get("engineer_reply","—")}</div></div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="info-card"><div class="info-label">Detected Language</div><div class="info-value">{entry.get("original_language","—")} ({entry.get("language_code","—")})</div></div><div class="info-card"><div class="info-label">English Translation</div><div class="info-value">{entry.get("english_ticket","—")}</div></div><div class="info-card"><div class="info-label">Final Translated Reply ({entry.get("original_language","—")})</div><div class="info-value">{entry.get("translated_reply","—")}</div></div>', unsafe_allow_html=True)
                    if entry.get("save_status") == "ok": st.success(f"✅ Saved  |  ID: {entry.get('saved_id')}  |  {entry.get('saved_time')}")
                    else: st.error(f"❌ Save failed: {entry.get('save_error')}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
elif active == "Summary":
    st.markdown('<div class="page-header"><h2>📊 Summary</h2><p>Overview of all processed and saved ticket records.</p></div>', unsafe_allow_html=True)
    st.button("🔄 Refresh", key="refresh_csv_summary")

    if os.path.exists(OUTPUT_CSV):
        try:
            df = pd.read_csv(OUTPUT_CSV, encoding="utf-8")
            if df.empty:
                st.info("No records yet. Process some tickets first.")
            else:
                total_tickets = len(df)
                languages     = df["original_language"].nunique() if "original_language" in df.columns else 0
                latest_time   = df["timestamp"].iloc[-1] if "timestamp" in df.columns else "—"
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Tickets", total_tickets)
                m2.metric("Languages",     languages)
                m3.metric("Latest Save",   str(latest_time)[:16])
                st.markdown("<hr class='divider'>", unsafe_allow_html=True)
                display_cols = [c for c in ["ticket_id","timestamp","original_language","original_ticket","english_ticket","engineer_reply","translated_reply"] if c in df.columns]
                render_df_as_html(df, display_cols)
        except Exception as exc:
            st.error(f"Could not read {OUTPUT_CSV}: {exc}")
    else:
        st.info(f"`{OUTPUT_CSV}` not found. Process at least one ticket first.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EXPORT RESULTS
# ══════════════════════════════════════════════════════════════════════════════
elif active == "Export Results":
    st.markdown('<div class="page-header"><h2>⬇️ Export Results</h2><p>Download all processed ticket records as a CSV file.</p></div>', unsafe_allow_html=True)

    if os.path.exists(OUTPUT_CSV):
        try:
            df = pd.read_csv(OUTPUT_CSV, encoding="utf-8")
            if df.empty:
                st.button("🔄 Refresh", key="refresh_csv_export")
                st.info("No records found. Process some tickets first.")
            else:
                total_tickets = len(df)
                languages     = df["original_language"].nunique() if "original_language" in df.columns else 0
                latest_time   = df["timestamp"].iloc[-1] if "timestamp" in df.columns else "—"

                csv_bytes = df.to_csv(index=False).encode("utf-8")
                btn_col1, btn_col2, btn_spacer = st.columns([1, 1.4, 4])
                with btn_col1:
                    st.button("🔄 Refresh", key="refresh_csv_export")
                with btn_col2:
                    st.download_button(
                        label="⬇️  Download CSV",
                        data=csv_bytes,
                        file_name="multilingual_tickets.csv",
                        mime="text/csv",
                        key="dl_csv_export",
                    )

                st.markdown(f'<div class="info-card" style="margin-top:14px;"><div class="info-label">File Details</div><div class="info-value" style="font-size:0.82rem;color:#94A3B8;">Filename: multilingual_tickets.csv &nbsp;·&nbsp; Rows: {total_tickets} &nbsp;·&nbsp; Columns: {len(df.columns)}</div></div>', unsafe_allow_html=True)

                st.markdown("<hr class='divider'>", unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Records",     total_tickets)
                m2.metric("Languages Covered", languages)
                m3.metric("Last Updated",      str(latest_time)[:16])

                st.markdown("<hr class='divider'>", unsafe_allow_html=True)
                display_cols = [c for c in ["ticket_id","timestamp","original_language","original_ticket","english_ticket","engineer_reply","translated_reply"] if c in df.columns]
                render_df_as_html(df, display_cols)

        except Exception as exc:
            st.error(f"Could not read {OUTPUT_CSV}: {exc}")
    else:
        st.button("🔄 Refresh", key="refresh_csv_export")
        st.info(f"`{OUTPUT_CSV}` not found. Process at least one ticket first.")


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    Multilingual Ticket Translator &nbsp;·&nbsp; Infinite Computer Solutions AI Prototype Challenge
</div>
""", unsafe_allow_html=True)
