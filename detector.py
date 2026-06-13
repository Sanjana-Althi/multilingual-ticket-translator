"""
detector.py
-----------
Module: Language Detection
Project: Multilingual Ticket Translator
Challenge: Infinite Computer Solutions AI Prototype Challenge

Purpose:
    Detects the language of an incoming support ticket and returns
    the full language name instead of a language code.

Dependencies:
    - langdetect (pip install langdetect)

Author: Althi Sanjana
"""

from langdetect import detect, LangDetectException


# ---------------------------------------------------------------
# Language code → Full name mapping
# Covers the 5 required languages + a generic fallback
# ---------------------------------------------------------------
LANGUAGE_CODE_MAP = {
    "te": "Telugu",
    "hi": "Hindi",
    "ta": "Tamil",
    "kn": "Kannada",
    "en": "English",
}


def detect_ticket_language(text: str) -> dict:
    """
    Detect the language of a support ticket.

    Parameters
    ----------
    text : str
        The raw text content of the support ticket.

    Returns
    -------
    dict
        A result dictionary with the following keys:
            - "language_code"  (str)  : ISO 639-1 code, e.g. "hi"
            - "language_name"  (str)  : Full name, e.g. "Hindi"
            - "is_supported"   (bool) : True if it's one of the 5 target languages
            - "error"          (str | None) : Error message if detection failed

    Example
    -------
    >>> result = detect_ticket_language("నా ఆర్డర్ రాలేదు")
    >>> print(result)
    {'language_code': 'te', 'language_name': 'Telugu', 'is_supported': True, 'error': None}
    """

    # Guard: reject empty or whitespace-only input early
    if not text or not text.strip():
        return {
            "language_code": None,
            "language_name": None,
            "is_supported": False,
            "error": "Input text is empty or contains only whitespace.",
        }

    try:
        # langdetect returns an ISO 639-1 code like "hi", "te", "en"
        detected_code = detect(text.strip())

        # Map code to a full name; use a readable fallback if not in our map
        language_name = LANGUAGE_CODE_MAP.get(
            detected_code,
            f"Unsupported Language (code: {detected_code})"
        )

        is_supported = detected_code in LANGUAGE_CODE_MAP

        return {
            "language_code": detected_code,
            "language_name": language_name,
            "is_supported": is_supported,
            "error": None,
        }

    except LangDetectException as e:
        # langdetect raises this when it cannot determine the language
        # (e.g., text is too short, contains only numbers/symbols)
        return {
            "language_code": None,
            "language_name": None,
            "is_supported": False,
            "error": f"Language detection failed: {str(e)}",
        }

    except Exception as e:
        # Catch-all for any unexpected errors (e.g., encoding issues)
        return {
            "language_code": None,
            "language_name": None,
            "is_supported": False,
            "error": f"Unexpected error during detection: {str(e)}",
        }


# ---------------------------------------------------------------
# Sample Usage  (run this file directly to test: python detector.py)
# ---------------------------------------------------------------
if __name__ == "__main__":

    sample_tickets = [
        # (label, text)
        ("Telugu",  "నా ఆర్డర్ రాలేదు, దయచేసి సహాయం చేయండి"),
        ("Hindi",   "मेरा ऑर्डर अभी तक नहीं आया, कृपया मदद करें"),
        ("Tamil",   "என் ஆர்டர் வரவில்லை, தயவுசெய்து உதவுங்கள்"),
        ("Kannada", "ನನ್ನ ಆರ್ಡರ್ ಬಂದಿಲ್ಲ, ದಯವಿಟ್ಟು ಸಹಾಯ ಮಾಡಿ"),
        ("English", "My order has not arrived yet, please help me"),
        ("Empty",   ""),
        ("Short/Ambiguous", "123"),
    ]

    print("=" * 55)
    print("  Multilingual Ticket Translator — Language Detector")
    print("=" * 55)

    for label, ticket_text in sample_tickets:
        result = detect_ticket_language(ticket_text)

        print(f"\n[Test: {label}]")
        if result["error"]:
            print(f"  ❌ Error       : {result['error']}")
        else:
            print(f"  ✅ Detected    : {result['language_name']} ({result['language_code']})")
            print(f"  Supported      : {result['is_supported']}")

    print("\n" + "=" * 55)
