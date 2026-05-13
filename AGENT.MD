# AGENT.MD — Yêu Cầu Đề Bài & Cách Làm

## Đề Bài

**Vị trí:** IT Dept — AGO Fruit (công ty nông sản xuất nhập khẩu)  
**Bài test:** Technical Assessment trước phỏng vấn  
**Option chọn:** Option A — Trade Document Automation  

---

## Bài Toán

AGO Fruit nhận **30–50 PDF/ngày** gồm các loại chứng từ thương mại:

| Loại chứng từ | Viết tắt |
|---|---|
| Commercial Invoice | CI |
| Packing List | PL |
| Bill of Lading | B/L |
| Phytosanitary Certificate | Phyto |
| Certificate of Origin | C/O |

**Vấn đề hiện tại:**
- Layout không nhất quán giữa các nhà cung cấp
- Nhập tay vào Excel mất ~10–15 phút/file → **5–12 giờ nhân công/ngày**
- Dễ sai sót khi nhập thủ công

**Yêu cầu:**
- Tự động hóa: trích xuất → xác thực → nhập Excel
- Chỉ cần review thủ công cho trường hợp độ tin cậy thấp

---

## Ràng Buộc

| Ràng buộc | Chi tiết |
|---|---|
| Ngân sách | Tối đa **5,000,000 VND/tháng** cho chi phí AI/LLM API |
| Bảo trì | Junior developer không có nền tảng ML phải maintain được |
| Ngôn ngữ | Hỗ trợ tiếng Việt (chứng từ hoặc nội dung) |

---

## Deliverables Cần Nộp

### 1. Proposal (PDF/Word/Markdown, tối đa 4 trang)
- [x] Kiến trúc và tech stack, kèm lý do → `proposal.md`
- [x] Phân tích chi phí: link trang giá chính thức (có ngày kiểm tra); chi phí/chứng từ; chi phí dự tính/tháng
- [x] Edge cases và cách xử lý (scan kém, hallucination, rate limit)
- [x] Cách ban quản lý kiểm soát (cổng phê duyệt, audit log)

### 2. Working PoC — GitHub repo
- [ ] README và sample input/output → `README.md`
- [ ] Prototype xử lý ít nhất một core flow
- [ ] Mời `logistics@agoexim.com` nếu repo private

### 3. Short Walkthrough (chọn 1 trong 2)
- [x] ~~Video 3 phút (Loom/YouTube)~~
- [x] Bài viết 200–300 từ → `walkthrough.md`
  - Quyết định thiết kế chính
  - Sẽ làm gì khác nếu có thêm thời gian
  - Một giả định chưa chắc chắn

---

## Cách Làm

### Chiến lược chính: Vision-LLM thay vì OCR truyền thống

```
PDF → PyMuPDF (render 300 DPI) → Gemini 2.5 Flash (Vision + JSON mode)
  → Structured JSON → Pydantic Validation → Confidence Scoring
  → [Cao] → Auto-export Excel
  → [Thấp] → Streamlit Review UI → Duyệt/Sửa → Excel
```

**Tại sao không dùng OCR (Tesseract)?**
- OCR truyền thống cần: OCR → regex parsing → template matching per supplier
- Mỗi supplier layout khác nhau → phải viết template riêng → không scale
- Vision-LLM hiểu tài liệu trực quan, giống cách con người đọc → layout-agnostic

**Tại sao Gemini 2.5 Flash?**
- Rẻ nhất trong các model multimodal: ~$0.003/chứng từ (~75 VND)
- Hỗ trợ tiếng Việt mạnh
- Native JSON output — không cần parse text
- Budget 5M VND/tháng → chỉ dùng 1.7–3.3%

### Tech Stack

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.11+ |
| LLM | Gemini 2.5 Flash API |
| PDF→Ảnh | PyMuPDF (pure Python) |
| Validation | Pydantic models |
| Review UI | Streamlit |
| Database | SQLite |
| Excel | openpyxl |
| Retry | tenacity |

### Quy trình phát triển

1. Tạo tài liệu (proposal, walkthrough, README) ← **đã xong**
2. Xây pipeline trích xuất (schemas, pdf_processor, llm_extractor, validator)
3. Xây export Excel + database audit log
4. Xây Streamlit review UI
5. Tạo sample PDF mẫu + chạy demo
6. Test end-to-end + chụp screenshot

---

## Ghi Chú Về AI

> *"Using ChatGPT, Claude, or Copilot is permitted and expected. We're evaluating how you think and what you can ship — not whether you avoid AI."*

Dự án này sử dụng AI (Claude) làm công cụ hỗ trợ. Tất cả quyết định kiến trúc, lựa chọn tech stack, và thiết kế pipeline đều dựa trên phân tích yêu cầu thực tế của AGO Fruit.
