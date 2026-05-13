"""
Gọi Gemini API để trích xuất dữ liệu từ ảnh chứng từ.
Đã tối ưu cho các file phức tạp (như MSC).
"""

from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential
from config import GOOGLE_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là chuyên gia OCR cao cấp của AGO Fruit. 
Nhiệm vụ: Trích xuất dữ liệu từ chứng từ vận tải/thương mại với độ chính xác tuyệt đối.
QUY TẮC:
1. Đọc tất cả các vùng trong ảnh, kể cả chữ nhỏ ở góc hoặc trong bảng.
2. Trả về JSON theo đúng schema yêu cầu.
3. Nếu giá trị không có sẵn, hãy cố gắng suy luận từ ngữ cảnh (ví dụ: Invoice No thường nằm gần chữ 'Inv No' hoặc 'Reference').
4. Nếu thực sự không thấy, mới để null.
5. KHÔNG giải thích, chỉ trả về JSON.
"""

from .schemas import SCHEMA_DEFINITIONS

class LLMExtractor:
    def __init__(self, api_key: str = GOOGLE_API_KEY, model: str = GEMINI_MODEL):
        if not api_key: raise ValueError("Thieu API Key")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def extract(self, images: List[Image.Image], filename: str = "unknown.pdf") -> Dict[str, Any]:
        # Lưu ảnh debug để anh kiểm tra
        debug_dir = Path("debug_images")
        debug_dir.mkdir(exist_ok=True)
        for i, img in enumerate(images):
            img.save(debug_dir / f"debug_{i}.png")
        
        # 1. Detect Type
        doc_type = self._detect_type(images)
        print(f"--- 🔍 AI nhận diện loại: {doc_type} ---")
        
        # 2. Extract Data
        return self._extract_data(images, doc_type, filename)

    def _detect_type(self, images: List[Image.Image]) -> str:
        prompt = "Phân tích ảnh và cho biết đây là loại chứng từ gì: commercial_invoice, packing_list, bill_of_lading, phytosanitary_certificate, certificate_of_origin. Trả về duy nhất từ khóa đó."
        response = self.model.generate_content([prompt] + images)
        res_text = response.text.lower()
        for t in SCHEMA_DEFINITIONS.keys():
            if t in res_text: return t
        return "packing_list" # Default nếu ko chắc

    def _extract_data(self, images: List[Image.Image], doc_type: str, filename: str) -> Dict[str, Any]:
        schema = SCHEMA_DEFINITIONS.get(doc_type, SCHEMA_DEFINITIONS["packing_list"])
        schema_text = json.dumps(schema, indent=2, ensure_ascii=False)
        
        user_prompt = f"""Hãy trích xuất dữ liệu từ ảnh này vào cấu trúc JSON sau.
Cố gắng tìm mọi thông tin có thể, đặc biệt là danh sách mặt hàng (items), số lượng, trọng lượng.

JSON SCHEMA:
{schema_text}
"""
        response = self.model.generate_content(
            [SYSTEM_PROMPT] + images + [user_prompt],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        try:
            data = json.loads(response.text)
        except:
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)

        return {
            "document_type": doc_type,
            "data": data,
            "token_usage": {
                "input": getattr(response.usage_metadata, 'prompt_token_count', 0),
                "output": getattr(response.usage_metadata, 'candidates_token_count', 0)
            }
        }
