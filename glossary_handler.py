"""
glossary_handler.py
--------------------
Module: Glossary Protection
Project: Multilingual Ticket Translator
Challenge: Infinite Computer Solutions AI Prototype Challenge

Purpose:
    Certain IT terms (VPN, Azure, Outlook, etc.) must never be translated —
    they are proper nouns or product names that must stay in their original form.

    This module:
        1. Reads those protected terms from glossary.json
        2. Replaces them with safe placeholders BEFORE translation
        3. Restores the original terms AFTER translation

    This way, the translator never sees or touches protected terms.

How the placeholder trick works:
    "My VPN is not working"
        → protect   → "My ##TERM_0## is not working"
        → translate → "मेरा ##TERM_0## काम नहीं कर रहा"    ← translator ignores placeholder
        → restore   → "मेरा VPN काम नहीं कर रहा"           ← original term back in place

Dependencies:
    - None (uses only Python standard library)

Author: Althi Sanjana
"""

import json
import os
import re


# ---------------------------------------------------------------
# Path to the glossary file (same directory as this module)
# ---------------------------------------------------------------
GLOSSARY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glossary.json")

# Placeholder format — must be unique enough to survive translation untouched
# Google Translate leaves ALL-CAPS alphanumeric tokens with ## markers intact
PLACEHOLDER_TEMPLATE = "##TERM_{}##"


def load_glossary(filepath: str = GLOSSARY_FILE) -> list:
    """
    Load protected terms from glossary.json.

    Returns a list of term strings sorted by length (longest first).
    Sorting longest-first ensures multi-word terms like "Active Directory"
    are matched before single words like "Active".

    Parameters
    ----------
    filepath : str
        Path to the glossary JSON file.

    Returns
    -------
    list[str]
        Sorted list of protected terms.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"glossary.json not found at: {filepath}\n"
            "Please ensure glossary.json is in the same folder as this module."
        )

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    terms = data.get("terms", [])

    if not terms:
        raise ValueError("glossary.json exists but contains no terms under the 'terms' key.")

    # Sort longest first so multi-word terms are matched before partial words
    return sorted(terms, key=len, reverse=True)


def protect_terms(text: str, glossary_terms: list) -> tuple:
    """
    Replace all glossary terms in the text with numbered placeholders.

    Matching is case-insensitive but the ORIGINAL casing is preserved
    in the restoration map so it comes back exactly as it was.

    Parameters
    ----------
    text : str
        Original ticket or response text.
    glossary_terms : list[str]
        List of terms to protect (from load_glossary).

    Returns
    -------
    tuple: (protected_text, term_map)
        - protected_text (str)  : Text with terms replaced by placeholders
        - term_map (dict)       : Maps each placeholder → original term
                                  e.g. {"##TERM_0##": "VPN", "##TERM_1##": "Azure"}
    """
    term_map = {}
    protected_text = text
    counter = 0

    for term in glossary_terms:
        # re.escape handles terms with special chars (e.g. "IP Address")
        # re.IGNORECASE so "vpn", "VPN", "Vpn" all match
        pattern = re.compile(re.escape(term), re.IGNORECASE)

        if pattern.search(protected_text):
            placeholder = PLACEHOLDER_TEMPLATE.format(counter)

            # Store the ORIGINAL matched text (preserves user's casing)
            match = pattern.search(protected_text)
            term_map[placeholder] = match.group(0)

            # Replace all occurrences with the placeholder
            protected_text = pattern.sub(placeholder, protected_text)
            counter += 1

    return protected_text, term_map


def restore_terms(translated_text: str, term_map: dict) -> str:
    """
    Restore original glossary terms by replacing placeholders back.

    Parameters
    ----------
    translated_text : str
        Text returned by the translator (may contain placeholders).
    term_map : dict
        The map returned by protect_terms, e.g. {"##TERM_0##": "VPN"}.

    Returns
    -------
    str
        Final text with all placeholders replaced by original terms.
    """
    restored_text = translated_text

    for placeholder, original_term in term_map.items():
        # Some translators add spaces around placeholders; strip just in case
        restored_text = restored_text.replace(placeholder, original_term)

    return restored_text


# ---------------------------------------------------------------
# Convenience wrapper — protect → (your translation here) → restore
# ---------------------------------------------------------------
def prepare_for_translation(text: str) -> tuple:
    """
    One-step helper: load glossary and protect terms in a single call.

    Use this when you want to quickly protect text before passing it
    to translator.py. Returns everything you need to restore later.

    Parameters
    ----------
    text : str
        Raw ticket text.

    Returns
    -------
    tuple: (protected_text, term_map, glossary_terms)
        Pass protected_text to the translator.
        Pass term_map to restore_terms() after translation.
    """
    glossary_terms = load_glossary()
    protected_text, term_map = protect_terms(text, glossary_terms)
    return protected_text, term_map, glossary_terms


# ---------------------------------------------------------------
# Sample Usage  (run directly to test: python glossary_handler.py)
# ---------------------------------------------------------------
if __name__ == "__main__":

    test_cases = [
        # (label, ticket_text)
        (
            "VPN + Azure",
            "I cannot connect to VPN and my Azure portal is showing an error."
        ),
        (
            "Active Directory (multi-word term)",
            "The user cannot log in because Active Directory is not syncing."
        ),
        (
            "Outlook + Ticket ID",
            "Ticket ID 10234: Outlook is not receiving emails since morning."
        ),
        (
            "Mixed case — 'vpn' and 'OUTLOOK'",
            "My vpn disconnects every hour and OUTLOOK crashes after that."
        ),
        (
            "Multiple terms in one ticket",
            "Server is down, Database backup failed, and the Firewall blocked the IP Address."
        ),
        (
            "No glossary terms present",
            "The screen goes black when I open the application."
        ),
    ]

    print("=" * 62)
    print("  Multilingual Ticket Translator — Glossary Handler")
    print("=" * 62)

    # Load glossary once (reuse across all test cases)
    try:
        glossary = load_glossary()
        print(f"\n✅ Loaded {len(glossary)} terms from glossary.json")
        print(f"   Terms: {', '.join(glossary[:6])} ... (+{len(glossary)-6} more)\n")
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Failed to load glossary: {e}")
        exit(1)

    for label, ticket in test_cases:
        print(f"─── Test: {label} {'─' * max(1, 48 - len(label))}")
        print(f"  Original   : {ticket}")

        # Step 1: Protect
        protected, term_map = protect_terms(ticket, glossary)
        print(f"  Protected  : {protected}")
        print(f"  Term map   : {term_map if term_map else '(no terms found)'}")

        # Step 2: Simulate translation (we just uppercase as a stand-in for the translator)
        # In real usage, you pass `protected` to translate_to_english() from translator.py
        simulated_translation = protected.upper()

        # Step 3: Restore
        restored = restore_terms(simulated_translation, term_map)
        print(f"  Restored   : {restored}")
        print()

    print("=" * 62)
    print("  Full pipeline example (how translator.py should call this)")
    print("=" * 62)
    sample = "My VPN is not connecting and the Server is down."
    protected, term_map, _ = prepare_for_translation(sample)
    print(f"\n  Raw ticket        : {sample}")
    print(f"  Pass to translator: {protected}")
    print(f"  After translation : (translator output with placeholders intact)")
    print(f"  Call restore_terms() with term_map to get the final text back.\n")
