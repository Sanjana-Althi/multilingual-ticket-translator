import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from detector import detect_ticket_language


def test_language_detection():
    result = detect_ticket_language("My order has not arrived")

    assert result["language_name"] == "English"
    assert result["is_supported"] is True
    assert result["error"] is None