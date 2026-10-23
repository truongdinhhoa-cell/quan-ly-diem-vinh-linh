import streamlit as st
import requests
import json

def tao_nhan_xet_va_xep_diem(ten_hs, chuoi_diem_tho, tong_quan_lop=""):
    try:
        # 1. Lấy khóa từ mục Secrets trên Streamlit Cloud
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
        4. Không dùng các ký tự đánh dấu Markdown như dấu sao (**), dấu thăng (#) để tránh bị lộ ký tự rác khi dán vào Zalo. Hãy dùng chữ IN HOA kết hợp biểu tượng (📌, 📊, 💡, 🤝) cho các mục lớn.
        
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

        # Ưu tiên 1: Dùng SDK mới nhất google-genai (hỗ trợ trực tiếp khóa AQ...)
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            if response and response.text:
                return response.text
        except Exception:
            pass

        # Ưu tiên 2: Gọi trực tiếp REST API với thời gian chờ ngắn (15 giây) để không bị treo
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        # Thử phương thức 1: Header x-goog-api-key
        headers_key = {"Content-Type": "application/json", "x-goog-api-key": api_key}
        res = requests.post(url, headers=headers_key, data=json.dumps(payload), timeout=15)
        
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
            
        # Thử phương thức 2: Header Authorization Bearer cho Auth Key AQ...
        headers_bearer = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        res2 = requests.post(url, headers=headers_bearer, data=json.dumps(payload), timeout=15)
        
        if res2.status_code == 200:
            return res2.json()["candidates"][0]["content"]["parts"][0]["text"]

        return f"❌ Lỗi xác thực từ Google (Mã {res.status_code}): {res.text}"

    except Exception as e:
        return f"❌ Lỗi chi tiết: {str(e)}"
