
"""
translator.py
-------------
Module: Language Translation
Project: Multilingual Ticket Translator
Challenge: Infinite Computer Solutions AI Prototype Challenge

Purpose:
    Translates incoming support tickets to English for engineers,
    and translates engineer responses back to the customer's language.

Dependencies:
    - deep-translator (pip install deep-translator)

Author: Althi Sanjana 
"""

from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException, TranslationNotFound


# ---------------------------------------------------------------
# Language name → Google Translate language code mapping
# Used when the caller passes a full name like "Telugu"
# ---------------------------------------------------------------
LANGUAGE_NAME_TO_CODE = {
    "Telugu":  "te",
    "Hindi":   "hi",
    "Tamil":   "ta",
    "Kannada": "kn",
    "English": "en",
}


def translate_to_english(text: str, source_language: str = "auto") -> dict:
    """
    Translate a support ticket from any supported language into English.

    Parameters
    ----------
    text : str
        The raw ticket text to translate.
    source_language : str
        Full language name (e.g. "Telugu") or ISO code (e.g. "te").
        Defaults to "auto" — Google detects it automatically.

    Returns
    -------
    dict
        - "translated_text"   (str | None) : English translation
        - "source_language"   (str)        : Language code used as source
        - "target_language"   (str)        : Always "en"
        - "error"             (str | None) : Error message if translation failed
    """

    if not text or not text.strip():
        return {
            "translated_text": None,
            "source_language": source_language,
            "target_language": "en",
            "error": "Input text is empty or contains only whitespace.",
        }

    # Accept full names like "Telugu" or raw codes like "te"
    source_code = LANGUAGE_NAME_TO_CODE.get(source_language, source_language)

    try:
        translated = GoogleTranslator(source=source_code, target="en").translate(text.strip())

        return {
            "translated_text": translated,
            "source_language": source_code,
            "target_language": "en",
            "error": None,
        }

    except LanguageNotSupportedException:
        return {
            "translated_text": None,
            "source_language": source_code,
            "target_language": "en",
            "error": f"Language '{source_language}' is not supported by the translator.",
        }

    except TranslationNotFound:
        return {
            "translated_text": None,
            "source_language": source_code,
            "target_language": "en",
            "error": "Translation could not be found. The text may be too short or invalid.",
        }

    except Exception as e:
        return {
            "translated_text": None,
            "source_language": source_code,
            "target_language": "en",
            "error": f"Unexpected error during translation: {str(e)}",
        }


def translate_from_english(text: str, target_language: str) -> dict:
    """
    Translate an engineer's English response back to the customer's language.

    Parameters
    ----------
    text : str
        The English response text to translate.
    target_language : str
        Full language name (e.g. "Tamil") or ISO code (e.g. "ta").

    Returns
    -------
    dict
        - "translated_text"   (str | None) : Translation in target language
        - "source_language"   (str)        : Always "en"
        - "target_language"   (str)        : Target language code used
        - "error"             (str | None) : Error message if translation failed
    """

    if not text or not text.strip():
        return {
            "translated_text": None,
            "source_language": "en",
            "target_language": target_language,
            "error": "Input text is empty or contains only whitespace.",
        }

    if not target_language:
        return {
            "translated_text": None,
            "source_language": "en",
            "target_language": None,
            "error": "Target language was not provided.",
        }

    # Accept full names like "Kannada" or raw codes like "kn"
    target_code = LANGUAGE_NAME_TO_CODE.get(target_language, target_language)

    # No translation needed if target is already English
    if target_code == "en":
        return {
            "translated_text": text.strip(),
            "source_language": "en",
            "target_language": "en",
            "error": None,
        }

    try:
        translated = GoogleTranslator(source="en", target=target_code).translate(text.strip())

        return {
            "translated_text": translated,
            "source_language": "en",
            "target_language": target_code,
            "error": None,
        }

    except LanguageNotSupportedException:
        return {
            "translated_text": None,
            "source_language": "en",
            "target_language": target_code,
            "error": f"Language '{target_language}' is not supported by the translator.",
        }

    except TranslationNotFound:
        return {
            "translated_text": None,
            "source_language": "en",
            "target_language": target_code,
            "error": "Translation could not be found. The text may be too short or invalid.",
        }

    except Exception as e:
        return {
            "translated_text": None,
            "source_language": "en",
            "target_language": target_code,
            "error": f"Unexpected error during translation: {str(e)}",
        }


# ---------------------------------------------------------------
# Sample Usage  (run directly to test: python translator.py)
# ---------------------------------------------------------------
if __name__ == "__main__":

    # --- Test Cases: translate_to_english ---
    to_english_cases = [
        ("Telugu",  "నా ఆర్డర్ రాలేదు, దయచేసి సహాయం చేయండి"),
        ("Hindi",   "मेरा ऑर्डर अभी तक नहीं आया, कृपया मदद करें"),
        ("Tamil",   "என் ஆர்டர் வரவில்லை, தயவுசெய்து உதவுங்கள்"),
        ("Kannada", "ನನ್ನ ಆರ್ಡರ್ ಬಂದಿಲ್ಲ, ದಯವಿಟ್ಟು ಸಹಾಯ ಮಾಡಿ"),
        ("English", "My order has not arrived yet, please help"),
        ("auto",    "मुझे लॉगिन करने में समस्या हो रही है"),  # auto-detect
        ("Telugu",  ""),                                         # empty input
    ]

    # --- Test Cases: translate_from_english ---
    from_english_cases = [
        ("Telugu",  "Your order will be delivered within 2 business days."),
        ("Hindi",   "We have resolved your issue. Please try again."),
        ("Tamil",   "Your account has been successfully updated."),
        ("Kannada", "Please contact us if the problem persists."),
        ("English", "This should return as-is since it's already English."),
        ("French",  "This language is not in our supported list."),  # unsupported
    ]

    print("=" * 60)
    print("  Multilingual Ticket Translator — Translation Module")
    print("=" * 60)

    # -- Section 1: To English --
    print("\n📥  Translating Tickets → English\n")
    for lang, ticket in to_english_cases:
        result = translate_to_english(ticket, source_language=lang)
        print(f"  Source     : {lang}")
        print(f"  Original   : {ticket if ticket else '(empty)'}")
        if result["error"]:
            print(f"  ❌ Error   : {result['error']}")
        else:
            print(f"  ✅ English : {result['translated_text']}")
        print()

    # -- Section 2: From English --
    print("=" * 60)
    print("\n📤  Translating Engineer Response → Customer Language\n")
    for lang, response in from_english_cases:
        result = translate_from_english(response, target_language=lang)
        print(f"  Target     : {lang}")
        print(f"  English    : {response}")
        if result["error"]:
            print(f"  ❌ Error   : {result['error']}")
        else:
            print(f"  ✅ Translated : {result['translated_text']}")
        print()

    print("=" * 60)
