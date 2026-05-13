"""
Test PDF -> Image conversion (Sửa lỗi đường dẫn linh hoạt)
"""
import sys
import os
from pathlib import Path

# Thư mục gốc của dự án
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from extractor.pdf_processor import PDFProcessor

def test_pdf_to_image():
    processor = PDFProcessor(dpi=300)
    
    # ĐƯỜNG DẪN TỚI FILE CỦA ANH
    # Nếu anh để file trong thư mục tests/sample_input/
    pdf_path = ROOT_DIR/ "sample_input" / "MSC packing list form.pdf"
    
    # Kiểm tra xem file có tồn tại không
    if not pdf_path.exists():
        print(f"❌ Không tìm thấy file tại: {pdf_path}")
        print("💡 Anh hãy kiểm tra xem file đã được chép vào thư mục tests/sample_input/ chưa nhé.")
        return

    print(f"--- Đang xử lý: {pdf_path.name} ---")
    images = processor.extract_images(pdf_path)
    
    if images:
        output_path = ROOT_DIR / "test_page_1.png"
        images[0].save(output_path)
        print(f"✅ Thành công! Đã tạo file '{output_path}'")
    else:
        print("❌ Lỗi: Không trích xuất được ảnh.")

if __name__ == "__main__":
    test_pdf_to_image()
