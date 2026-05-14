# Báo cáo Trợ lý AI (AGO Fruit Automation) 🤖

## Mục tiêu dự án
Xây dựng hệ thống tự động trích xuất 5 loại chứng từ chính cho AGO Fruit sử dụng Gemini Vision.

## Nhật ký thực hiện (Log)
- **Cấu trúc dữ liệu:** Đã hoàn thiện 5 Schema chuẩn cho Invoice, Packing List, BL, Phyto, CO.
- **Xử lý PDF:** Đã tối ưu hóa việc chuyển đổi sang ảnh 400 DPI để AI đọc rõ chữ nhất.
- **AI Engine:** Đã cấu hình Gemini 1.5 Flash với chiến thuật trích xuất 2 bước (Detection -> Extraction).
- **Lưu trữ & Xuất bản:** Đã hoàn thiện database SQLite và tính năng xuất Excel "Data Entry" (phẳng hóa dữ liệu để dễ nhập liệu).
- **Giao diện:** Hoàn thiện Streamlit App với tính năng Preview và Dashboard chi phí.

## Ghi chú kỹ thuật
- **Model:** `gemini-1.5-flash` được chọn vì cân bằng tốt nhất giữa chi phí và tốc độ.
- **Xác thực:** Đã thêm cơ chế tính điểm tin cậy (Confidence Score) trên từng trường dữ liệu.
- **Dọn dẹp:** Đã tạo bộ công cụ `tools/` để reset và kiểm tra hệ thống nhanh chóng.
