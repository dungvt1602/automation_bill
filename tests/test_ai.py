"""
Test AI Extraction (Sửa lỗi đường dẫn)
"""
import sys
import json
from pathlib import Path

# Thư mục gốc của dự án
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from extractor.pdf_processor import PDFProcessor
from extractor.llm_extractor import LLMExtractor

def test_ai_extraction():
    processor = PDFProcessor(dpi=300)
    
    # ĐƯỜNG DẪN TỚI FILE CỦA ANH
    pdf_path = ROOT_DIR / "sample_input" / "MSC packing list form.pdf"
    
    if not pdf_path.exists():
        print(f"❌ Không tìm thấy file tại: {pdf_path}")
        return

    images = processor.extract_images(pdf_path)
    
    print(f"--- 🤖 Đang gửi ảnh '{pdf_path.name}' lên Gemini AI ---")
    try:
        extractor = LLMExtractor()
        result = extractor.extract(images, filename=pdf_path.name)
        print("\n✅ KẾT QUẢ JSON:")
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")

if __name__ == "__main__":
    test_ai_extraction()
