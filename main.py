"""
AGO Fruit Trade Document Automation - CLI Entry Point
Kết nối các module: Processor -> Extractor -> Validator -> DB -> Excel
"""

import argparse
import logging
import sys
from pathlib import Path

from config import SAMPLE_INPUT_DIR, OUTPUT_DIR
from extractor import PDFProcessor, LLMExtractor, Validator
from database import DatabaseManager
from export import ExcelWriter

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AGO-CLI")

class AGOCLI:
    def __init__(self):
        self.processor = PDFProcessor()
        self.extractor = LLMExtractor()
        self.validator = Validator()
        self.db = DatabaseManager()
        self.writer = ExcelWriter()

    def process_file(self, file_path: Path):
        """Xử lý một file PDF duy nhất."""
        logger.info(">>> Đang xử lý: %s", file_path.name)
        try:
            # 1. Chuyển PDF sang ảnh
            images = self.processor.extract_images(file_path)
            
            # 2. Gọi Gemini AI trích xuất
            raw_data = self.extractor.extract(images, filename=file_path.name)
            
            # 3. Xác thực và chấm điểm confidence
            result = self.validator.validate(raw_data, filename=file_path.name)
            
            # 4. Lưu vào Database
            doc_id = self.db.save_extraction(result)
            
            logger.info("Hoàn tất trích xuất ID: %d. Confidence: %.2f", doc_id, result.overall_confidence)
            if result.needs_review:
                logger.warning("(!) Chứng từ này cần review thủ công (Confidence thấp hoặc có lỗi).")
            return result
        except Exception as e:
            logger.error("Lỗi khi xử lý %s: %s", file_path.name, str(e))
            return None

    def process_batch(self, input_dir: Path):
        """Xử lý tất cả file PDF trong thư mục."""
        files = list(input_dir.glob("*.pdf"))
        if not files:
            logger.warning("Không tìm thấy file PDF nào trong %s", input_dir)
            return

        logger.info("Tìm thấy %d file. Bắt đầu xử lý hàng loạt...", len(files))
        results = []
        for f in files:
            res = self.process_file(f)
            if res:
                results.append(res)
        
        return results

    def export_all(self, output_file: str = "final_results.xlsx"):
        """Lấy toàn bộ dữ liệu từ DB và xuất ra Excel."""
        logger.info("Đang lấy dữ liệu từ database để xuất Excel...")
        # (Lưu ý: Để đơn giản cho PoC, ta sẽ xuất các kết quả vừa trích xuất xong 
        # hoặc load từ DB và giả lập lại ExtractionResult objects)
        docs = self.db.get_all_documents()
        if not docs:
            logger.error("Database trống, không có gì để xuất.")
            return

        # Mock lại ExtractionResult objects từ DB data
        # Trong thực tế production sẽ có logic convert chuyên sâu hơn
        from extractor.schemas import ExtractionResult, DocumentType
        import json
        
        results_to_export = []
        for d in docs:
            res = ExtractionResult(
                filename=d['filename'],
                document_type=DocumentType(d['document_type']),
                overall_confidence=d['overall_confidence'],
                needs_review=(d['status'] == 'pending'),
                data=json.loads(d['raw_data_json']),
                token_usage={'input': d['token_usage_input'], 'output': d['token_usage_output']}
            )
            results_to_export.append(res)
        
        output_path = OUTPUT_DIR / output_file
        self.writer.write_results(results_to_export, output_path)
        print(f"\n✅ Đã xuất file Excel thành công tại: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="AGO Fruit Trade Document Automation CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Command: extract
    extract_parser = subparsers.add_parser("extract", help="Trích xuất 1 file PDF")
    extract_parser.add_argument("file", help="Đường dẫn tới file PDF")

    # Command: batch
    batch_parser = subparsers.add_parser("batch", help="Trích xuất toàn bộ PDF trong thư mục")
    batch_parser.add_argument("--dir", default=str(SAMPLE_INPUT_DIR), help="Thư mục chứa PDF")

    # Command: export
    export_parser = subparsers.add_parser("export", help="Xuất toàn bộ database ra Excel")
    export_parser.add_argument("--name", default="ago_extraction_results.xlsx", help="Tên file đầu ra")

    args = parser.parse_args()
    cli = AGOCLI()

    if args.command == "extract":
        cli.process_file(Path(args.file))
    elif args.command == "batch":
        cli.process_batch(Path(args.dir))
    elif args.command == "export":
        cli.export_all(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
