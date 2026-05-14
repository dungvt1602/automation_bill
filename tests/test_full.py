"""
Full Pipeline Test (Sửa lỗi đường dẫn)
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from extractor import PDFProcessor, LLMExtractor, Validator
from database import DatabaseManager
from export.excel_writer import ExcelWriter

def test_full_pipeline():
    processor = PDFProcessor()
    extractor = LLMExtractor()
    validator = Validator()
    db = DatabaseManager()
    excel_writer = ExcelWriter()
    
    pdf_path = ROOT_DIR / "sample_input" / "commercial_invoice_sample.pdf"
    
    if not pdf_path.exists():
        print(f"❌ Không tìm thấy file tại: {pdf_path}")
        return

    print(f"--- 🚀 Bắt đầu quy trình Full cho: {pdf_path.name} ---")
    images = processor.extract_images(pdf_path)
    raw_output = extractor.extract(images, filename=pdf_path.name)
    result = validator.validate(raw_output, filename=pdf_path.name)
    doc_id = db.save_extraction(result)
    
    print(f"✅ HOÀN TẤT TRÍCH XUẤT! ID DB: {doc_id}")
    print(f"- Loại chứng từ: {result.document_type}")
    print(f"- Confidence: {result.overall_confidence}")
    
    # Xuất ra file Excel trong thư mục sample_output
    output_path = ROOT_DIR / "sample_output" / "test_result_MSC.xlsx"
    excel_writer.write_results([result], output_path)
    print(f"\n📊 Đã xuất file Excel thử nghiệm tại: {output_path}")

if __name__ == "__main__":
    test_full_pipeline()
