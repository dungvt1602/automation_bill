# AGO Fruit — Tự Động Hóa Chứng Từ Thương Mại

> **Bài test kỹ thuật — Vị trí IT Dept, AGO Fruit (Option A: Trade Document Automation)**

Hệ thống tự động trích xuất dữ liệu có cấu trúc từ PDF chứng từ thương mại (Commercial Invoice, Packing List, Bill of Lading, Phyto, C/O) → xác thực → nhập Excel, có bước review thủ công cho các trường hợp độ tin cậy thấp.

---


## Cấu Trúc Dự Án

```
ago-trade-doc-automation/
├── README.md                    # Hướng dẫn cài đặt + sử dụng (file này)
├── proposal.md                  # Tài liệu đề xuất 4 trang
├── walkthrough.md               # Bài viết tổng quan 200-300 từ
├── requirements.txt             # Thư viện Python
├── .env.example                 # Template API key
├── config.py                    # Hằng số cấu hình
├── main.py                      # Điểm vào CLI
├── app.py                       # Giao diện review Streamlit
├── extractor/
│   ├── __init__.py
│   ├── pdf_processor.py         # Chuyển PDF → ảnh
│   ├── llm_extractor.py         # Tích hợp API Gemini
│   ├── schemas.py               # Pydantic models cho từng loại chứng từ
│   └── validator.py             # Xác thực + chấm điểm độ tin cậy
├── export/
│   ├── __init__.py
│   └── excel_writer.py          # Xuất Excel có format
├── database/
│   ├── __init__.py
│   └── models.py                # Models SQLite cho audit log
├── sample_input/                # PDF mẫu để test
│   └── (chứng từ thương mại mẫu)
├── sample_output/               # File Excel được tạo
│   └── (output mẫu)
└── tests/
    └── test_extractor.py        # Test cơ bản
```

---

## Hướng Dẫn Khởi Động (Dành cho Windows)

### 1. Cài đặt Môi trường ảo (Virtual Environment)
Mở Terminal (PowerShell hoặc CMD) tại thư mục dự án và chạy:

```powershell
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
.\venv\Scripts\activate

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Chay du an
streamlit run app.py
```

