import google.generativeai as genai

def tao_nhan_xet_va_xep_diem(ten_hs, chuoi_diem_tho, tong_quan_lop=""):
    try:
        # THẦY GIỮ NGUYÊN API KEY CỦA THẦY Ở DÒNG DƯỚI ĐÂY:
        genai.configure(api_key="AQ.Ab8RN6KE9vuz0mYigZOt3Yz0VMDlV0v934UXZmZulPAVfxfF6Q")
        
        model_name = 'gemini-pro'
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_name = m.name
                break
        
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Bạn là một Giáo viên chủ nhiệm tận tâm. Dưới đây là dữ liệu điểm thực tế của học sinh {ten_hs}:
        {chuoi_diem_tho}
        
        Dữ liệu toàn lớp để so sánh:
        {tong_quan_lop}
        
        QUY TẮC TRÌNH BÀY BẮT BUỘC ĐỂ GỬI ZALO (TUYỆT ĐỐI TUÂN THỦ):
        1. TUYỆT ĐỐI KHÔNG kẻ bảng bằng dấu gạch đứng (|) và dấu gạch ngang (---) vì khi copy dán sang Zalo sẽ bị vỡ khung, xô lệch dòng.
        2. Trình bày điểm từng môn theo dạng danh sách xuống dòng rõ ràng, đẹp mắt như mẫu sau:
           • Toán học: TX1: 10,0 | TX2: 9,0
           • Ngữ văn: TX1: 6,0
           • Tiếng Anh: TX1: 10,0
           • Giáo dục thể chất: Đạt (Đ)
        3. Chỉ hiển thị đúng các cột điểm thực tế đang có (TX1, TX2...). Nếu dữ liệu chưa có chữ "GK:" hay "CK:" thì tuyệt đối không tự thêm vào.
        4. Không dùng các ký tự đánh dấu Markdown như dấu sao (**), dấu thăng (#) để tránh bị lộ ký tự rác khi dán vào Zalo. Hãy dùng chữ IN HOA kết hợp biểu tượng (📌, 📊, 💡, 🤝) cho các mục lớn.
        
        Nội dung báo cáo gồm 4 phần:
        📌 1. KẾT QUẢ HỌC TẬP CÁC MÔN CỦA EM {ten_hs.upper()}:
        (Liệt kê từng môn mỗi môn 1 dòng theo đúng mẫu ở quy tắc 2)
        
        📊 2. PHÂN TÍCH PHỔ ĐIỂM & VỊ THỨ TRONG LỚP:
        (Đánh giá mặt bằng chung của lớp và vị thứ tương đối của học sinh trong tập thể 46 em)
        
        💡 3. ĐÁNH GIÁ LỰC HỌC & SỰ TIẾN BỘ:
        (Nhận xét các môn thế mạnh, các môn cần cố gắng thêm và sự thay đổi điểm số giữa các lần kiểm tra)
        
        🤝 4. LỜI NHẮN GỬI TỚI GIA ĐÌNH:
        (Lời nhắn ân cần, lịch sự của GVCN gửi phụ huynh)
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ Lỗi chi tiết: {str(e)}"