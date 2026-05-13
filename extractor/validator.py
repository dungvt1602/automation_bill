"""
Xác thực kết quả trích xuất + chấm điểm confidence tổng thể.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import List, Dict, Any

from config import CONFIDENCE_THRESHOLD
from .schemas import DocumentType, ExtractionResult

logger = logging.getLogger(__name__)

# Tiền tệ hợp lệ thường gặp trong xuất nhập khẩu nông sản
VALID_CURRENCIES = {"USD", "EUR", "VND", "CNY", "JPY", "KRW", "THB", "TWD", "GBP", "AUD"}

# Incoterms 2020
VALID_INCOTERMS = {
    "EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CPT", "CIP",
    "DAP", "DPU", "DDP",
}

class Validator:
    def __init__(self, threshold: float = CONFIDENCE_THRESHOLD):
        self.threshold = threshold

    def validate(self, extraction_output: Dict[str, Any], filename: str = "unknown.pdf") -> ExtractionResult:
        doc_type_str = extraction_output.get("document_type", "unknown")
        data = extraction_output.get("data", {})
        token_usage = extraction_output.get("token_usage", {})

        errors: List[str] = []
        warnings: List[str] = []

        try:
            doc_type = DocumentType(doc_type_str)
        except ValueError:
            doc_type = DocumentType.UNKNOWN
            errors.append(f"Loại chứng từ không nhận diện được: {doc_type_str}")

        confidences = self._collect_confidences(data)

        if doc_type == DocumentType.COMMERCIAL_INVOICE:
            warnings.extend(self._validate_invoice(data))
        elif doc_type == DocumentType.BILL_OF_LADING:
            warnings.extend(self._validate_bill_of_lading(data))

        overall = min(confidences) if confidences else 0.0
        if not confidences:
            errors.append("Không tìm thấy trường nào có confidence")

        needs_review = overall < self.threshold or len(errors) > 0

        return ExtractionResult(
            filename=filename,
            document_type=doc_type,
            overall_confidence=round(overall, 3),
            needs_review=needs_review,
            data=data,
            token_usage=token_usage,
            errors=errors,
            warnings=warnings,
        )

    def _collect_confidences(self, data: Any) -> List[float]:
        confidences: List[float] = []
        self._walk_confidences(data, confidences)
        return confidences

    def _walk_confidences(self, obj: Any, out: List[float]):
        if isinstance(obj, dict):
            if "confidence" in obj and "value" in obj:
                conf = obj.get("confidence", 0.0)
                if isinstance(conf, (int, float)):
                    out.append(float(conf))
            else:
                for v in obj.values():
                    self._walk_confidences(v, out)
        elif isinstance(obj, list):
            for item in obj:
                self._walk_confidences(item, out)

    def _validate_invoice(self, data: Dict) -> List[str]:
        warnings = []
        items = data.get("items", [])
        total_field = data.get("total_amount", {})
        total_val = total_field.get("value") if isinstance(total_field, dict) else None

        if items and total_val is not None:
            line_sum = 0.0
            for item in items:
                amt = item.get("amount", {})
                if isinstance(amt, dict) and amt.get("value") is not None:
                    try:
                        line_sum += float(amt["value"])
                    except: pass
            try:
                total_num = float(total_val)
                if line_sum > 0 and abs(line_sum - total_num) > 0.01 * total_num:
                    warnings.append(f"Tổng dòng ({line_sum:,.2f}) ≠ tổng hóa đơn ({total_num:,.2f}).")
            except: pass
        return warnings

    def _validate_bill_of_lading(self, data: Dict) -> List[str]:
        warnings = []
        container = data.get("container_no", {})
        if isinstance(container, dict):
            cont_val = (container.get("value") or "").strip()
            if cont_val and not re.match(r"^[A-Z]{4}\d{7}$", cont_val):
                warnings.append(f"Container '{cont_val}' không đúng format ISO 6346.")
        return warnings