### 2. Cấu hình API Key
1. Copy file `.env.example` thành `.env`: `copy .env.example .env`
2. Lấy Google API Key miễn phí tại: [AI Studio](https://aistudio.google.com/apikey)
3. Mở file `.env` bằng Notepad hoặc VS Code và dán key vào:
   ```env
   GOOGLE_API_KEY=AIzaSy... (Key của bạn ở đây)
   ```

### 3. Tạo dữ liệu mẫu để chạy thử
Chạy script sau để hệ thống tự tạo ra các file PDF chứng từ giả lập:
```powershell
python tools/generate_samples.py
```

---

## Cách Sử Dụng

### Lựa chọn 1: Giao diện Web (Khuyên dùng)
```powershell
streamlit run app.py
```

### Lựa chọn 2: Dòng lệnh (CLI)
```powershell
python main.py batch
python main.py export --name ket_qua_ago.xlsx
```

### Các công cụ hỗ trợ (Tools)
- **Truy vấn Database:** `python tools/query_db.py`
- **Dọn dẹp dự án:** `python tools/reset_project.py`

### Các bài kiểm tra (Tests)
- **Test PDF -> Ảnh:** `python tests/test_pdf.py`
- **Test AI trích xuất:** `python tests/test_ai.py`

Mở trình duyệt tại `http://localhost:8501` để:
- Upload PDF → xem dữ liệu trích xuất song song với preview PDF
- Sửa trường trực tiếp, duyệt/từ chối
- Xử lý hàng loạt
- Xem audit log
- Xuất Excel

---

## Chi Tiết Kỹ Thuật

### Pipeline Trích Xuất Chính

#### `extractor/schemas.py` — Pydantic Models

Mỗi loại chứng từ có Pydantic model riêng, mỗi trường kèm `confidence: float` (0.0–1.0):

- **`CommercialInvoice`**: invoice_no, date, seller, buyer, items (product, qty, unit_price, total), currency, incoterms
- **`PackingList`**: packing_list_no, items (description, qty, net_weight, gross_weight, dimensions, cartons)
- **`BillOfLading`**: bl_no, shipper, consignee, vessel, port_of_loading, port_of_discharge, container_no, seal_no
- **`PhytosanitaryCertificate`**: cert_no, exporter, importer, origin_country, product_description, treatment
- **`CertificateOfOrigin`**: cert_no, exporter, importer, origin_country, hs_code, description

#### `extractor/pdf_processor.py` — PDF → Ảnh

- Chuyển trang PDF sang ảnh ở 300 DPI bằng PyMuPDF
- Tiền xử lý ảnh cơ bản (xoay tự động, tăng độ tương phản)
- Xử lý chứng từ nhiều trang

#### `extractor/llm_extractor.py` — Gemini API

- Gửi ảnh trang lên Gemini 2.5 Flash kèm prompt có cấu trúc
- Tự động nhận diện loại chứng từ
- Phân tích output ở chế độ JSON
- Logic retry với exponential backoff
- Theo dõi token usage để giám sát chi phí

#### `extractor/validator.py` — Xác Thực

- Xác thực chéo giữa các trường (VD: tổng từng dòng = tổng hóa đơn)
- Chuẩn hóa định dạng ngày
- Xác thực tiền tệ
- Chấm điểm độ tin cậy: trường dưới ngưỡng (0.7) → đánh dấu cần review
- Độ tin cậy tổng thể = min(độ tin cậy các trường)

### Kiểm Soát Quản Lý

#### `database/models.py` — Audit Log

- Bảng SQLite: `documents`, `extraction_results`, `audit_log`, `user_actions`
- Theo dõi: ai upload, khi nào xử lý, điểm độ tin cậy, ai duyệt, sửa gì
- Nhật ký kiểm toán đầy đủ cho tuân thủ quy trình

---

## Xử Lý Trường Hợp Ngoại Lệ

| Trường hợp | Chiến lược |
|---|---|
| Scan chất lượng thấp | Tiền xử lý ảnh (tương phản, chỉnh nghiêng); nếu confidence < 0.5, đánh dấu "cần nhập tay" |
| Dữ liệu bị ảo giác (hallucination) | Xác thực chéo giữa các trường; so sánh tổng trích xuất vs. từng dòng; yêu cầu review thủ công cho layout chứng từ lần đầu |
| Giới hạn tốc độ API | Exponential backoff + xử lý theo hàng đợi; batch API cho việc không gấp |
| Chứng từ đa ngôn ngữ | Gemini xử lý đa ngôn ngữ tự nhiên; prompt yêu cầu rõ xử lý tiếng Việt + tiếng Anh |
| Layout không nhất quán | Trích xuất bằng LLM không phụ thuộc layout (khác OCR theo template); prompt định nghĩa trường, không định nghĩa vị trí |
| Chứng từ nhiều trang | Ghép các trang vào một context trích xuất; xử lý bảng nằm trên nhiều trang |
| PDF có mật khẩu/mã hóa | Phát hiện và thông báo người dùng; bỏ qua xử lý tự động |

---


## Sample Input/Output

### Input mẫu (`sample_input/`)

Các file PDF chứng từ thương mại giả lập thực tế:
- `commercial_invoice_sample.pdf` — Hóa đơn thương mại (xuất khẩu trái cây)
- `packing_list_sample.pdf` — Phiếu đóng gói

### Output mẫu (`sample_output/`)

- `extraction_results.xlsx` — File Excel với dữ liệu đã trích xuất, mỗi sheet cho một loại chứng từ
- `extraction_results.json` — Dữ liệu JSON thô từ pipeline

---
