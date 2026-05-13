"""
AGO Fruit - Web Review UI (Streamlit)
Giao diện cho nhân viên review kết quả AI và xuất Excel.
"""

import streamlit as st
import json
from pathlib import Path
from PIL import Image
import io

from config import OUTPUT_DIR, SAMPLE_INPUT_DIR
from extractor import PDFProcessor, LLMExtractor, Validator
from database import DatabaseManager
from export import ExcelWriter
from extractor.schemas import ExtractionResult, DocumentType

# ── Cấu hình trang ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AGO Fruit - AI Document Automation",
    page_icon="🍏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho giao diện premium
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
    </style>
""", unsafe_allow_html=True) # FIXED: unsafe_allow_html=True

# ── Khởi tạo service ────────────────────────────────────────────────────────
@st.cache_resource
def get_services():
    return {
        "processor": PDFProcessor(),
        "extractor": LLMExtractor(),
        "validator": Validator(),
        "db": DatabaseManager(),
        "writer": ExcelWriter()
    }

services = get_services()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/apple.png", width=80)
    st.title("AGO Fruit IT")
    st.markdown("---")
    menu = st.radio("Chức năng", ["Trích xuất mới", "Lịch sử & Review", "Thống kê & Chi phí"])
    
    st.markdown("---")
    st.info("💡 **Mẹo:** Gemini 2.5 Flash xử lý tốt cả bản scan tay.")

# ── Main Logic ──────────────────────────────────────────────────────────────

if menu == "Trích xuất mới":
    st.header("🚀 Trích xuất chứng từ mới")
    
    uploaded_file = st.file_uploader("Kéo thả file PDF chứng từ vào đây", type=["pdf"])
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        
        # Lưu file tạm để xử lý
        temp_path = Path("temp_upload.pdf")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with col1:
            st.subheader("📄 Xem trước")
            try:
                images = services["processor"].extract_images(temp_path)
                st.image(images[0], caption="Trang 1 của chứng từ", use_column_width=True)
            except Exception as e:
                st.error(f"Lỗi hiển thị PDF: {str(e)}")
            
        with col2:
            st.subheader("🤖 Kết quả AI")
            if st.button("Bắt đầu trích xuất với Gemini AI"):
                with st.spinner("Đang phân tích chứng từ..."):
                    try:
                        raw_data = services["extractor"].extract(images, filename=uploaded_file.name)
                        result = services["validator"].validate(raw_data, filename=uploaded_file.name)
                        
                        st.session_state.current_result = result
                        services["db"].save_extraction(result)
                        st.success("Trích xuất xong!")
                    except Exception as e:
                        st.error(f"Lỗi trích xuất: {str(e)}")

            if "current_result" in st.session_state:
                res = st.session_state.current_result
                
                conf_color = "confidence-high" if res.overall_confidence >= 0.7 else "confidence-low"
                st.markdown(f"Độ tin cậy tổng thể: <span class='{conf_color}'>{res.overall_confidence*100:.1f}%</span>", unsafe_allow_html=True)
                
                with st.form("review_form"):
                    st.write(f"Loại chứng từ: **{res.document_type.value}**")
                    edited_data = st.text_area("Dữ liệu JSON", value=json.dumps(res.data, indent=2, ensure_ascii=False), height=400)
                    
                    if st.form_submit_button("Xác nhận & Lưu"):
                        try:
                            final_json = json.loads(edited_data)
                            last_id = services["db"].get_all_documents()[0]['id']
                            services["db"].update_document_data(last_id, final_json)
                            st.balloons()
                            st.success("Đã duyệt và lưu vào hệ thống!")
                        except:
                            st.error("Định dạng JSON không hợp lệ.")

elif menu == "Lịch sử & Review":
    st.header("📚 Lịch sử trích xuất")
    docs = services["db"].get_all_documents()
    
    if not docs:
        st.info("Chưa có dữ liệu trích xuất.")
    else:
        for d in docs:
            with st.expander(f"📄 {d['filename']} - {d['document_type']} ({d['upload_time']})"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.json(json.loads(d['raw_data_json']))
                with c2:
                    st.write(f"**Trạng thái:** {d['status']}")
                    st.write(f"**Độ tin cậy:** {d['overall_confidence']*100:.1f}%")
                    if st.button("Xem Audit Log", key=f"log_{d['id']}"):
                        logs = services["db"].get_audit_logs(d['id'])
                        st.table(logs)

        if st.button("🎯 Xuất toàn bộ ra Excel"):
            results_to_export = []
            for d in docs:
                results_to_export.append(ExtractionResult(
                    filename=d['filename'],
                    document_type=DocumentType(d['document_type']),
                    overall_confidence=d['overall_confidence'],
                    needs_review=(d['status'] == 'pending'),
                    data=json.loads(d['raw_data_json']),
                    token_usage={'input': d['token_usage_input'], 'output': d['token_usage_output']}
                ))
            
            output_path = OUTPUT_DIR / "ago_report.xlsx"
            services["writer"].write_results(results_to_export, output_path)
            
            with open(output_path, "rb") as f:
                st.download_button("📥 Tải file Excel", f, file_name="ago_fruit_report.xlsx")

elif menu == "Thống kê & Chi phí":
    st.header("📊 Thống kê vận hành")
    docs = services["db"].get_all_documents()
    
    total_docs = len(docs)
    if total_docs > 0:
        avg_conf = sum(d['overall_confidence'] for d in docs) / total_docs
        total_input = sum(d['token_usage_input'] for d in docs)
        total_output = sum(d['token_usage_output'] for d in docs)
        cost_vnd = ((total_input * 0.3 / 1000000) + (total_output * 2.5 / 1000000)) * 25000

        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng số chứng từ", total_docs)
        m2.metric("Độ chính xác TB", f"{avg_conf*100:.1f}%")
        m3.metric("Tổng chi phí dự tính", f"{cost_vnd:,.0f} ₫")
        
        st.markdown("---")
        st.subheader("So sánh với Budget hàng tháng")
        st.progress(min(cost_vnd / 5000000, 1.0))
        st.write(f"Đã sử dụng **{cost_vnd:,.0f} ₫** / 5,000,000 ₫")
    else:
        st.info("Chưa có dữ liệu để thống kê.")
