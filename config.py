"""
Cấu hình chung cho hệ thống trích xuất chứng từ thương mại.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Đường dẫn ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
SAMPLE_INPUT_DIR = BASE_DIR / "sample_input"
SAMPLE_OUTPUT_DIR = BASE_DIR / "sample_output"
OUTPUT_DIR = BASE_DIR / "output"
DB_PATH = BASE_DIR / "extraction.db"

# Tạo thư mục nếu chưa có
for d in [SAMPLE_INPUT_DIR, SAMPLE_OUTPUT_DIR, OUTPUT_DIR]:
    d.mkdir(exist_ok=True)

# ── API ───────────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

# ── Trích xuất ────────────────────────────────────────────────────────────────
PDF_DPI = 300                     # Độ phân giải chuyển PDF → ảnh
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
MAX_RETRIES = 3                   # Số lần retry khi gọi API lỗi
IMAGE_MAX_DIMENSION = 2048        # Resize ảnh lớn để tiết kiệm token

# ── Loại chứng từ được hỗ trợ ─────────────────────────────────────────────────
DOCUMENT_TYPES = [
    "commercial_invoice",
    "packing_list",
    "bill_of_lading",
    "phytosanitary_certificate",
    "certificate_of_origin",
]

# ── Chi phí (để theo dõi) ─────────────────────────────────────────────────────
COST_PER_1M_INPUT_TOKENS = 0.30   # USD - Gemini 2.5 Flash
COST_PER_1M_OUTPUT_TOKENS = 2.50  # USD - Gemini 2.5 Flash
