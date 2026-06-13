
"""
main.py
-------
Project : Multilingual Ticket Translator — Batch Processor
Usage   : python main.py
"""

import os

from detector import detect_ticket_language
from translator import translate_to_english, translate_from_english
from glossary_handler import load_glossary, protect_terms, restore_terms
from storage import save_ticket_record


TICKETS_FOLDER = "tickets"

DEFAULT_REPLY = "Thank you for reaching out. We are working on your issue."

SUPPORTED_LANGUAGES = {"Telugu", "Hindi", "Tamil", "Kannada", "English"}

SAMPLE_TICKETS = {
    "ticket_001_telugu.txt":  "నా VPN కనెక్ట్ అవడం లేదు. Server కి access లేదు. దయచేసి సహాయం చేయండి.",
    "ticket_002_hindi.txt":   "मेरा Outlook नहीं खुल रहा है। Active Directory में भी login नहीं हो रहा।",
    "ticket_003_tamil.txt":   "என் Database connection தோல்வியடைகிறது. Server response கிடைக்கவில்லை.",
    "ticket_004_kannada.txt": "Firewall ನನ್ನ IP Address ಅನ್ನು block ಮಾಡಿದೆ. VPN ಮೂಲಕ connect ಆಗಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ.",
    "ticket_005_english.txt": "The Azure portal is showing a 403 error. I cannot access the Database or Server dashboard.",
}


def _create_sample_tickets(folder_path):
    os.makedirs(folder_path, exist_ok=True)
    for fname, content in SAMPLE_TICKETS.items():
        with open(os.path.join(folder_path, fname), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   Created sample: {folder_path}/{fname}")
    print()


def load_tickets_from_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"\n   '{folder_path}/' not found — creating sample tickets...\n")
        _create_sample_tickets(folder_path)

    txt_files = sorted(f for f in os.listdir(folder_path) if f.endswith(".txt"))

    if not txt_files:
        print(f"   No .txt files found in '{folder_path}/'. Exiting.")
        return []

    tickets = []
    for fname in txt_files:
        try:
            with open(os.path.join(folder_path, fname), "r", encoding="utf-8") as fh:
                content = fh.read().strip()
            if content:
                tickets.append({"filename": fname, "text": content})
            else:
                print(f"   Skipping empty file: {fname}")
        except OSError as exc:
            print(f"   Could not read {fname}: {exc}")

    return tickets


def process_ticket(ticket_text, filename):
    ticket_id = os.path.splitext(filename)[0].upper()

    # Step 1 — Detect language
    detection = detect_ticket_language(ticket_text)
    if detection.get("error"):
        raise RuntimeError(f"Language detection failed: {detection['error']}")

    language_name = detection.get("language_name", "")
    language_code = detection.get("language_code", "")

    if language_name not in SUPPORTED_LANGUAGES:
        raise RuntimeError(
            f"Unsupported language: '{language_name}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )

    # Step 2 — Load glossary
    glossary_terms = load_glossary()

    # Step 3 — Protect glossary terms in ticket
    protected_ticket, term_map = protect_terms(ticket_text, glossary_terms)

    # Step 4 — Translate ticket to English (skip if already English)
    if language_name == "English":
        english_ticket = ticket_text
    else:
        translation = translate_to_english(protected_ticket, source_language=language_name)
        if translation.get("error"):
            raise RuntimeError(f"Ticket translation failed: {translation['error']}")
        english_ticket = restore_terms(translation["translated_text"], term_map)

    # Step 5 — Show context to engineer
    print(f"\n  Original Ticket  : {ticket_text}")
    print(f"  English Ticket   : {english_ticket}")

    # Step 6 — Engineer reply
    try:
        engineer_reply = input("\n  Enter engineer reply (press Enter for default): ").strip()
    except (EOFError, KeyboardInterrupt):
        engineer_reply = ""

    if not engineer_reply:
        engineer_reply = DEFAULT_REPLY

    # Step 7 — Translate reply back (skip if original language is English)
    if language_name == "English":
        translated_reply = engineer_reply
    else:
        protected_reply, reply_term_map = protect_terms(engineer_reply, glossary_terms)
        reply_translation = translate_from_english(protected_reply, target_language=language_name)
        if reply_translation.get("error"):
            raise RuntimeError(f"Reply translation failed: {reply_translation['error']}")
        translated_reply = restore_terms(reply_translation["translated_text"], reply_term_map)

    # Step 8 — Save record
    saved = save_ticket_record(
        original_language=language_name,
        original_ticket=ticket_text,
        english_ticket=english_ticket,
        engineer_reply=engineer_reply,
        translated_reply=translated_reply,
        ticket_id=ticket_id,
    )

    return {
        "language_name":   language_name,
        "language_code":   language_code,
        "english_ticket":  english_ticket,
        "engineer_reply":  engineer_reply,
        "translated_reply": translated_reply,
        "saved_id":        saved["ticket_id"],
    }


def run_batch():
    print("\n" + "=" * 65)
    print("   Multilingual Ticket Translator  —  Batch Processor")
    print("=" * 65)

    tickets = load_tickets_from_folder(TICKETS_FOLDER)
    if not tickets:
        return

    total         = len(tickets)
    success_count = 0
    fail_count    = 0

    print(f"\n   {total} ticket(s) found in '{TICKETS_FOLDER}/'\n")

    for idx, ticket in enumerate(tickets, start=1):
        filename = ticket["filename"]
        text     = ticket["text"]

        print(f"\n{'─' * 65}")
        print(f"  Ticket {idx}/{total}  |  {filename}")
        print(f"{'─' * 65}")

        try:
            res = process_ticket(text, filename)

            print(f"\n  Detected Language : {res['language_name']} ({res['language_code']})")
            print(f"  Engineer Reply    : {res['engineer_reply']}")
            print(f"  Translated Reply  : {res['translated_reply']}")
            print(f"  Saved OK          : ID = {res['saved_id']}")

            success_count += 1

        except Exception as exc:
            print(f"\n  ERROR — '{filename}': {exc}")
            fail_count += 1

    print(f"\n{'=' * 65}")
    print(f"  Done  |  Success: {success_count}  |  Failed: {fail_count}  |  Total: {total}")
    print(f"  Output: output/tickets.csv")
    print(f"{'=' * 65}\n")


if __name__ == "__main__":
    run_batch()
