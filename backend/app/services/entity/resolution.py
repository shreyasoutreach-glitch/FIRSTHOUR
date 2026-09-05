"""
Deterministic entity resolution. Strong identifiers are matched first and
decide the outcome by themselves; weaker similarity signals only ever
*support* a decision that a strong identifier already leans toward -- they
never merge two entities on their own. This is the "never merge solely
because names look similar" rule from the architecture doc, enforced in
code rather than left as a guideline for the LLM to (maybe) follow.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

SIGNAL_WEIGHTS = {
    "exact_transaction_id": 1.00,
    "exact_fund_account_id": 0.95,
    "exact_upi_id": 0.90,
    "exact_phone": 0.85,
    "normalized_name": 0.70,
    "address_similarity": 0.40,
    "temporal_consistency": 0.30,
}

AUTO_LINK_THRESHOLD = 0.90
REVIEW_THRESHOLD = 0.70


@dataclass
class ResolutionResult:
    signal: str
    weight: float
    decision: str  # AUTO_LINK / REVIEW / KEEP_SEPARATE


def normalize_phone(phone: str) -> str:
    """Digits only, then keep the last 10 -- strips punctuation, spaces and a
    leading country code (e.g. India's +91) so "+91 98765-43210" and
    "9876543210" compare equal."""
    digits = re.sub(r"\D", "", phone)
    return digits[-10:] if len(digits) >= 10 else digits


def normalize_name(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\b(pvt|ltd|private|limited|inc|llp|the)\b", "", name)
    return re.sub(r"\s+", " ", name).strip()


def decide(weight: float) -> str:
    if weight >= AUTO_LINK_THRESHOLD:
        return "AUTO_LINK"
    if weight >= REVIEW_THRESHOLD:
        return "REVIEW"
    return "KEEP_SEPARATE"


def resolve(
    *,
    candidate_transaction_id: str | None = None,
    known_transaction_id: str | None = None,
    candidate_fund_account_id: str | None = None,
    known_fund_account_id: str | None = None,
    candidate_upi_id: str | None = None,
    known_upi_id: str | None = None,
    candidate_phone: str | None = None,
    known_phone: str | None = None,
    candidate_name: str | None = None,
    known_name: str | None = None,
) -> ResolutionResult:
    """Evaluate signals strongest-first and stop at the first one that fires.
    Weaker signals are only reached when every stronger identifier is either
    absent or a non-match -- they can raise a match into REVIEW but can never
    reach AUTO_LINK on their own, matching the architecture's decision bands.
    """
    if candidate_transaction_id and known_transaction_id and candidate_transaction_id == known_transaction_id:
        w = SIGNAL_WEIGHTS["exact_transaction_id"]
        return ResolutionResult("exact_transaction_id", w, decide(w))

    if candidate_fund_account_id and known_fund_account_id and candidate_fund_account_id == known_fund_account_id:
        w = SIGNAL_WEIGHTS["exact_fund_account_id"]
        return ResolutionResult("exact_fund_account_id", w, decide(w))

    if candidate_upi_id and known_upi_id and candidate_upi_id.lower() == known_upi_id.lower():
        w = SIGNAL_WEIGHTS["exact_upi_id"]
        return ResolutionResult("exact_upi_id", w, decide(w))

    if candidate_phone and known_phone and normalize_phone(candidate_phone) == normalize_phone(known_phone):
        w = SIGNAL_WEIGHTS["exact_phone"]
        return ResolutionResult("exact_phone", w, decide(w))

    if candidate_name and known_name and normalize_name(candidate_name) == normalize_name(known_name):
        w = SIGNAL_WEIGHTS["normalized_name"]
        return ResolutionResult("normalized_name", w, decide(w))

    return ResolutionResult("none", 0.0, "KEEP_SEPARATE")
