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

        # BƯỚC ĐỘT PHÁ: Tự động truy vấn danh sách các mô hình mà API Key của thầy được phép dùng
        list_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        # Xác định phương thức xác thực chuẩn
        headers_key = {"Content-Type": "application/json", "x-goog-api-key": api_key}
        res_models = requests.get(list_url, headers=headers_key, timeout=10)
        
        if res_models.status_code in [401, 403]:
            headers_bearer = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            res_models = requests.get(list_url, headers=headers_bearer, timeout=10)
            active_headers = headers_bearer
        else:
            active_headers = headers_key

        danh_sach_models = []
        if res_models.status_code == 200:
            models_data = res_models.json().get("models", [])
            for m in models_data:
                # Chỉ lọc lấy các mô hình Gemini hỗ trợ tạo văn bản
                if "generateContent" in m.get("supportedGenerationMethods", []) and "gemini" in m.get("name", "").lower():
                    danh_sach_models.append(m["name"].replace("models/", ""))
        
        # Sắp xếp ưu tiên các mô hình 'flash' (nhanh nhất) lên đầu danh sách chạy
        if danh_sach_models:
            flash_models = [m for m in danh_sach_models if "flash" in m.lower()]
            danh_sach_models = flash_models + [m for m in danh_sach_models if m not in flash_models]
        else:
            # Danh sách dự phòng an toàn cuối cùng
            danh_sach_models = ["gemini-3.8-flash", "gemini-3.1-pro-preview", "gemini-2.5-flash", "gemini-1.5-flash"]

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        nhat_ky_loi = []

        # Tự động rà quét và chạy mô hình phù hợp nhất
        for m_name in danh_sach_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent"
            res = requests.post(url, headers=active_headers, data=json.dumps(payload), timeout=20)
            
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            nhat_ky_loi.append(f"[{m_name}]: Mã {res.status_code}")
            time.sleep(0.5)

        return f"⚠️ Tài khoản Google của thầy hiện không cấp quyền truy cập vào bất kỳ mô hình nào, hoặc đã hết hạn mức. Chi tiết các thử nghiệm: {', '.join(nhat_ky_loi)}"

    except Exception as e:
        return f"❌ Lỗi hệ thống: {str(e)}"
