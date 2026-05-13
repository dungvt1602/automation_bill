# Plan — Kế Hoạch Triển Khai (FINAL) ✅

## Phase 1: Tài Liệu ✅
- [x] `proposal.md` — Đề xuất kiến trúc & chi phí
- [x] `walkthrough.md` — Bài viết tổng quan thiết kế
- [x] `requirements.txt` — Thư viện Python
- [x] `.env.example` — Cấu hình API key
- [x] `config.py` — Hằng số hệ thống
- [x] `README.md` — Hướng dẫn cài đặt & sử dụng chi tiết
- [x] `AGENT.MD` — Theo dõi yêu cầu bài toán

## Phase 2: Core Extraction Pipeline ✅
- [x] `extractor/schemas.py` — Pydantic models & JSON Schemas
- [x] `extractor/pdf_processor.py` — PDF -> Image (400 DPI)
- [x] `extractor/llm_extractor.py` — Gemini AI (Strategy: Detect -> Extract)
- [x] `extractor/validator.py` — Cross-field validation & Confidence scoring

## Phase 3: Export & Database ✅
- [x] `database/models.py` — SQLite (Documents & Audit Log)
- [x] `export/excel_writer.py` — Xuất Excel "Data Entry" chuyên nghiệp

## Phase 4: App Layer ✅
- [x] `main.py` — Giao diện dòng lệnh (CLI)
- [x] `app.py` — Giao diện Web Review (Streamlit)

## Phase 5: Sample Data & Tools ✅
- [x] `tools/generate_samples.py` — Tạo dữ liệu mẫu
- [x] `tools/query_db.py` — Truy vấn SQL trực tiếp
- [x] `tools/reset_project.py` — Dọn dẹp dự án
- [x] `tests/` — Bộ script kiểm tra từng module

## Phase 6: Finalize ✅
- [x] Kiểm tra pipeline chạy mượt mà
- [x] Tổ chức cấu hình thư mục sạch sẽ (tests, tools)
- [x] Sẵn sàng bàn giao (Push GitHub)
