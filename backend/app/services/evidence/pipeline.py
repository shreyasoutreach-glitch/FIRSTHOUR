"""
Evidence compiler: hash -> validate -> extract -> normalize -> cross-verify.

The LLM's only job anywhere in this file is turning messy free text into
*candidate* structured claims (extract_candidate_claims). Everything after
that -- schema shape, normalization, and especially verification status --
is deterministic code that checks candidates against the authoritative
financial_events table. A claim is never marked VERIFIED because the LLM
sounded confident; it is VERIFIED only when it matches a real record.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import uuid

ALLOWED_MIME_PREFIXES = ("image/", "application/pdf", "text/")

AMOUNT_PATTERNS = [
    re.compile(r"(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(cr|crore|l|lakh|lakhs)?", re.IGNORECASE),
]

BENEFICIARY_PATTERNS = [
    re.compile(r"(?:send|transfer|pay|release)\s+(?:it\s+)?to\s+([A-Z][A-Za-z0-9 &\.]{2,40})", re.IGNORECASE),
]

INSTRUCTION_KEYWORDS = ("urgent", "immediately", "right now", "asap", "confidential", "don't call",
                         "do not call", "new vendor", "new account")

_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._ ()\[\],'&+-]")


def safe_filename(raw_filename: str | None, fallback: str = "upload") -> str:
    """Turn an untrusted client-supplied filename into something that can
    never control where a file gets written, while keeping it
    human-readable where possible.

    file.filename is attacker-controlled input -- it can contain "../",
    "..\\\\", an absolute path ("/etc/passwd", "C:\\\\Windows\\\\..."), null
    bytes, or nothing at all. This function is intentionally layered rather
    than a single string-replace, since any one trick (e.g. only handling
    "/") is bypassed by the others (e.g. "\\\\" on a system that treats it as
    a separator, or a literal ".." with no separator at all):

    1. Drop anything from a null byte onward (defends against null-byte
       tricks some filesystems/older libs mishandle).
    2. Normalize backslashes to forward slashes, so Windows-style traversal
       ("..\\\\..\\\\evil.txt") is caught by the same logic as POSIX-style.
    3. Take only the final path component (posixpath.basename), discarding
       every directory segment the client tried to smuggle in -- this alone
       neutralizes both "../" traversal and absolute paths.
    4. Strip any remaining characters outside a safe allow-list, and strip
       leading dots (so a component that was e.g. "..txt" can't collapse
       back into something traversal-like when concatenated elsewhere).
    5. Fall back to a fixed name if nothing safe survives.

    The caller (upload_evidence) still performs a final resolved-path
    containment check before writing -- this function makes that check
    nearly always redundant, not a replacement for it.
    """
    if not raw_filename:
        return fallback

    name = raw_filename.split("\x00", 1)[0]
    name = name.replace("\\", "/")

    import posixpath
    name = posixpath.basename(name)

    name = _UNSAFE_FILENAME_CHARS.sub("_", name)
    name = name.lstrip(".")
    name = name.strip().strip("_")

    if not name:
        return fallback

    return name[:150]


def is_path_contained(base_dir: str, candidate_path: str) -> bool:
    """True only if candidate_path resolves to a location inside base_dir.
    Uses realpath (resolves symlinks + ".."/"." components) on both sides so
    this is a check on where the file would *actually* land, not on the
    unresolved string."""
    base_resolved = os.path.realpath(base_dir)
    candidate_resolved = os.path.realpath(candidate_path)
    return candidate_resolved == base_resolved or candidate_resolved.startswith(base_resolved + os.sep)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_mime(mime_type: str) -> bool:
    return any(mime_type.startswith(p) for p in ALLOWED_MIME_PREFIXES)


def _parse_amount(raw: str, unit: str | None) -> float:
    value = float(raw.replace(",", ""))
    if unit:
        unit = unit.lower()
        if unit in ("cr", "crore"):
            value *= 1_00_00_000
        elif unit in ("l", "lakh", "lakhs"):
            value *= 1_00_000
    return value


def extract_candidate_claims(raw_text: str, source_artifact_id: str) -> list[dict]:
    """Uses the EvidenceProvider abstraction to extract candidate claims."""
    from app.services.evidence.provider import GeminiEvidenceProvider, DeterministicEvidenceProvider
    
    provider = None
    if os.environ.get("GEMINI_API_KEY") and os.environ.get("DEMO_MODE", "false").lower() != "true":
        try:
            provider = GeminiEvidenceProvider()
        except ValueError:
            provider = DeterministicEvidenceProvider()
    else:
        provider = DeterministicEvidenceProvider()
        
    try:
        return provider.extract(raw_text, source_artifact_id)
    except Exception as e:
        import logging
        logging.warning(f"Live LLM extraction failed: {e}. Falling back to deterministic.")
        fallback = DeterministicEvidenceProvider()
        return fallback.extract(raw_text, source_artifact_id)


def cross_reference_amount_claim(claim_amount: float, candidate_events: list[tuple[str, float]],
                                  tolerance: float = 0.01) -> tuple[str, str]:
    """Compare an extracted amount claim against real financial_events.
    Returns (verification_status, matched_event_id)."""
    for event_id, event_amount in candidate_events:
        if event_amount == 0:
            continue
        diff = abs(float(claim_amount) - float(event_amount)) / float(event_amount)
        if diff <= tolerance:
            return "VERIFIED", event_id
    if candidate_events:
        return "CONFLICTING", ""
    return "UNVERIFIED", ""
