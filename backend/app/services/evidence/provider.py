import os
import uuid
import logging
from typing import Protocol, List, Dict, Any


class EvidenceProvider(Protocol):
    def extract(self, raw_text: str, source_artifact_id: str) -> List[Dict[str, Any]]:
        ...


def _claims_from_model(result, source_artifact_id: str, method: str) -> List[Dict[str, Any]]:
    claims_out = []
    for c in result.claims:
        claim_value = {}
        if c.claim_type == "amount" and c.amount is not None:
            claim_value = {"amount": c.amount, "raw_text": c.source_text}
        elif c.claim_type == "beneficiary" and c.beneficiary_name:
            claim_value = {"name": c.beneficiary_name, "raw_text": c.source_text}
        elif c.claim_type == "instruction_signal" and c.keywords:
            claim_value = {"keywords": c.keywords}
        claims_out.append({
            "id": f"CLM_{uuid.uuid4().hex[:10]}",
            "source_artifact_id": source_artifact_id,
            "source_location": method,
            "extraction_method": method,
            "claim_type": c.claim_type,
            "claim_value": claim_value,
        })
    return claims_out


class GeminiEvidenceProvider:
    """AI may locate source snippets, but it may not author financial values.

    Amounts and beneficiary identifiers are parsed deterministically from the
    model-returned source snippets by DeterministicEvidenceProvider. The model
    therefore never becomes the authority for a financial value.
    """
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing")
        from google import genai
        self.client = genai.Client(api_key=self.api_key)

    @staticmethod
    def _schema():
        from pydantic import BaseModel, Field

        class EvidenceSnippet(BaseModel):
            source_text: str = Field(description="Exact visible snippet from the supplied evidence.")
            keywords: list[str] = Field(default_factory=list, description="Visible instruction/urgency words only.")

        class EvidenceExtractionResult(BaseModel):
            snippets: list[EvidenceSnippet]

        return EvidenceExtractionResult

    def _prompt(self) -> str:
        return (
            "You are locating evidence for a financial investigation. "
            "Return only exact snippets visibly present in the evidence and visible instruction/urgency keywords. "
            "Do not generate, normalize, calculate, infer or restate any amount, beneficiary, timestamp, identity, status or score. "
            "The exact source snippet will be parsed deterministically by the application."
        )

    def _compile_snippets(self, snippets, source_artifact_id: str) -> List[Dict[str, Any]]:
        deterministic = DeterministicEvidenceProvider()
        claims: List[Dict[str, Any]] = []
        for snippet in snippets:
            claims.extend(deterministic.extract(snippet.source_text, source_artifact_id))
            if snippet.keywords:
                claims.append({
                    "id": f"CLM_{uuid.uuid4().hex[:10]}",
                    "source_artifact_id": source_artifact_id,
                    "source_location": "model_snippet",
                    "extraction_method": "gemini_2_5_flash_snippet_locator",
                    "claim_type": "instruction_signal",
                    "claim_value": {"keywords": sorted(set(snippet.keywords))},
                })
        return claims

    def extract(self, raw_text: str, source_artifact_id: str) -> List[Dict[str, Any]]:
        try:
            from google.genai import types
            schema = self._schema()
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{self._prompt()}\n\nEVIDENCE TEXT:\n{raw_text}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.0,
                ),
            )
            if not response.text:
                return []
            result = schema.model_validate_json(response.text)
            return self._compile_snippets(result.snippets, source_artifact_id)
        except Exception as exc:
            logging.error("Gemini text extraction failed: %s", exc)
            raise

    def extract_binary(self, data: bytes, mime_type: str, source_artifact_id: str) -> tuple[str, List[Dict[str, Any]]]:
        try:
            from google.genai import types
            schema = self._schema()
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Part.from_bytes(data=data, mime_type=mime_type), self._prompt()],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.0,
                ),
            )
            if not response.text:
                return "", []
            result = schema.model_validate_json(response.text)
            claims = self._compile_snippets(result.snippets, source_artifact_id)
            raw_text = "\n".join(s.source_text for s in result.snippets)
            return raw_text, claims
        except Exception as exc:
            logging.error("Gemini multimodal extraction failed: %s", exc)
            raise


class DeterministicEvidenceProvider:
    def extract(self, raw_text: str, source_artifact_id: str) -> List[Dict[str, Any]]:
        import re

        amount_patterns = [
            re.compile(r"(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(cr|crore|l|lakh|lakhs)?", re.IGNORECASE)
        ]
        beneficiary_patterns = [
            re.compile(r"(?:send|transfer|pay|release)\s+(?:it\s+)?to\s+([A-Z][A-Za-z0-9 &\.]{2,40})", re.IGNORECASE)
        ]
        instruction_keywords = ("urgent", "immediately", "right now", "asap", "confidential", "don't call", "do not call")

        def parse_amount(raw: str, unit: str | None) -> float:
            value = float(raw.replace(",", ""))
            if unit:
                unit = unit.lower()
                if unit in ("cr", "crore"):
                    value *= 10000000
                elif unit in ("l", "lakh", "lakhs"):
                    value *= 100000
            return value

        claims = []
        for pattern in amount_patterns:
            for match in pattern.finditer(raw_text):
                claims.append({
                    "id": f"CLM_{uuid.uuid4().hex[:10]}",
                    "source_artifact_id": source_artifact_id,
                    "source_location": f"char:{match.start()}-{match.end()}",
                    "extraction_method": "rule_based_extractor",
                    "claim_type": "amount",
                    "claim_value": {"amount": parse_amount(match.group(1), match.group(2)), "raw_text": match.group(0)},
                })

        for pattern in beneficiary_patterns:
            for match in pattern.finditer(raw_text):
                claims.append({
                    "id": f"CLM_{uuid.uuid4().hex[:10]}",
                    "source_artifact_id": source_artifact_id,
                    "source_location": f"char:{match.start()}-{match.end()}",
                    "extraction_method": "rule_based_extractor",
                    "claim_type": "beneficiary",
                    "claim_value": {"name": match.group(1).strip(), "raw_text": match.group(0)},
                })

        hit_keywords = [kw for kw in instruction_keywords if kw in raw_text.lower()]
        if hit_keywords:
            claims.append({
                "id": f"CLM_{uuid.uuid4().hex[:10]}",
                "source_artifact_id": source_artifact_id,
                "source_location": "full_text",
                "extraction_method": "rule_based_extractor",
                "claim_type": "instruction_signal",
                "claim_value": {"keywords": hit_keywords},
            })
        return claims
