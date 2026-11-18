# Gợi ý thuyết trình và hỏi đáp

## Trình bày khoảng 1 phút

“Nhóm xây dựng hệ thống phân tích văn bản tiếng Việt để cảnh báo nội dung có khả năng là tin nhắn rác/lừa đảo. Hệ thống gồm một mô hình Linear SVM huấn luyện từ SMS tiếng Việt đã ẩn danh, một bộ quy tắc minh bạch để chỉ ra các dấu hiệu như yêu cầu OTP, liên kết, chuyển tiền hay hứa thưởng, và giao diện web để người dùng dán nội dung cần kiểm tra. Nhóm chọn cấu hình bằng cross-validation trên tập huấn luyện và đánh giá một lần trên tập test riêng. Trên 597 SMS kiểm tra, mô hình đạt macro F1 0,914; recall lớp rác/lừa đảo 0,956 và precision 0,812. Kết quả cho thấy mô hình bắt được nhiều trường hợp rác/lừa đảo nhưng vẫn có cảnh báo nhầm. Dữ liệu hiện chỉ kiểm định cho SMS; Zalo/email là hướng mở rộng cần bộ dữ liệu riêng.”

## Câu hỏi có thể được hỏi

### Vì sao dùng Linear SVM và TF-IDF?

Đây là mô hình cơ sở mạnh cho phân loại văn bản, huấn luyện nhanh trên máy cá nhân, dễ tái lập và có thể xem các đặc trưng tuyến tính. N-gram ký tự có thể hữu ích với viết tắt, lỗi chính tả và biến thể cách viết. Đây không phải khẳng định SVM luôn tốt hơn Transformer; có thể so sánh PhoBERT trong giai đoạn tiếp theo nếu đủ thời gian/tài nguyên.

### Vì sao không chỉ dùng accuracy?

Accuracy có thể che việc mô hình bỏ sót lớp hiếm. Nhóm báo cáo recall, precision và macro F1. Với tập test hiện tại, mô hình bắt được 151/158 mẫu lừa đảo nhưng cảnh báo nhầm 35 mẫu bình thường.

### Điểm SVM 0,8 có nghĩa là 80% nguy hiểm không?

Không. Đó là decision margin có dấu, không phải xác suất. Giao diện nói rõ điểm này và không hiển thị như phần trăm tin cậy.

### Vì sao giao diện nhận Zalo/email nhưng kết quả chưa được xác nhận?

Mô hình có thể nhận văn bản thuần từ các nguồn đó, nhưng bộ dữ liệu đánh giá chỉ gồm SMS. Khác biệt về độ dài, ngữ cảnh và mẫu hợp lệ có thể làm hiệu quả thay đổi. Cần có dữ liệu email/Zalo được thu thập, ẩn danh, gán nhãn và chia tập độc lập trước khi tuyên bố hỗ trợ.

### Hệ thống có thể tự kết luận ngân hàng lừa đảo không?

Không. Mô hình đưa ra cảnh báo tham khảo dựa trên nội dung, không xác minh người gửi, tên miền hoặc giao dịch. Người dùng nên tự mở kênh chính thức của ngân hàng để xác minh.

### Hướng phát triển?

Thu thập thêm dữ liệu có quyền sử dụng cho email và Zalo; đánh giá theo thời gian và từng kênh; so sánh PhoBERT với mô hình cơ sở; điều chỉnh ngưỡng theo chi phí bỏ sót/cảnh báo nhầm; kiểm tra độ ổn định với viết không dấu và biến thể chính tả.
