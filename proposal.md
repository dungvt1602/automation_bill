# Đề xuất Giải pháp Tự động hóa Chứng từ - AGO Fruit 🍎

## 1. Tổng quan
Đề xuất này mô tả hệ thống PoC (Proof of Concept) sử dụng trí tuệ nhân tạo thị giác (Vision-AI) để tự động hóa việc trích xuất dữ liệu từ các chứng từ xuất nhập khẩu (Invoice, Packing List, Bill of Lading, v.v.).

## 2. Kiến trúc Kỹ thuật
Hệ thống được xây dựng trên nền tảng Python với các thành phần chính:
- **Xử lý hình ảnh:** Chuyển đổi PDF sang ảnh chất lượng cao (400 DPI) bằng PyMuPDF.
- **Trí tuệ nhân tạo:** Sử dụng **Gemini 1.5 Flash** để đọc và hiểu nội dung chứng từ.
- **Xác thực dữ liệu:** Cơ chế kiểm tra chéo (ví dụ: Tổng tiền = Đơn giá x Số lượng) để đảm bảo tính chính xác.
- **Lưu trữ:** SQLite lưu lại lịch sử trích xuất và nhật ký thay đổi (Audit Log).
- **Giao diện:** Streamlit Web App cho phép nhân viên review và chỉnh sửa dữ liệu dễ dàng.

## 3. Ước tính Chi phí vận hành
Dựa trên khối lượng 3,000 chứng từ mỗi tháng:
- **Mô hình AI (Gemini Flash):** ~500,000 VND/tháng.
- **Hạ tầng (Cloud/Server):** ~1,000,000 VND/tháng (có thể chạy trên máy nội bộ để tiết kiệm).
- **Tổng cộng:** Khoảng **1.5 - 2 triệu VND/tháng**, thấp hơn nhiều so với ngân sách 5 triệu VND/tháng của công ty.

## 4. Lợi ích mang lại
- **Tốc độ:** Xử lý 1 chứng từ trong chưa đầy 10 giây.
- **Độ chính xác:** AI có khả năng đọc hiểu các bảng biểu phức tạp của hãng tàu (MSC, Maersk, v.v.).
- **Giảm sai sót:** Hệ thống tự động cảnh báo khi dữ liệu giữa các chứng từ không khớp nhau.
