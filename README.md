# Nhận diện tin nhắn lừa đảo tiếng Việt

Ứng dụng nghiên cứu hoàn chỉnh gồm dữ liệu SMS công khai, quy trình chọn và huấn luyện mô hình, báo cáo đánh giá độc lập và giao diện Streamlit. Mô hình hiện tại giải bài toán nhị phân **bình thường (0) / rác-lừa đảo (1)** trên SMS tiếng Việt. Chưa có dữ liệu kiểm định tương ứng cho Zalo/email, nên không khẳng định chất lượng trên các nguồn đó.

## Chạy ứng dụng

Yêu cầu Python 3.11–3.12.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python train.py
streamlit run app.py
```

Mở URL Streamlit hiện trong terminal. Mô hình đã huấn luyện được lưu tại `models/`; đánh giá và dự đoán lưu tại `reports/`.

## Thành phần

- `data/train.csv`, `data/test.csv`: tách đúng theo bản phát hành của bộ dữ liệu; không gộp test vào train.
- `train.py`: chọn cấu hình bằng stratified 5-fold cross-validation chỉ trên train; chọn ngưỡng theo dự đoán ngoài fold trên train (mục tiêu precision lừa đảo ≥ 0,90), rồi đánh giá trên test.
- `app.py`: giao diện ba mục Phân tích/Tổng quan/Hướng dẫn; đánh dấu dấu hiệu trong nội dung, giải thích hai chiều, hướng dẫn an toàn, ví dụ thử nhanh và nút xóa. Lịch sử tắt mặc định; mẫu phản hồi sai phải được kiểm tra/xác nhận, qua hàng chờ cục bộ và được gán nhãn thủ công trước khi xuất CSV kèm kênh nguồn.
- `reports/evaluation.json`: số liệu đánh giá và cấu hình đã chọn.
- `proposal.md`: đề cương có giới hạn phạm vi cập nhật theo dữ liệu thực tế.

## Diễn giải kết quả

Mô hình là Linear SVM dùng TF-IDF từ và ký tự. Điểm hiển thị là khoảng cách có dấu của bộ phân loại, **không phải xác suất**. Ngưỡng được chọn trên dự đoán chéo của tập huấn luyện theo mục tiêu precision, nhưng precision trên test chỉ đạt 0,830; ngưỡng không đảm bảo đạt mục tiêu khi gặp dữ liệu khác. Trên test, mô hình gắn nhầm 31 tin bình thường và bỏ sót 7 tin lừa đảo. Các cụm từ giải thích là đặc trưng tuyến tính liên quan đến điểm dự đoán, không phải bằng chứng xác thực một vụ lừa đảo. Cần xem recall và precision của lớp lừa đảo cùng macro F1, không chỉ accuracy.

## Dữ liệu và ghi công

Nguồn: Tran et al., *Vietnamese SMS Dataset with Quality Assurance*, Hugging Face. Bộ phát hành mô tả SMS tiếng Việt đã ẩn danh, nhãn 0/1, giấy phép CC BY 4.0; tệp train có 2.394 mẫu và test có 597 mẫu. Xem `DATASET.md` để biết nguồn, ghi công và điều kiện giấy phép. Dữ liệu không chứa SMS từ tài khoản của người dùng dự án.

## Giới hạn và an toàn

- Kết quả phản ánh một bộ SMS và một lần đánh giá; không đại diện mọi chiến thuật mới, tin Zalo hoặc email.
- Nhãn “bình thường” không đảm bảo an toàn. Tin nhắn giả mạo có thể đổi cách viết, viết không dấu hoặc dùng hình ảnh mà mô hình văn bản không đọc được.
- Chỉ dán dữ liệu đã ẩn danh. Ứng dụng không đọc SMS/Zalo/email tự động và không gửi nội dung đến ngân hàng.
- Bộ đếm, lịch sử bật theo lựa chọn và hàng chờ duyệt được lưu cục bộ trong `reports/feedback.sqlite`; tệp này được loại khỏi Git. Mẫu trong hàng chờ chưa tự động đưa vào train.
- Khi nghi ngờ, không bấm liên kết; tự mở ứng dụng/website chính thức hoặc gọi số lấy từ nguồn chính thức.
