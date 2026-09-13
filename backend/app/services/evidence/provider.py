import os
import uuid
import logging
from typing import Protocol, List, Dict, Any

class EvidenceProvider(Protocol):
    def extract(self, raw_text: str, source_artifact_id: str) -> List[Dict[str, Any]]:
        ...

class GeminiEvidenceProvider:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing")
        from google import genai
        self.client = genai.Client(api_key=self.api_key)

    def extract(self, raw_text: str, source_artifact_id: str) -> List[Dict[str, Any]]:
        try:
            from google.genai import types
            from pydantic import BaseModel, Field
            
            class ClaimExtraction(BaseModel):
                claim_type: str = Field(description="Must be one of: amount, beneficiary, instruction_signal")
                amount: float | None = Field(None, description="The monetary amount, if claim_type is amount")
                currency: str | None = Field(None, description="Currency code (e.g., INR), if claim_type is amount")
                beneficiary_name: str | None = Field(None, description="Name of the person/entity receiving funds, if claim_type is beneficiary")
                source_text: str = Field(description="The exact snippet of text from the source that supports this claim")
                keywords: list[str] | None = Field(None, description="List of urgent/instructional keywords, if claim_type is instruction_signal")

            class EvidenceExtractionResult(BaseModel):
                claims: list[ClaimExtraction]

            prompt = (
                "You are an expert financial forensic analyst. Read the following evidence "
                "text and extract structured claims about transaction amounts, beneficiaries, "
                "and instruction signals (e.g., urgency). Only extract facts explicitly present in the text.\n\n"
                f"EVIDENCE TEXT:\n{raw_text}"
            )
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=EvidenceExtractionResult,
                    temperature=0.0
                ),
            )
            
            if not response.text:
                return []
                
            result = EvidenceExtractionResult.model_validate_json(response.text)
            
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
                    "source_location": "gemini_extracted",
                    "extraction_method": "gemini_2_5_flash",
                    "claim_type": c.claim_type,
                    "claim_value": claim_value,
                })
            return claims_out
            
        except Exception as e:
            logging.error(f"Gemini API extraction failed: {e}")
            raise

class DeterministicEvidenceProvider:
    def extract(self, raw_text: str, source_artifact_id: str) -> List[Dict[str, Any]]:
        import re
        AMOUNT_PATTERNS = [re.compile(r"(?:rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(cr|crore|l|lakh|lakhs)?", re.IGNORECASE)]
        BENEFICIARY_PATTERNS = [re.compile(r"(?:send|transfer|pay|release)\s+(?:it\s+)?to\s+([A-Z][A-Za-z0-9 &\.]{2,40})", re.IGNORECASE)]
        INSTRUCTION_KEYWORDS = ("urgent", "immediately", "right now", "asap")
        
        def _parse_amount(raw: str, unit: str | None) -> float:
            value = float(raw.replace(",", ""))
            if unit:
                unit = unit.lower()
                if unit in ("cr", "crore"): value *= 10000000
                elif unit in ("l", "lakh", "lakhs"): value *= 100000
            return value

        claims = []
        for pattern in AMOUNT_PATTERNS:
            for match in pattern.finditer(raw_text):
                amount = _parse_amount(match.group(1), match.group(2))
                claims.append({
                    "id": f"CLM_{uuid.uuid4().hex[:10]}",
                    "source_artifact_id": source_artifact_id,
                    "source_location": f"char:{match.start()}-{match.end()}",
                    "extraction_method": "rule_based_extractor",
                    "claim_type": "amount",
                    "claim_value": {"amount": amount, "raw_text": match.group(0)},
                })

        for pattern in BENEFICIARY_PATTERNS:
            for match in pattern.finditer(raw_text):
                claims.append({
                    "id": f"CLM_{uuid.uuid4().hex[:10]}",
                    "source_artifact_id": source_artifact_id,
                    "source_location": f"char:{match.start()}-{match.end()}",
                    "extraction_method": "rule_based_extractor",
                    "claim_type": "beneficiary",
                    "claim_value": {"name": match.group(1).strip(), "raw_text": match.group(0)},
                })
                
        hit_keywords = [kw for kw in INSTRUCTION_KEYWORDS if kw in raw_text.lower()]
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
