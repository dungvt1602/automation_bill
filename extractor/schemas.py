"""
Pydantic models và Schema Definitions cho chứng từ.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    COMMERCIAL_INVOICE = "commercial_invoice"
    PACKING_LIST = "packing_list"
    BILL_OF_LADING = "bill_of_lading"
    PHYTOSANITARY_CERTIFICATE = "phytosanitary_certificate"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    UNKNOWN = "unknown"

class ExtractionResult(BaseModel):
    filename: str
    document_type: DocumentType = DocumentType.UNKNOWN
    overall_confidence: float = 0.0
    needs_review: bool = True
    data: dict = Field(default_factory=dict)
    token_usage: dict = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    @property
    def estimated_cost_vnd(self) -> float:
        inp = self.token_usage.get("input", 0)
        out = self.token_usage.get("output", 0)
        return ((inp * 0.3 / 1000000) + (out * 2.5 / 1000000)) * 25000

# Định nghĩa Schema thô để gửi cho Gemini AI
SCHEMA_DEFINITIONS = {
    "commercial_invoice": {
        "invoice_no": {"value": "string", "confidence": 0.0},
        "date": {"value": "string", "confidence": 0.0},
        "seller_name": {"value": "string", "confidence": 0.0},
        "buyer_name": {"value": "string", "confidence": 0.0},
        "currency": {"value": "string", "confidence": 0.0},
        "items": [
            {
                "description": {"value": "string", "confidence": 0.0},
                "quantity": {"value": "number", "confidence": 0.0},
                "unit_price": {"value": "number", "confidence": 0.0},
                "amount": {"value": "number", "confidence": 0.0}
            }
        ],
        "total_amount": {"value": "number", "confidence": 0.0}
    },
    "packing_list": {
        "packing_list_no": {"value": "string", "confidence": 0.0},
        "invoice_ref": {"value": "string", "confidence": 0.0},
        "items": [
            {
                "description": {"value": "string", "confidence": 0.0},
                "quantity": {"value": "number", "confidence": 0.0},
                "net_weight_kg": {"value": "number", "confidence": 0.0},
                "gross_weight_kg": {"value": "number", "confidence": 0.0}
            }
        ],
        "total_net_weight": {"value": "number", "confidence": 0.0},
        "total_gross_weight": {"value": "number", "confidence": 0.0}
    },
    "bill_of_lading": {
        "bl_no": {"value": "string", "confidence": 0.0},
        "vessel_name": {"value": "string", "confidence": 0.0},
        "port_of_loading": {"value": "string", "confidence": 0.0},
        "container_no": {"value": "string", "confidence": 0.0},
        "gross_weight_kg": {"value": "number", "confidence": 0.0}
    },
    "phytosanitary_certificate": {
        "certificate_no": {"value": "string", "confidence": 0.0},
        "exporter": {"value": "string", "confidence": 0.0},
        "product_description": {"value": "string", "confidence": 0.0}
    },
    "certificate_of_origin": {
        "certificate_no": {"value": "string", "confidence": 0.0},
        "origin_country": {"value": "string", "confidence": 0.0},
        "hs_code": {"value": "string", "confidence": 0.0}
    }
}
