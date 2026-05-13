"""
Chuyển đổi PDF → ảnh bằng PyMuPDF (fitz).
Tối ưu hóa độ nét cho Gemini Vision.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
from PIL import Image

from config import PDF_DPI, IMAGE_MAX_DIMENSION

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, dpi: int = 400, max_dim: int = 3072): # Tăng DPI và kích thước tối đa
        self.dpi = dpi
        self.max_dim = max_dim

    def extract_images(self, pdf_path: str | Path) -> List[Image.Image]:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {pdf_path}")

        try:
            doc = fitz.open(str(pdf_path))
        except Exception as exc:
            raise ValueError(f"Không thể mở PDF: {exc}")

        images: List[Image.Image] = []
        
        for i in range(len(doc)):
            page = doc[i]
            # Render trang với DPI cao
            zoom = self.dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Chỉ resize nếu ảnh thực sự quá khổng lồ (vượt mức cho phép của Google API)
            if max(img.width, img.height) > self.max_dim:
                ratio = self.max_dim / max(img.width, img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
            images.append(img)
            logger.info(f"Đã render trang {i+1}: {img.width}x{img.height}")

        doc.close()
        return images
