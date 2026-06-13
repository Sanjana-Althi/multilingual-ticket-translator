"""
app.py
------
Project : Multilingual Ticket Translator
Module  : Streamlit Frontend
Challenge: Infinite Computer Solutions AI Prototype Challenge

Run with: streamlit run app.py
"""

import os
import pandas as pd
import streamlit as st

# ── Backend imports ────────────────────────────────────────────────────────────
from detector import detect_ticket_language
from translator import translate_to_english, translate_from_english
from glossary_handler import load_glossary, protect_terms, restore_terms
from storage import save_ticket_record
# ──────────────────────────────────────────────────────────────────────────────

SUPPORTED_LANGUAGES = {"Telugu", "Hindi", "Tamil", "Kannada", "English"}
DEFAULT_REPLY       = (
    "Thank you for contacting support. We have received your request and are "
    "working on a resolution. We will provide an update as soon as possible."
)
OUTPUT_CSV = os.path.join("output", "tickets.csv")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multilingual Ticket Translator",
    page_icon="🌐",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

.app-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    border-radius: 12px;
    padding: 28px 36px 20px;
    margin-bottom: 24px;
    color: #ffffff;
}
.app-header h1 { margin: 0; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }
.app-header p  { margin: 6px 0 0; font-size: 0.95rem; color: #94a3b8; }

.lang-badge {
    display: inline-block;
    background: #0f3460;
    color: #e2e8f0;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-top: 4px;
}

.card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 14px;
}
.card-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748b;
    margin-bottom: 6px;
}
.card-value {
    font-size: 1rem;
    color: #1e293b;
    line-height: 1.6;
}

.guidance-box {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 14px;
    font-size: 0.9rem;
    color: #1e40af;
}

