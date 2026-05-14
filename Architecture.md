# Đề xuất Kiến trúc Kỹ thuật (Architecture Proposal)

*Dự án: Tự động hóa trích xuất chứng từ cho AGO Fruit*

---

## 1. Kiến trúc & Công nghệ (Architecture & Tech Stack)
- **Luồng xử lý (Pipeline):** Upload PDF → PyMuPDF (Render 400 DPI) → Gemini 2.5 Flash → Validate Schema → Database (SQLite) → Streamlit (UI) → Xuất Excel (Data Entry Format).
- **Backend & Logic (`Python 3.11+`):** *Lý do:* Phổ biến, hệ sinh thái thư viện xử lý dữ liệu lớn, dễ dàng bàn giao và bảo trì cho đội ngũ kỹ sư nội bộ.
- **Xử lý PDF (`PyMuPDF`):** *Lý do:* Hoạt động hoàn toàn bằng thư viện C/Python, tốc độ render ảnh cực nhanh, không yêu cầu cài đặt phần mềm bên thứ 3 phức tạp (như Poppler) giúp việc deploy cực kỳ đơn giản.
- **Trí tuệ nhân tạo (`Google Gemini 2.5 Flash`):** *Lý do:* Khả năng phân tích hình ảnh (Vision) xuất sắc, hỗ trợ xuất JSON gốc (Native Structured Output) nên không cần phân tích chuỗi (regex parsing) rườm rà. Quan trọng nhất, chi phí cực kỳ tối ưu cho các bài toán xử lý số lượng lớn.
- **Giao diện & Review (`Streamlit`):** *Lý do:* Cho phép xây dựng nhanh công cụ quản trị (Dashboard) và giao diện duyệt chứng từ (Review UI) trực tiếp bằng Python mà không tốn tài nguyên thiết kế Frontend.
- **Lưu trữ (`SQLite`):** *Lý do:* Hoàn hảo cho mức độ PoC (zero-config, nhẹ nhàng, lưu dữ liệu tập trung 1 file). Cấu trúc bảng đã được thiết kế chuẩn mực, sẵn sàng migrate lên PostgreSQL/SQL Server khi triển khai Production.

## 2. Phân tích Chi phí (Cost Breakdown)
*Mô hình: Google Gemini 2.5 Flash. Bảng giá cập nhật ngày: 14/05/2026. Chi tiết tại: [Google AI Pricing](https://ai.google.dev/pricing)*

- **Báo giá API gốc:** $0.30 / 1 triệu input tokens và $2.50 / 1 triệu output tokens.
- **Chi phí trên mỗi chứng từ (Per-document Cost) & Dự toán:**
  - Đầu vào (50 ảnh/ngày): $50 \times 258 \, \text{tokens} \times (0,30 \, \text{USD} / 1.000.000) \approx 0,00387 \, \text{USD}$
  - Đầu ra (50 JSON/ngày): $50 \times 500 \, \text{tokens} \times (2,50 \, \text{USD} / 1.000.000) \approx 0,0625 \, \text{USD}$
  - **Tổng cộng 1 ngày:** $0,06637 \, \text{USD}$ (tương đương khoảng **1.700 VNĐ**).
  - **Tổng cộng 1 tháng (30 ngày):** Khoảng $2 \, \text{USD}$ (tương đương **50.000 VNĐ**).

*=> So với mức ngân sách 5.000.000 VNĐ/tháng mà công ty cho phép, chi phí API phần lõi chỉ chiếm **1%**, tạo ra khoảng trống tài chính cực lớn (headroom) dư dả để triển khai thêm hạ tầng Cloud Server hoặc lưu trữ.*

## 3. Xử lý các trường hợp ngoại lệ (Edge Cases)
- **Bản scan chất lượng kém/mờ (Low-quality scans):** Quá trình render PDF mặc định đẩy độ nét lên cao (400 DPI). Nếu chữ quá nhòe không thể đọc, prompt AI được cấu hình để trả về `null` thay vì đoán mò. Điều này sẽ kéo điểm tin cậy (Confidence Score) xuống và hệ thống lập tức dán cờ (flagged) chuyển sang bộ phận Review thủ công.
- **Ảo giác của AI (Hallucinations):** Rủi ro AI tự "bịa" ra dữ liệu được khống chế bởi 2 cơ chế: (1) Prompt ràng buộc AI chỉ sử dụng thông tin tìm thấy trên ảnh; (2) Cơ chế xác thực chéo toán học (Ví dụ: `Số lượng` × `Đơn giá` phải khớp với `Tổng tiền`). Nếu sai logic, hệ thống sẽ phát cảnh báo.
- **Giới hạn API (API Rate Limits):** Xử lý ngoại lệ với thư viện `tenacity`. Nếu gặp lỗi quá tải (ResourceExhausted), hệ thống sẽ tự động chờ theo cấp số nhân (Exponential Backoff) và thử lại. Giới hạn đồng thời (Concurrency Limits) cũng sẽ được cấu hình khi chạy Batch Processing.
- **Khuôn dạng văn bản không nhất quán:** Thay vì bóc tách text, việc dùng AI Vision giúp hệ thống "miễn nhiễm" với các thay đổi bất chợt trong form mẫu của nhà cung cấp (MSC, Maersk...). AI đọc dữ liệu dựa vào ngữ cảnh không gian thay vì tọa độ cố định.

## 4. Quản trị & Kiểm soát hệ thống (Management Control)
- **Cổng phê duyệt (Approval Gates / Human-in-the-loop):** Mọi trường dữ liệu đều có độ tin cậy. Những file có điểm tin cậy tổng thể dưới 90% (tùy chỉnh được) sẽ tự động bị chặn xuất Excel. Nhân viên chuyên trách bắt buộc phải truy cập giao diện Streamlit, kiểm tra ảnh chứng từ song song với kết quả, sửa lỗi và bấm "Phê duyệt" bằng tay.
- **Nhật ký truy vết (Audit Logs):** Mọi hành động chỉnh sửa của con người đều được lưu vết trong bảng `audit_logs` của Database. Quản lý có thể truy xuất thời gian, người thực hiện, thông tin nào bị đổi, giá trị cũ và mới là gì. Điều này đảm bảo tính minh bạch tuyệt đối trong vận hành.
- **Báo cáo trực quan (Dashboard):** Quản lý có một trang Dashboard theo dõi chỉ số hiệu suất thời gian thực: Tỷ lệ chứng từ được tự động hóa hoàn toàn (Automation Rate), số lượng chờ duyệt, và mức tiêu hao ngân sách Token.
