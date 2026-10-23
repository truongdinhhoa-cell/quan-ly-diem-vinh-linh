import streamlit as st
import requests
import json
import time

def tao_nhan_xet_va_xep_diem(ten_hs, chuoi_diem_tho, tong_quan_lop=""):
    try:
        api_key = ""
        if "GEMINI_API_KEY" in st.secrets:
            api_key = str(st.secrets["GEMINI_API_KEY"]).strip()
        
        if not api_key:
            return "❌ Lỗi: Chưa tìm thấy GEMINI_API_KEY trong mục Secrets của Streamlit Cloud."

        prompt = f"""
        Bạn là một Giáo viên chủ nhiệm tận tâm của Trường THPT Vĩnh Linh. Dưới đây là dữ liệu điểm thực tế của học sinh {ten_hs}:
        {chuoi_diem_tho}
        
        Dữ liệu toàn lớp để so sánh:
        {tong_quan_lop}
        
        QUY TẮC TRÌNH BÀY BẮT BUỘC ĐỂ GỬI ZALO (TUYỆT ĐỐI TUÂN THỦ):
        1. TUYỆT ĐỐI KHÔNG kẻ bảng bằng dấu gạch đứng (|) và dấu gạch ngang (---) vì khi copy dán sang Zalo sẽ bị vỡ khung, xô lệch dòng.
        2. Trình bày điểm từng môn theo dạng danh sách xuống dòng rõ ràng, đẹp mắt như mẫu sau:
           • Toán học: TX1: 10,0 | TX2: 9,0
           • Ngữ văn: TX1: 6,0
           • Giáo dục thể chất: Đạt (Đ)
        3. Chỉ hiển thị đúng các cột điểm thực tế đang có (TX1, TX2...). Nếu dữ liệu chưa có chữ "GK:" hay "CK:" thì tuyệt đối không tự thêm vào.
        4. Không dùng các ký tự đánh dấu Markdown như dấu sao (**), dấu thăng (#). Hãy dùng chữ IN HOA kết hợp biểu tượng (📌, 📊, 💡, 🤝) cho các mục lớn.
        
        Nội dung báo cáo gồm 4 phần:
        📌 1. KẾT QUẢ HỌC TẬP CÁC MÔN CỦA EM {ten_hs.upper()}:
        (Liệt kê từng môn mỗi môn 1 dòng theo đúng mẫu ở quy tắc 2)
        
        📊 2. PHÂN TÍCH PHỔ ĐIỂM & VỊ THỨ TRONG LỚP:
        (Đánh giá mặt bằng chung của lớp và vị thứ tương đối của học sinh trong tập thể lớp)
        
        💡 3. ĐÁNH GIÁ LỰC HỌC & SỰ TIẾN BỘ:
        (Nhận xét các môn thế mạnh, các môn cần cố gắng thêm và sự thay đổi điểm số giữa các lần kiểm tra)
        
        🤝 4. LỜI NHẮN GỬI TỚI GIA ĐÌNH:
        (Lời nhắn ân cần, lịch sự của GVCN gửi phụ huynh)
        """

        list_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        headers_key = {"Content-Type": "application/json", "x-goog-api-key": api_key}
        try:
            # Tăng thời gian chờ quét mô hình lên 30 giây
            res_models = requests.get(list_url, headers=headers_key, timeout=30)
        except Exception:
            res_models = None
        
        if res_models and res_models.status_code in [401, 403]:
            headers_bearer = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            try:
                res_models = requests.get(list_url, headers=headers_bearer, timeout=30)
                active_headers = headers_bearer
            except Exception:
                active_headers = headers_bearer
        else:
            active_headers = headers_key

        danh_sach_models = []
        if res_models and res_models.status_code == 200:
            models_data = res_models.json().get("models", [])
            for m in models_data:
                if "generateContent" in m.get("supportedGenerationMethods", []) and "gemini" in m.get("name", "").lower():
                    danh_sach_models.append(m["name"].replace("models/", ""))
        
        if danh_sach_models:
            flash_models = [m for m in danh_sach_models if "flash" in m.lower()]
            danh_sach_models = flash_models + [m for m in danh_sach_models if m not in flash_models]
        else:
            danh_sach_models = ["gemini-1.5-flash", "gemini-2.5-flash"]

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        nhat_ky_loi = []

        for m_name in danh_sach_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent"
            try:
                # BƯỚC QUAN TRỌNG: Tăng thời gian chờ AI suy nghĩ lên 60 giây
                res = requests.post(url, headers=active_headers, data=json.dumps(payload), timeout=60)
                
                if res.status_code == 200:
                    return res.json()["candidates"][0]["content"]["parts"][0]["text"]
                
                nhat_ky_loi.append(f"[{m_name}]: Mã {res.status_code}")
            except requests.exceptions.Timeout:
                nhat_ky_loi.append(f"[{m_name}]: Quá 60 giây không phản hồi")
            except Exception as err:
                nhat_ky_loi.append(f"[{m_name}]: Lỗi mạng")
                
            time.sleep(0.5)

        return f"⚠️ Hệ thống đang phản hồi chậm hoặc có lỗi. Chi tiết: {', '.join(nhat_ky_loi)}"

    except Exception as e:
        return f"❌ Lỗi hệ thống: {str(e)}"