hr.soft { border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>🌐 Multilingual Ticket Translator</h1>
    <p>AI-powered support ticket translation · Telugu · Hindi · Tamil · Kannada · English</p>
</div>
""", unsafe_allow_html=True)


# ── Shared helpers ─────────────────────────────────────────────────────────────
def run_detection_and_translation(ticket_text: str, ticket_id: str = "TICKET") -> dict:
    """Detect language and translate ticket to English only. Does not translate reply."""
    result = {
        "ticket_id":         ticket_id,
        "original_language": None,
        "language_code":     None,
        "original_ticket":   ticket_text,
        "english_ticket":    None,
        "error":             None,
    }

    # ── BACKEND CALL: detect language ──────────────────────────
    detection = detect_ticket_language(ticket_text)
    if detection.get("error"):
        result["error"] = detection["error"]
        return result

    language_name = detection.get("language_name", "")
    language_code = detection.get("language_code", "")

    if language_name not in SUPPORTED_LANGUAGES:
        result["error"] = f"Unsupported language: {language_name}"
        return result

    result["original_language"] = language_name
    result["language_code"]     = language_code

    # ── BACKEND CALL: load glossary ────────────────────────────
    try:
        glossary_terms = load_glossary()
    except (FileNotFoundError, ValueError) as exc:
        result["error"] = f"Glossary error: {exc}"
        return result

    # ── BACKEND CALL: protect terms ────────────────────────────
    protected_ticket, term_map = protect_terms(ticket_text, glossary_terms)
    result["term_map"] = term_map
    result["glossary_terms"] = glossary_terms

    # ── BACKEND CALL: translate ticket → English ───────────────
    if language_name == "English":
        result["english_ticket"] = ticket_text
    else:
        translation = translate_to_english(protected_ticket, source_language=language_name)
        if translation.get("error"):
            result["error"] = translation["error"]
            return result
        result["english_ticket"] = restore_terms(translation["translated_text"], term_map)

    return result


def translate_engineer_reply(engineer_reply: str, language_name: str, glossary_terms: list) -> tuple:
    """Translate engineer reply back to original language. Returns (translated_reply, error)."""
    if language_name == "English":
        return engineer_reply, None

    # ── BACKEND CALL: protect terms in reply ──────────────────
    protected_reply, reply_term_map = protect_terms(engineer_reply, glossary_terms)

    # ── BACKEND CALL: translate reply → original language ─────
    reply_translation = translate_from_english(protected_reply, target_language=language_name)
    if reply_translation.get("error"):
        return None, reply_translation["error"]

    # ── BACKEND CALL: restore terms ───────────────────────────
    translated_reply = restore_terms(reply_translation["translated_text"], reply_term_map)
    return translated_reply, None


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["✏️  Single Ticket", "📂  Batch Processing", "📊  Summary & Export"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SINGLE TICKET
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Single Ticket Translation")
    st.caption("Paste a support ticket, detect its language, and translate it end-to-end.")

    ticket_input = st.text_area(
        "Support Ticket",
        placeholder="Paste the customer's support ticket here…",
        height=130,
        key="single_ticket_input",
    )

    if st.button("🔍 Detect & Translate", type="primary", key="detect_btn"):
        if not ticket_input.strip():
            st.warning("Please paste a ticket before clicking Detect & Translate.")
        else:
            with st.spinner("Detecting language and translating…"):
                res = run_detection_and_translation(ticket_input.strip(), ticket_id="SINGLE-001")
            if res["error"]:
                st.error(f"Pipeline error: {res['error']}")
            else:
                st.session_state["single_res"] = res
                st.session_state.pop("single_translated", None)

    if "single_res" in st.session_state:
        res = st.session_state["single_res"]

        st.markdown("<hr class='soft'>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="card">
                <div class="card-label">Original Ticket</div>
                <div class="card-value">{res['original_ticket']}</div>
            </div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div class="card">
                <div class="card-label">English Translation</div>
                <div class="card-value">{res['english_ticket']}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<div class='lang-badge'>🌍 {res['original_language']} &nbsp;·&nbsp; {res['language_code']}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<hr class='soft'>", unsafe_allow_html=True)
        st.subheader("Engineer Reply")

        st.markdown("""
        <div class="guidance-box">
            <strong>Press Enter to provide a custom reply.</strong><br>
            Default Response: <em>"Thank you for contacting support. We have received your request
            and are working on a resolution. We will provide an update as soon as possible."</em>
        </div>
        """, unsafe_allow_html=True)

        engineer_reply = st.text_area(
            "Write your reply in English",
            placeholder="Type your custom reply here, or leave empty to use the default response…",
            height=100,
            key="single_engineer_reply",
        )

        if st.button("🔁 Translate Reply", type="primary", key="translate_reply_btn"):
            reply_to_use = engineer_reply.strip() if engineer_reply.strip() else DEFAULT_REPLY
            with st.spinner("Translating reply back to customer language…"):
                try:
                    glossary_terms = res.get("glossary_terms") or load_glossary()
                except Exception:
                    glossary_terms = []
                translated, err = translate_engineer_reply(
                    reply_to_use, res["original_language"], glossary_terms
                )
            if err:
                st.error(f"Translation error: {err}")
            else:
                st.session_state["single_translated"]   = translated
                st.session_state["single_reply_used"]   = reply_to_use

                # ── Auto-save ──────────────────────────────────────────
                try:
                    saved = save_ticket_record(
                        original_language = res["original_language"],
                        original_ticket   = res["original_ticket"],
                        english_ticket    = res["english_ticket"],
                        engineer_reply    = reply_to_use,
                        translated_reply  = translated,
                        ticket_id         = res["ticket_id"],
                    )
                    st.session_state["single_saved_id"]   = saved["ticket_id"]
                    st.session_state["single_saved_time"] = saved["timestamp"]
                except Exception as exc:
                    st.session_state["single_save_err"] = str(exc)

    if "single_translated" in st.session_state:
        reply_used   = st.session_state["single_reply_used"]
        translated   = st.session_state["single_translated"]
        res          = st.session_state["single_res"]

        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown(f"""
            <div class="card">
                <div class="card-label">Engineer Reply (English)</div>
                <div class="card-value">{reply_used}</div>
            </div>""", unsafe_allow_html=True)
        with col_d:
            st.markdown(f"""
            <div class="card">
                <div class="card-label">Translated Reply ({res['original_language']})</div>
                <div class="card-value">{translated}</div>
            </div>""", unsafe_allow_html=True)

        if "single_save_err" in st.session_state:
            st.error(f"Save error: {st.session_state['single_save_err']}")
        elif "single_saved_id" in st.session_state:
            st.success(
                f"✅ Record saved — ID: {st.session_state['single_saved_id']}  "
                f"|  {st.session_state['single_saved_time']}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — BATCH PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Batch Processing")

    st.markdown("""
    <div class="guidance-box">
        <strong>Upload up to 10 TXT files.</strong><br>
        To upload all files from a folder: Open the folder, press <strong>Ctrl + A</strong>,
        then click <strong>Open</strong>.
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload ticket files (.txt)",
        type=["txt"],
        accept_multiple_files=True,
        key="batch_upload",
    )

    if uploaded_files and len(uploaded_files) > 10:
        st.error("Maximum 10 files allowed. Please remove extra files and re-upload.")
        uploaded_files = []

    # ── STEP 1: Process Tickets (detect + translate only) ─────────────────────
    if uploaded_files:
        st.caption(f"{len(uploaded_files)} file(s) selected.")

        if st.button("⚙️ Process Tickets", type="primary", key="process_tickets_btn"):
            st.session_state.pop("batch_processed", None)
            st.session_state.pop("batch_final", None)
            st.session_state.pop("batch_validation_errors", None)

            processed = []
            progress   = st.progress(0, text="Processing…")
            total      = len(uploaded_files)

            for idx, uf in enumerate(uploaded_files):
                progress.progress((idx) / total, text=f"Processing {idx+1}/{total}: {uf.name}")
                try:
                    content = uf.read().decode("utf-8").strip()
                    uf.seek(0)
                except Exception as exc:
                    processed.append({
                        "filename": uf.name,
                        "error": f"Could not read file: {exc}",
                    })
                    continue

                if not content:
                    processed.append({"filename": uf.name, "error": "File is empty."})
                    continue

                ticket_id = os.path.splitext(uf.name)[0].upper()
                res = run_detection_and_translation(content, ticket_id=ticket_id)
                res["filename"] = uf.name
                processed.append(res)

            progress.progress(1.0, text="Detection & translation complete.")
            st.session_state["batch_processed"] = processed
            st.success("✅ Tickets processed. Please review and enter engineer replies below.")

    # ── STEP 2: Display tickets with engineer reply boxes ─────────────────────
    if "batch_processed" in st.session_state:
        processed = st.session_state["batch_processed"]
        st.markdown("<hr class='soft'>", unsafe_allow_html=True)
        st.subheader("Review Tickets & Enter Replies")

        for idx, res in enumerate(processed):
            ticket_num = idx + 1
            fname      = res.get("filename", f"ticket_{ticket_num}.txt")
            has_error  = bool(res.get("error"))

            label = f"Ticket {ticket_num}  ·  {fname}" + (" ⚠️" if has_error else "")
            with st.expander(label, expanded=True):
                if has_error:
                    st.error(f"Error: {res['error']}")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div class="card">
                            <div class="card-label">File Name</div>
                            <div class="card-value">{fname}</div>
                        </div>
                        <div class="card">
                            <div class="card-label">Original Ticket</div>
                            <div class="card-value">{res['original_ticket']}</div>
                        </div>""", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="card">
                            <div class="card-label">Detected Language</div>
                            <div class="card-value">{res['original_language']} ({res['language_code']})</div>
                        </div>
                        <div class="card">
                            <div class="card-label">English Translation</div>
                            <div class="card-value">{res['english_ticket']}</div>
                        </div>""", unsafe_allow_html=True)

                    st.caption("Enter engineer reply below. If left empty, you may choose the default response during submission.")
                    st.text_area(
                        "Engineer Reply",
                        placeholder="Type your reply in English…",
                        height=90,
                        key=f"batch_reply_{idx}",
                    )

        # ── STEP 3: Translate & Save All ──────────────────────────────────────
        st.markdown("<hr class='soft'>", unsafe_allow_html=True)

        if st.button("🚀 Translate & Save All", type="primary", key="translate_save_all_btn"):
            valid_tickets  = []
            empty_indices  = []

            for idx, res in enumerate(processed):
                if res.get("error"):
                    continue
                reply = st.session_state.get(f"batch_reply_{idx}", "").strip()
                if not reply:
                    empty_indices.append(idx)
                else:
                    valid_tickets.append((idx, res, reply))

            # ── Validation ────────────────────────────────────────────
            if empty_indices:
                st.session_state["batch_empty_indices"] = empty_indices
                st.session_state["batch_valid_before_empty"] = valid_tickets
                for i in empty_indices:
                    fname_i = processed[i].get("filename", f"Ticket {i+1}")
                    st.warning(
                        f"⚠️ Ticket {i+1} ({fname_i}) does not contain an engineer reply."
                    )
            else:
                st.session_state.pop("batch_empty_indices", None)
                st.session_state["batch_ready_to_finalize"] = True
                st.session_state["batch_tickets_to_finalize"] = [
                    (idx, res, reply) for idx, res, reply in valid_tickets
                ]

        # ── Empty ticket resolution ───────────────────────────────────────────
        if "batch_empty_indices" in st.session_state:
            empty_indices = st.session_state["batch_empty_indices"]
            st.markdown("<hr class='soft'>", unsafe_allow_html=True)
            st.subheader("⚠️ Some tickets have no reply")

            col_def, col_ret = st.columns(2)
            with col_def:
                if st.button("✅ Use Default Reply for empty tickets", key="use_default_btn"):
                    all_to_finalize = list(st.session_state.get("batch_valid_before_empty", []))
                    for i in empty_indices:
                        res = processed[i]
                        if not res.get("error"):
                            all_to_finalize.append((i, res, DEFAULT_REPLY))
                    st.session_state["batch_tickets_to_finalize"] = all_to_finalize
                    st.session_state["batch_ready_to_finalize"]   = True
                    st.session_state.pop("batch_empty_indices", None)
            with col_ret:
                if st.button("✏️ Return and Edit", key="return_edit_btn"):
                    st.session_state.pop("batch_empty_indices", None)
                    st.session_state.pop("batch_ready_to_finalize", None)
                    st.info("Please scroll up and fill in the missing replies, then click Translate & Save All again.")

        # ── Final processing ──────────────────────────────────────────────────
        if st.session_state.get("batch_ready_to_finalize"):
            tickets_to_finalize = st.session_state.get("batch_tickets_to_finalize", [])
            st.session_state.pop("batch_ready_to_finalize", None)
            st.session_state.pop("batch_tickets_to_finalize", None)

            final_results = []
            total_fin     = len(tickets_to_finalize)
            fin_progress  = st.progress(0, text="Translating & saving…")

            try:
                glossary_terms = load_glossary()
            except Exception:
                glossary_terms = []

            for step, (idx, res, reply) in enumerate(tickets_to_finalize):
                fin_progress.progress(
                    step / total_fin,
                    text=f"Saving {step+1}/{total_fin}: {res.get('filename', '')}",
                )

                translated_reply, err = translate_engineer_reply(
                    reply, res["original_language"], glossary_terms
                )

                entry = {**res, "engineer_reply": reply, "translated_reply": None, "save_status": None, "save_error": None}

                if err:
                    entry["save_status"] = "error"
                    entry["save_error"]  = err
                else:
                    entry["translated_reply"] = translated_reply
                    try:
                        saved = save_ticket_record(
                            original_language = res["original_language"],
                            original_ticket   = res["original_ticket"],
                            english_ticket    = res["english_ticket"],
                            engineer_reply    = reply,
                            translated_reply  = translated_reply,
                            ticket_id         = res["ticket_id"],
                        )
                        entry["save_status"] = "ok"
                        entry["saved_id"]    = saved["ticket_id"]
                        entry["saved_time"]  = saved["timestamp"]
                    except Exception as exc:
                        entry["save_status"] = "error"
                        entry["save_error"]  = str(exc)

                final_results.append(entry)

            fin_progress.progress(1.0, text="Done!")
            st.session_state["batch_final"] = final_results

        # ── Display final results ─────────────────────────────────────────────
        if "batch_final" in st.session_state:
            final_results = st.session_state["batch_final"]
            success_count = sum(1 for r in final_results if r.get("save_status") == "ok")
            fail_count    = len(final_results) - success_count

            st.markdown("<hr class='soft'>", unsafe_allow_html=True)

            if fail_count == 0:
                st.success(
                    "✅ All Tickets Processed Successfully  ·  "
                    "✅ Records Saved To CSV  ·  "
                    "✅ Ready For Download"
                )
            else:
                st.warning(f"Completed with {fail_count} error(s). Check individual tickets below.")

            st.subheader("Final Results")
            for entry in final_results:
                status_icon = "✅" if entry.get("save_status") == "ok" else "❌"
                with st.expander(
                    f"{status_icon}  Ticket — {entry.get('filename', '—')}  ·  {entry.get('original_language', '—')}",
                    expanded=False,
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div class="card">
                            <div class="card-label">File Name</div>
                            <div class="card-value">{entry.get('filename', '—')}</div>
                        </div>
                        <div class="card">
                            <div class="card-label">Original Ticket</div>
                            <div class="card-value">{entry.get('original_ticket', '—')}</div>
                        </div>
                        <div class="card">
                            <div class="card-label">Engineer Reply</div>
                            <div class="card-value">{entry.get('engineer_reply', '—')}</div>
                        </div>""", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="card">
                            <div class="card-label">Detected Language</div>
                            <div class="card-value">{entry.get('original_language', '—')} ({entry.get('language_code', '—')})</div>
                        </div>
                        <div class="card">
                            <div class="card-label">English Translation</div>
                            <div class="card-value">{entry.get('english_ticket', '—')}</div>
                        </div>
                        <div class="card">
                            <div class="card-label">Final Translated Reply ({entry.get('original_language', '—')})</div>
                            <div class="card-value">{entry.get('translated_reply', '—')}</div>
                        </div>""", unsafe_allow_html=True)

                    if entry.get("save_status") == "ok":
                        st.success(
                            f"✅ Saved Successfully  |  ID: {entry.get('saved_id')}  |  {entry.get('saved_time')}"
                        )
                    else:
                        st.error(f"❌ Save failed: {entry.get('save_error')}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SUMMARY & EXPORT
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Summary & Export")
    st.caption("All saved records from output/tickets.csv")

    st.button("🔄 Refresh", key="refresh_csv")

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

                st.markdown("<hr class='soft'>", unsafe_allow_html=True)

                display_cols = [
                    c for c in
                    ["ticket_id", "timestamp", "original_language", "original_ticket",
                     "english_ticket", "engineer_reply", "translated_reply"]
                    if c in df.columns
                ]

                st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

                csv_bytes = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_bytes,
                    file_name="multilingual_tickets.csv",
                    mime="text/csv",
                    type="primary",
                )
        except Exception as exc:
            st.error(f"Could not read {OUTPUT_CSV}: {exc}")
    else:
        st.info(
            f"`{OUTPUT_CSV}` not found yet. "
            "Process at least one ticket to generate the output file."
        )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<hr class='soft'>", unsafe_allow_html=True)
st.caption("Multilingual Ticket Translator · Infinite Computer Solutions AI Prototype Challenge")
