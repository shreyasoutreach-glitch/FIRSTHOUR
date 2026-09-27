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
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing")
        from google import genai
        self.client = genai.Client(api_key=self.api_key)

    @staticmethod
    def _schema():
        from pydantic import BaseModel, Field

        class ClaimExtraction(BaseModel):
            claim_type: str = Field(description="Must be one of: amount, beneficiary, instruction_signal")
            amount: float | None = Field(None, description="The monetary amount, if claim_type is amount")
            currency: str | None = Field(None, description="Currency code (e.g., INR), if claim_type is amount")
            beneficiary_name: str | None = Field(None, description="Name of the person/entity receiving funds")
            source_text: str = Field(description="Exact snippet from the source supporting this claim")
            keywords: list[str] | None = Field(None, description="Urgent/instructional keywords")

        class EvidenceExtractionResult(BaseModel):
            claims: list[ClaimExtraction]

        return EvidenceExtractionResult

    def _prompt(self) -> str:
        return (
            "You are extracting evidence for a financial investigation. "
            "Extract only claims explicitly visible in the supplied evidence. "
            "Do not infer identity, authorization, transaction status, or intent. "
            "Extract amounts, beneficiary names, and instruction/urgency signals. "
            "Every claim must include the exact source text that supports it."
        )

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
            return _claims_from_model(result, source_artifact_id, "gemini_2_5_flash_text")
        except Exception as exc:
            logging.error("Gemini text extraction failed: %s", exc)
            raise

    def extract_binary(self, data: bytes, mime_type: str, source_artifact_id: str) -> tuple[str, List[Dict[str, Any]]]:
        """Extract evidence from an image/PDF using Gemini's multimodal input.

        The model output remains candidate evidence only. Verification against
        financial records happens later in routes_evidence.py.
        """
        try:
            from google.genai import types

            schema = self._schema()
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=data, mime_type=mime_type),
                    self._prompt(),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.0,
                ),
            )
            if not response.text:
                return "", []
            result = schema.model_validate_json(response.text)
            claims = _claims_from_model(result, source_artifact_id, "gemini_2_5_flash_vision")
            # Preserve the model's grounded snippets as searchable text, not
            # as asserted facts. The claims are independently verified later.
            raw_text = "\n".join(
                c["claim_value"].get("raw_text", "")
                for c in claims
                if isinstance(c.get("claim_value"), dict)
            )
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
