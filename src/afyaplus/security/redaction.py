"""PII redaction helpers (Week 9 reuse).

Patterns target the synthetic teaching notes the demo sends around:
emails, Kenyan and international phone numbers, card numbers, ISO
dates of birth and national-ID style digit runs. Redaction happens
before any note is echoed back or logged.
"""

from __future__ import annotations

import re
from typing import Any

# Order matters: wider/more specific patterns run first so digit runs
# are not double-masked.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("CARD", re.compile(r"\b\d{4}(?:[ -]?\d{4}){3}\b")),
    ("PHONE", re.compile(r"(?:\+254|254|0)(?:7|1)\d{8}(?!\d)")),
    ("PHONE_INTL", re.compile(r"\+\d{9,15}(?!\d)")),
    ("DOB", re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),
    ("ID", re.compile(r"\b\d{7,9}\b")),
]

PLACEHOLDERS: dict[str, str] = {
    "EMAIL": "[EMAIL]",
    "CARD": "[CARD]",
    "PHONE": "[PHONE]",
    "PHONE_INTL": "[PHONE]",
    "DOB": "[DOB]",
    "ID": "[ID]",
}


def redact(text: str) -> str:
    """Replace every recognised PII pattern with a labelled placeholder."""
    if not text:
        return ""
    result = str(text)
    for name, pattern in _PATTERNS:
        result = pattern.sub(PLACEHOLDERS[name], result)
    return result


def contains_pii(text: str) -> bool:
    """True when any PII pattern is still present."""
    if not text:
        return False
    return any(pattern.search(str(text)) for _name, pattern in _PATTERNS)


def redact_value(value: Any) -> Any:
    """Recursively redact strings inside dicts / lists / tuples."""
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, dict):
        return {key: redact_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(redact_value(item) for item in value)
    return value
