import streamlit as st
import pandas as pd
import pdfplumber
import time
import re
import os
from ai_reviewer import tao_nhan_xet_va_xep_diem

st.set_page_config(page_title="Quản lý Điểm GVCN Trường THPT Vĩnh Linh", layout="wide")

# --- CẤU HÌNH GIAO DIỆN MÀU XANH FACEBOOK & FONT CHỮ ĐỎ DỄ NHÌN ---
st.markdown("""
    <style>
    /* Nền tổng thể màu xanh nhạt dịu mắt kiểu Facebook */
    .stApp {
        background-color: #E7F3FF;
    }
    
    /* Thanh tiêu đề màu xanh Facebook (#1877F2) */
    .fb-header {
        background: linear-gradient(90deg, #1877F2 0%, #0A58CA 100%);
        padding: 18px 25px;
        border-radius: 12px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(24, 119, 242, 0.25);
        border: 2px solid #ffffff;
    }
    
    /* Tiêu đề chính trên nền xanh (dùng màu trắng kem pha đỏ/vàng hoặc thẻ trắng chữ đỏ để nổi bật) */
    .fb-title-box {
        background-color: #ffffff;
        padding: 15px 20px;
        border-radius: 10px;
        border-left: 8px solid #1877F2;
        border-right: 8px solid #1877F2;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        text-align: center;
        margin-bottom: 20px;
    }
    
    .fb-title-box h1 {
        color: #D32F2F !important; /* Màu đỏ tươi thân thiện, dễ nhìn */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
        font-size: 32px;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Đổi font chữ các tiêu đề mục và nội dung sang màu đỏ đậm dễ đọc */
    h1, h2, h3, h4, p, label, .stMarkdown {
        color: #C62828 !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Khung upload file và các khối dữ liệu nổi bật trên nền xanh */
    .stFileUploader {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 2px dashed #1877F2;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }

    /* Bo góc đẹp mắt cho ảnh Banner */
    .stImage img {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border: 3px solid #1877F2;
    }
    
    /* Đường kẻ ngang màu xanh Facebook */
    hr {
        border-top: 2px solid #1877F2 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1. HIỂN THỊ BANNER TRƯỜNG THPT VĨNH LINH Ở ĐẦU TRANG
banner_found = False
for ten_file_anh in ["banner.jpg", "banner.png", "banner.jpeg", "image_a0f45a.jpg"]:
    if os.path.exists(ten_file_anh):
        st.image(ten_file_anh, use_container_width=True)
        banner_found = True
        break

if not banner_found:
    st.info("💡 Mẹo nhỏ: Thầy hãy lưu bức ảnh Banner của trường vào cùng thư mục chứa code và đặt tên là **banner.jpg** để ảnh tự động hiển thị rực rỡ ở ngay đầu trang nhé!")

# 2. TIÊU ĐỀ CHÍNH THEO YÊU CẦU
st.markdown("""
    <div class="fb-title-box">
        <h1>🎓 Quản lý Điểm GVCN Trường THPT Vĩnh Linh</h1>
    </div>
""", unsafe_allow_html=True)

# 3. ĐỔI THÀNH MỤC 1 THEO YÊU CẦU
st.write("### 📂 MỤC 1: Tải lên Sổ Điểm Tổng Hợp (PDF vnEdu 30 trang)")
file_pdf = st.file_uploader("Chọn file PDF sổ điểm của lớp", type=["pdf"], key="pdf_don_le")

# --- GIỮ NGUYÊN 100% CẤU TRÚC XỬ LÝ DỮ LIỆU ĐÃ CHẠY ỔN ĐỊNH ---
if file_pdf:
    with st.spinner("Đang bóc tách dữ liệu chuẩn xác từng ô điểm..."):
        
        danh_sach_hoc_sinh = []
        du_lieu_diem = {}
        
        with pdfplumber.open(file_pdf) as pdf:
            # 1. Quét danh sách học sinh giữ nguyên thứ tự gốc từ 1 -> 46 trong sổ điểm
            for page in pdf.pages:
                text = page.extract_text()
                if text and "Môn " in text:
                    bang = page.extract_table()
                    if bang:
                        for dong in bang:
                            if len(dong) >= 2 and dong[0] and dong[1]:
                                stt_raw = str(dong[0]).replace('.', '').strip()
                                ten_raw = str(dong[1]).strip()
                                stt_lines = [s.strip() for s in stt_raw.split('\n') if s.strip().isdigit()]
                                ten_lines = [t.strip() for t in ten_raw.split('\n') if t.strip() and "họ và tên" not in t.lower()]
                                
                                if stt_lines and len(stt_lines) == len(ten_lines):
                                    for t in ten_lines:
                                        if t not in danh_sach_hoc_sinh:
                                            danh_sach_hoc_sinh.append(t)
                                elif stt_raw.isdigit() and ten_raw and "họ và tên" not in ten_raw.lower():
                                    ten_clean = ten_raw.replace('\n', ' ').strip()
                                    if ten_clean not in danh_sach_hoc_sinh:
                                        danh_sach_hoc_sinh.append(ten_clean)
                    if len(danh_sach_hoc_sinh) >= 40:
                        break

            # Dự phòng nếu chưa lấy được từ bảng điểm thì quét Sơ yếu lý lịch
            if not danh_sach_hoc_sinh:
                for page in pdf.pages[:6]:
                    text = page.extract_text()
                    if text and "SƠ YẾU LÝ LỊCH HỌC SINH" in text:
                        bang = page.extract_table()
                        if bang:
                            for dong in bang:
                                if len(dong) >= 2 and dong[1]:
                                    for ten in str(dong[1]).split('\n'):
                                        ten = ten.strip()
                                        if ten and "họ và tên" not in ten.lower() and not ten.isdigit():
                                            if ten not in danh_sach_hoc_sinh:
                                                danh_sach_hoc_sinh.append(ten)

            # 2. Quét điểm từng môn
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                
                mon_hien_tai = ""
                for line in text.split('\n'):
                    if line.startswith("Môn "):
                        mon_hien_tai = line.split("(")[0].replace("Môn ", "").strip()
                        break
                
                if mon_hien_tai:
                    bang = page.extract_table()
                    if bang:
                        col_hs = 1
                        col_tx = 2
                        col_gk = None
                        col_ck = None
                        
                        for i, dong in enumerate(bang[:4]):
                            for j, cell in enumerate(dong):
                                if not cell: continue
                                val = str(cell).replace('\n', ' ').strip().lower()
                                if "họ và tên" in val: 
                                    col_hs = j
                                elif "ddgtx" in val or "đđgtx" in val or "thường xuyên" in val: 
                                    col_tx = j
                                elif "ddggk" in val or "đđggk" in val or ("giữa kì" in val and "thường xuyên" not in val): 
                                    col_gk = j
                                elif "ddgck" in val or "đđgck" in val or ("cuối kì" in val and "thường xuyên" not in val): 
                                    col_ck = j

                        if col_gk is None or col_gk <= col_tx:
                            so_cot_bang = max(len(r) for r in bang[:6]) if bang else 0
                            if so_cot_bang >= 8:
                                col_gk = col_tx + 4
                                col_ck = col_tx + 5
                            else:
                                col_gk = col_tx + 1
                                col_ck = col_tx + 2

                        for dong in bang:
                            if len(dong) > col_hs:
                                ten_hs_pdf = str(dong[col_hs]).replace('\n', ' ').strip()
                                hs_matched = ""
                                for ten_hs in danh_sach_hoc_sinh:
                                    if ten_hs in ten_hs_pdf:
                                        hs_matched = ten_hs
                                        break
                                
                                if hs_matched:
                                    tx_list = []
                                    end_tx = min(col_gk, len(dong))
                                    for c in range(col_tx, end_tx):
                                        cell_val = str(dong[c]).strip() if dong[c] is not None else ""
                                        if cell_val and cell_val.lower() not in ['none', '-', '', 'nan']:
                                            for item in cell_val.replace('\n', ' ').split():
                                                item_clean = item.strip()
                                                if item_clean and item_clean != '-':
                                                    if item_clean.upper() == 'D':
                                                        item_clean = 'Đ'
                                                    tx_list.append(item_clean)
                                    
                                    gk_val = ""
                                    if col_gk < len(dong) and dong[col_gk] is not None:
                                        v = str(dong[col_gk]).replace('\n', ' ').strip()
                                        if v and v.lower() not in ['none', '-', '', 'nan']:
                                            gk_val = 'Đ' if v.upper() == 'D' else v
                                            
                                    ck_val = ""
                                    if col_ck and col_ck < len(dong) and dong[col_ck] is not None:
                                        v = str(dong[col_ck]).replace('\n', ' ').strip()
                                        if v and v.lower() not in ['none', '-', '', 'nan']:
                                            ck_val = 'Đ' if v.upper() == 'D' else v
                                    
                                    diem_format = []
                                    if tx_list:
                                        tx_str = ", ".join([f"TX{idx+1}: {d}" for idx, d in enumerate(tx_list)])
                                        diem_format.append(tx_str)
                                    if gk_val:
                                        diem_format.append(f"GK: {gk_val}")
                                    if ck_val:
                                        diem_format.append(f"CK: {ck_val}")
                                        
                                    if diem_format:
                                        chuoi_mon = f"{mon_hien_tai}: " + " | ".join(diem_format)
                                        if hs_matched not in du_lieu_diem:
                                            du_lieu_diem[hs_matched] = []
                                        du_lieu_diem[hs_matched].append(chuoi_mon)

        # 3. Hiển thị bảng kết quả có cột STT bên trái và nút Copy nhanh bên phải
        danh_sach_hs_co_diem = []
        st.success(f"🎉 Đã quét thành công dữ liệu của {len(danh_sach_hoc_sinh)} học sinh theo đúng thứ tự Sổ điểm!")
        
        st.write("📋 **Bảng dữ liệu kết quả học tập toàn lớp (Bấm biểu tượng Copy ở góc phải mỗi ô điểm để dán ngay vào Zalo):**")
        
        col_title_stt, col_title_ten, col_title_diem = st.columns([0.8, 2.5, 6.7])
        col_title_stt.markdown("**STT**")
        col_title_ten.markdown("**Tên Học Sinh**")
        col_title_diem.markdown("**Tổng hợp Điểm (Chi tiết từng môn - Có nút Copy góc phải)**")
        st.divider()

        for idx, ten in enumerate(danh_sach_hoc_sinh, start=1):
            diem_gom_duoc = du_lieu_diem.get(ten, [])
            if diem_gom_duoc:
                danh_sach_hs_co_diem.append(ten)
                ban_in_zalo = f"📌 KẾT QUẢ HỌC TẬP CỦA EM: {ten.upper()}\n" + "\n".join([f"• {m}" for m in diem_gom_duoc])
            else:
                ban_in_zalo = "Không có dữ liệu điểm"
            
            c_stt, c_ten, c_diem = st.columns([0.8, 2.5, 6.7])
            with c_stt:
                st.markdown(f"**{idx}**")
            with c_ten:
                st.markdown(f"**{ten}**")
            with c_diem:
                st.code(ban_in_zalo, language="text")

        # --- PHÂN TÍCH CHUYÊN SÂU & XẾP HẠNG ---
        st.write("---")
        st.write("📊 **PHÂN TÍCH CHUYÊN SÂU & ĐÁNH GIÁ LỰC HỌC TỪNG EM**")
        
        hoc_sinh_xem = st.selectbox("Chọn học sinh để phân tích phổ điểm, vị thứ và lực học:", options=danh_sach_hs_co_diem)
        
        if hoc_sinh_xem:
            diem_cua_hs = "\n".join(du_lieu_diem.get(hoc_sinh_xem, []))
            
            du_lieu_toan_lop = []
            for hs, ds_diem in du_lieu_diem.items():
                du_lieu_toan_lop.append(f"- {hs}: {'; '.join(ds_diem)}")
            tong_quan_chung = f"Sĩ số: {len(danh_sach_hs_co_diem)} học sinh.\nBảng điểm toàn lớp:\n" + "\n".join(du_lieu_toan_lop)
            
            with st.spinner(f"Đang nhờ AI phân tích phổ điểm và vị thứ cho em {hoc_sinh_xem}..."):
                nhan_xet_chuyen_sau = tao_nhan_xet_va_xep_diem(hoc_sinh_xem, diem_cua_hs, tong_quan_chung)
            
            st.info(f"💡 **Báo cáo đánh giá chi tiết của em {hoc_sinh_xem}:**")
            st.write(nhan_xet_chuyen_sau)
            
            # --- NÚT SAO CHÉP NHANH BÁO CÁO AI ---
            st.write("📋 **Sao chép nội dung báo cáo nhận xét:**")
            st.code(nhan_xet_chuyen_sau, language="text")
            st.caption("💡 *Thầy có thể bấm vào biểu tượng Copy ở góc trên bên phải khung văn bản trên để sao chép toàn bộ kết quả một cách nhanh chóng!*")