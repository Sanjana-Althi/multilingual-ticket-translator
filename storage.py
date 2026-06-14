"""
storage.py
----------
Module: Ticket Storage
Project: Multilingual Ticket Translator
Challenge: Infinite Computer Solutions AI Prototype Challenge

Purpose:
    Persists every processed support ticket as a row in a CSV file.
    Each row captures the full lifecycle of a ticket:
        - What the customer sent (original language + text)
        - What the engineer saw (English translation)
        - What the engineer replied (English)
        - What the customer received (reply translated back)

    Records are APPENDED — existing data is never overwritten.
    The output folder is created automatically if it doesn't exist.

Output:
    output/tickets.csv

Dependencies:
    - None (uses only Python standard library: csv, os, uuid, datetime)

Author: Althi Sanjana
"""

import csv
import os
import uuid
from datetime import datetime


# ---------------------------------------------------------------
# Configuration — change these if you need a different location
# ---------------------------------------------------------------
OUTPUT_DIR  = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tickets.csv")

CSV_COLUMNS = [
    "ticket_id",
    "timestamp",
    "original_language",
    "original_ticket",
    "english_ticket",
    "engineer_reply",
    "translated_reply",
]


def _ensure_output_dir() -> None:
    """Create the output directory if it does not already exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _ensure_csv_header() -> None:
    """
    Write the CSV header row if the file is new or empty.
    Called automatically before every write — safe to call multiple times.
    """
    file_exists    = os.path.exists(OUTPUT_FILE)
    file_non_empty = file_exists and os.path.getsize(OUTPUT_FILE) > 0

    if not file_non_empty:
        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()


def save_ticket_record(
    original_language: str,
    original_ticket: str,
    english_ticket: str,
    engineer_reply: str,
    translated_reply: str,
    ticket_id: str = None,
) -> dict:

    # --- validation ---
    required = {
        "original_language": original_language,
        "original_ticket": original_ticket,
        "english_ticket": english_ticket,
        "engineer_reply": engineer_reply,
        "translated_reply": translated_reply,
    }

    for field_name, value in required.items():
        if not value or not str(value).strip():
            raise ValueError(f"Required field '{field_name}' is empty or missing.")

    # --- build record ---
    record = {
        "ticket_id": ticket_id if ticket_id else str(uuid.uuid4())[:8].upper(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "original_language": original_language.strip(),
        "original_ticket": original_ticket.strip(),
        "english_ticket": english_ticket.strip(),
        "engineer_reply": engineer_reply.strip(),
        "translated_reply": translated_reply.strip(),
    }

    try:
        _ensure_output_dir()
        _ensure_csv_header()

        with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writerow(record)

    except OSError as e:
        raise OSError(f"Could not write to {OUTPUT_FILE}: {str(e)}")

    return record
    
"""
    Save one fully-processed ticket as a row in output/tickets.csv.

    Parameters
    ----------
    original_language : str
        Language the ticket arrived in, e.g. "Telugu".
    original_ticket : str
        Raw ticket text as submitted by the customer.
    english_ticket : str
        English translation of the ticket shown to the engineer.
    engineer_reply : str
        Engineer's response written in English.
    translated_reply : str
        Engineer's reply translated back to the customer's language.
    ticket_id : str, optional
        Provide your own ID (e.g. from a ticketing system).
        If omitted, a unique UUID is generated automatically.

    Returns
    -------
    dict
        The complete record that was saved, including generated ticket_id
        and timestamp. Useful for confirming what was written.

    Raises
    ------
    ValueError
        If any required field is empty or None.
    OSError
        If the file cannot be written due to a permissions issue.
    """

    # Open in APPEND mode — existing rows are never touched
with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)


def read_all_tickets() -> list:
    """
    Read and return all saved ticket records from the CSV.

    Returns
    -------
    list[dict]
        Each dict represents one ticket row.
        Returns an empty list if the file doesn't exist yet.
    """
    if not os.path.exists(OUTPUT_FILE):
        return []

    with open(OUTPUT_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ---------------------------------------------------------------
# Sample Usage  (run directly to test: python storage.py)
# ---------------------------------------------------------------
if __name__ == "__main__":

    test_tickets = [
        {
            "original_language": "Telugu",
            "original_ticket":   "నా VPN కనెక్ట్ అవడం లేదు, దయచేసి సహాయం చేయండి.",
            "english_ticket":    "My VPN is not connecting, please help.",
            "engineer_reply":    "Please restart your VPN client and try again.",
            "translated_reply":  "దయచేసి మీ VPN క్లయింట్‌ను పునఃప్రారంభించి మళ్ళీ ప్రయత్నించండి.",
        },
        {
            "original_language": "Hindi",
            "original_ticket":   "मेरा Outlook खुल नहीं रहा है।",
            "english_ticket":    "My Outlook is not opening.",
            "engineer_reply":    "Please clear the Outlook cache and restart the application.",
            "translated_reply":  "कृपया Outlook कैश साफ़ करें और एप्लिकेशन को पुनः आरंभ करें।",
        },
        {
            "original_language": "Tamil",
            "original_ticket":   "Server இணைப்பு தோல்வியடைகிறது.",
            "english_ticket":    "Server connection is failing.",
            "engineer_reply":    "The Server issue has been escalated to the infrastructure team.",
            "translated_reply":  "Server சிக்கல் உள்கட்டமைப்பு குழுவிடம் அனுப்பப்பட்டது.",
            "ticket_id":         "TKT-9901",   # custom ID example
        },
        {
            "original_language": "Kannada",
            "original_ticket":   "Database ಸಂಪರ್ಕ ವಿಫಲವಾಗಿದೆ.",
            "english_ticket":    "Database connection has failed.",
            "engineer_reply":    "The Database server will be restored within 30 minutes.",
            "translated_reply":  "Database ಸರ್ವರ್ 30 ನಿಮಿಷಗಳಲ್ಲಿ ಮರುಸ್ಥಾಪಿಸಲಾಗುವುದು.",
        },
    ]

    print("=" * 62)
    print("  Multilingual Ticket Translator — Storage Module")
    print("=" * 62)

    # --- Save all test tickets ---
    print(f"\n📝  Saving {len(test_tickets)} ticket(s) to {OUTPUT_FILE}\n")

    for ticket in test_tickets:
        try:
            saved = save_ticket_record(**ticket)
            print(f"  ✅ Saved   | ID: {saved['ticket_id']} | "
                  f"Lang: {saved['original_language']} | "
                  f"Time: {saved['timestamp']}")
        except (ValueError, OSError) as e:
            print(f"  ❌ Failed  | {e}")

    # --- Test validation: missing field ---
    print("\n  Testing validation (empty field)...")
    try:
        save_ticket_record(
            original_language="Hindi",
            original_ticket="",          # intentionally empty
            english_ticket="Test",
            engineer_reply="Test reply",
            translated_reply="परीक्षण उत्तर",
        )
    except ValueError as e:
        print(f"  ✅ Caught expected error: {e}")

    # --- Read back and display all records ---
    print(f"\n📂  Reading all records from {OUTPUT_FILE}\n")
    all_records = read_all_tickets()

    if not all_records:
        print("  No records found.")
    else:
        for rec in all_records:
            print(f"  [{rec['ticket_id']}] {rec['original_language']:10} | "
                  f"{rec['original_ticket'][:45]}...")

    print(f"\n  Total records in file: {len(all_records)}")
    print("\n" + "=" * 62)
