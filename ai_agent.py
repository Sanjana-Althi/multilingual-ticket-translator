"""
ai_agent.py
-----------
Module  : AI Agent (OpenRouter Edition)
Project : Multilingual Ticket Translator
Purpose : Pre-processes support tickets using Google Gemini 2.5 Flash
          via OpenRouter before they enter the deep-translator pipeline.

Drop-in replacement for the previous Gemini SDK version.
Public interface is identical — app.py requires zero changes.

Usage:
    from ai_agent import TicketAgent
    agent  = TicketAgent()
    result = agent.process(ticket_text)
"""

import os
import json
import requests
from typing import Optional


class TicketAgent:
    """
    Sends a support ticket to Gemini 2.5 Flash via OpenRouter and returns
    a structured analysis: improved text, summary, category, and priority.

    Behaviour guarantees:
    - Never raises an exception to the caller.
    - On any failure, returns the original ticket unchanged so the
      existing translation pipeline continues without interruption.
    - API key is read from the OPENROUTER_API_KEY environment variable.
    """

    # ── Configuration ──────────────────────────────────────────────────────────
    API_ENDPOINT   = "https://openrouter.ai/api/v1/chat/completions"
    MODEL          =  "nex-agi/nex-n2-pro:free"
    REQUEST_TIMEOUT = 20          # seconds before giving up on the API call

    VALID_PRIORITIES = {"Low", "Medium", "High"}
    VALID_CATEGORIES = {
        "Network", "VPN", "Hardware", "Software", "Email",
        "Access", "Database", "Server", "Security", "General",
    }
    DEFAULT_CATEGORY = "General"
    DEFAULT_PRIORITY = "Medium"

    # ── Initialisation ─────────────────────────────────────────────────────────
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialise the agent.

        Parameters
        ----------
        api_key : str, optional
            OpenRouter API key. If omitted, the OPENROUTER_API_KEY
            environment variable is used automatically.
        """
        self._api_key: str = api_key or os.environ.get("OPENROUTER_API_KEY", "")

        if not self._api_key:
            print(
                "[TicketAgent] WARNING: OPENROUTER_API_KEY is not set. "
                "All process() calls will return the fallback result until "
                "a valid key is provided."
            )

    # ── Public interface ───────────────────────────────────────────────────────
    def process(self, ticket_text: str) -> dict:
        """
        Analyse and improve a support ticket using the AI model.

        Parameters
        ----------
        ticket_text : str
            Raw support ticket text in any language.

        Returns
        -------
        dict
            {
                "improved_ticket": str,   # Clarified version of the ticket
                "summary":         str,   # One-line summary (max ~15 words)
                "category":        str,   # e.g. "Network", "VPN", "Software"
                "priority":        str,   # "Low", "Medium", or "High"
                "error":           str | None   # None on success
            }
        """
        # Guard: empty input — skip the API call entirely
        if not ticket_text or not ticket_text.strip():
            return self._fallback(ticket_text, error="Empty ticket text provided.")

        # Guard: no API key — skip the API call entirely
        if not self._api_key:
            return self._fallback(
                ticket_text,
                error="No OpenRouter API key found. Set OPENROUTER_API_KEY.",
            )

        try:
            raw_response = self._call_api(ticket_text.strip())
            return self._parse_response(raw_response, original=ticket_text)

        except requests.exceptions.Timeout:
            return self._fallback(ticket_text, error="OpenRouter request timed out.")

        except requests.exceptions.ConnectionError:
            return self._fallback(ticket_text, error="Network error — could not reach OpenRouter.")

        except Exception as exc:
            return self._fallback(ticket_text, error=f"Unexpected error: {str(exc)}")

    # ── Private: API call ──────────────────────────────────────────────────────
    def _call_api(self, ticket_text: str) -> str:
        """
        Send the ticket to OpenRouter and return the raw model text.

        Raises
        ------
        requests.HTTPError
            When the API returns a non-2xx status code.
        requests.Timeout
            When the request exceeds REQUEST_TIMEOUT seconds.
        """
        
        headers = {
    "Authorization": f"Bearer {self._api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Multilingual Ticket Translator"
}

        payload = {
            "model": self.MODEL,
            "messages": [
                {
                    "role":    "system",
                    "content": self._system_prompt(),
                },
                {
                    "role":    "user",
                    "content": ticket_text,
                },
            ],
            # Ask the model to return JSON directly where supported
            
        }

        response = requests.post(
            self.API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=self.REQUEST_TIMEOUT,
        )

        # Surface HTTP errors clearly (e.g. 401 Unauthorized, 429 Rate Limited)
        response.raise_for_status()

        data = response.json()

        # Extract text from the standard OpenAI-compatible response structure
        return data["choices"][0]["message"]["content"]

    # ── Private: prompt ────────────────────────────────────────────────────────
    @staticmethod
    def _system_prompt() -> str:
        """
        Return the system prompt sent to the model.

        The prompt is kept as a static method so it can be read,
        tested, and updated independently of the rest of the class.
        """
        return (
            "You are a professional IT support assistant.\n\n"
            "A support ticket will be provided to you. Perform these tasks:\n\n"
            "1. IMPROVE the ticket text:\n"
            "   - Fix grammar and clarity.\n"
            "   - Do NOT change the meaning.\n"
            "   - Keep the ticket in the SAME language as the original.\n"
            "   - Do NOT translate it into another language.\n\n"
            "2. Write a SHORT summary (maximum 15 words).\n"
            "   - CRITICAL: The summary MUST ALWAYS be written in English,\n"
            "     regardless of the input language. Even if the ticket is in\n"
            "     Telugu, Tamil, Hindi, Malayalam, Kannada, or any other language,\n"
            "     the summary field must contain English text only.\n\n"
            "3. Choose one CATEGORY from this list only:\n"
            "   Network, VPN, Hardware, Software, Email, "
            "Access, Database, Server, Security, General\n\n"
            "4. Choose one PRIORITY:\n"
            "   - High   : System down, cannot work at all, data loss, security breach\n"
            "   - Medium : Feature broken but workaround exists, intermittent issue\n"
            "   - Low    : Minor inconvenience, general question, how-to request\n\n"
            "STRICT OUTPUT RULES:\n"
            "- Return ONLY a valid JSON object. Nothing else.\n"
            "- No markdown fences (no ```json or ```).\n"
            "- No explanation, preamble, or commentary before or after the JSON.\n"
            "- No extra keys beyond the four required.\n\n"
            "Required format (exactly):\n"
            '{\n'
            '  "improved_ticket": "...",\n'
            '  "summary": "...",\n'
            '  "category": "...",\n'
            '  "priority": "..."\n'
            '}'
        )

    # ── Private: response parsing ──────────────────────────────────────────────
    def _parse_response(self, raw_text: str, original: str) -> dict:
        """
        Convert the model's raw text into a validated result dict.

        Handles edge cases:
        - Model wraps JSON in ```json ... ``` fences despite instructions
        - Model returns extra commentary before or after the JSON block
        - Individual fields are missing or contain unexpected values
        """
        cleaned = self._strip_fences(raw_text)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Attempt to extract a JSON object from somewhere in the text
            extracted = self._extract_json_block(raw_text)
            if extracted is None:
                return self._fallback(
                    original,
                    error=f"Could not parse model response as JSON. Raw: {raw_text[:300]}",
                )
            data = extracted

        # Sanitise each field individually so a single bad value does not
        # discard the entire result
        improved = str(data.get("improved_ticket", "")).strip() or original
        summary  = str(data.get("summary",         "")).strip() or "No summary available."
        category = str(data.get("category",        "")).strip()
        priority = str(data.get("priority",        "")).strip()

        # Enforce allowed values — unknown values fall back to safe defaults
        if category not in self.VALID_CATEGORIES:
            category = self.DEFAULT_CATEGORY
        if priority not in self.VALID_PRIORITIES:
            priority = self.DEFAULT_PRIORITY

        return {
            "improved_ticket": improved,
            "summary":         summary,
            "category":        category,
            "priority":        priority,
            "error":           None,
        }

    # ── Private: text utilities ────────────────────────────────────────────────
    @staticmethod
    def _strip_fences(text: str) -> str:
        """
        Remove markdown code fences if the model included them.

        Handles:
            ```json
            { ... }
            ```
        and:
            ```
            { ... }
            ```
        """
        stripped = text.strip()
        if not stripped.startswith("```"):
            return stripped

        lines = stripped.splitlines()
        # Drop the opening fence line (```json or ```) and closing fence line
        inner_lines = []
        for line in lines[1:]:
            if line.strip() == "```":
                break
            inner_lines.append(line)

        return "\n".join(inner_lines).strip()

    @staticmethod
    def _extract_json_block(text: str) -> Optional[dict]:
        """
        Last-resort extraction: find the first { ... } block in the text
        and attempt to parse it as JSON.

        Returns None if no valid JSON object is found.
        """
        start = text.find("{")
        end   = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None

    # ── Private: fallback ──────────────────────────────────────────────────────
    @staticmethod
    def _fallback(original_text: str, error: str = None) -> dict:
        """
        Return a safe result when the agent cannot process the ticket.

        The improved_ticket is always set to the original text so the
        caller (run_detection_and_translation) continues unchanged.
        """
        return {
            "improved_ticket": original_text or "",
            "summary":         "AI Agent unavailable — original ticket used.",
            "category":        "General",
            "priority":        "Medium",
            "error":           error,
        }


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    """
    Run this file directly to verify your OpenRouter key works:

        python ai_agent.py

    Expected output: improved_ticket, summary, category, priority printed.
    If you see an error message, check your OPENROUTER_API_KEY.
    """

    test_tickets = [
        # English — deliberate grammar mistakes
        (
            "English",
            "my outlook is not open since morning. "
            "i tried restarting but it still not work. please help fast.",
        ),
        # Telugu — should stay in Telugu after improvement
        (
            "Telugu",
            "నా VPN కనెక్ట్ అవడం లేదు. Server కి access లేదు. దయచేసి సహాయం చేయండి.",
        ),
        # Edge case: empty string
        (
            "Empty",
            "",
        ),
    ]

    print("=" * 60)
    print("  TicketAgent — OpenRouter Integration Test")
    print(f"  Model : {TicketAgent.MODEL}")
    print("=" * 60)

    agent = TicketAgent()  # reads OPENROUTER_API_KEY from environment

    for label, ticket in test_tickets:
        print(f"\n[{label}]")
        print(f"  Input    : {ticket[:80]}{'...' if len(ticket) > 80 else ''}")

        result = agent.process(ticket)

        print(f"  Improved : {result['improved_ticket'][:80]}")
        print(f"  Summary  : {result['summary']}")
        print(f"  Category : {result['category']}")
        print(f"  Priority : {result['priority']}")
        if result["error"]:
            print(f"  Error    : {result['error']}")

    print("\n" + "=" * 60)
