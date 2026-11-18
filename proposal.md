# ĐỀ CƯƠNG ĐỀ TÀI (BẢN DỰ THẢO)

## 1. Tên đề tài
**Xây dựng hệ thống phát hiện và cảnh báo tin nhắn lừa đảo tiếng Việt trên SMS, Zalo và Email**

## 2. Lý do chọn đề tài
Các tin nhắn giả mạo ngân hàng, thông báo trúng thưởng, đe dọa khóa tài khoản hoặc dụ người nhận truy cập đường dẫn có thể khiến người dùng tiết lộ thông tin và mất tài sản. Người ít am hiểu công nghệ có thể khó nhận ra dấu hiệu. Xử lý ngôn ngữ tự nhiên và học máy có thể hỗ trợ phân tích nội dung, nhưng kết quả phụ thuộc vào chất lượng dữ liệu, cách gán nhãn và khác biệt giữa các kênh.

## 3. Mục tiêu
Xây dựng một hệ thống có khả năng phân tích nội dung tin nhắn tiếng Việt từ SMS, Zalo và email nhằm nhận diện, phân loại các dấu hiệu lừa đảo phổ biến như giả mạo ngân hàng, thông báo trúng thưởng, yêu cầu cung cấp thông tin cá nhân hoặc truy cập đường dẫn đáng ngờ. Hệ thống đưa ra cảnh báo kèm giải thích về dấu hiệu được phát hiện, qua đó hỗ trợ người dùng nhận biết rủi ro và hạn chế nguy cơ bị lừa đảo, chiếm đoạt tài sản, đặc biệt là người ít am hiểu công nghệ.

Trong phạm vi nguyên mẫu, người dùng chủ động dán nội dung văn bản vào hệ thống. Kết quả mang tính tham khảo, không khẳng định chắc chắn một nội dung là lừa đảo và không thay thế việc xác minh với ngân hàng/cơ quan chức năng.

## 4. Câu hỏi nghiên cứu
1. Mô hình học máy nào phù hợp để phân loại tin nhắn lừa đảo tiếng Việt trên bộ dữ liệu nhóm tuyển chọn/xây dựng?
2. Mô hình nhận diện tốt đến đâu theo từng lớp, đặc biệt với lừa đảo bị bỏ sót và tin bình thường bị cảnh báo nhầm?
3. Những dấu hiệu nào trong văn bản có thể giải thích cảnh báo của hệ thống?

## 5. Phạm vi
- Giai đoạn thực nghiệm chính sử dụng dữ liệu SMS tiếng Việt công khai, đã ẩn danh, với nhãn nhị phân: `0` = bình thường, `1` = rác/lừa đảo.
- Đầu vào hệ thống là văn bản do người dùng nhập/dán; không tích hợp quyền truy cập SMS, Zalo, email hay tài khoản ngân hàng.
- Giao diện có thể nhận văn bản dán từ SMS, Zalo hoặc email, nhưng kết quả mô hình chỉ được đánh giá trên SMS. Mở rộng sang email/Zalo cần dữ liệu có nguồn, nhãn và phép đánh giá riêng.
- Kết quả gồm nhãn dự đoán, điểm quyết định của mô hình tuyến tính và một số đặc trưng văn bản góp phần vào điểm dự đoán.

## 6. Phương pháp
1. Khảo sát nghiên cứu, bộ dữ liệu công khai và điều khoản sử dụng; ghi công nguồn dữ liệu.
2. Kiểm tra cột dữ liệu, nhãn, lớp, mẫu thiếu/trùng và việc tách train/test do nhà phát hành cung cấp.
3. Chọn cấu hình trên train bằng stratified 5-fold cross-validation; so sánh TF-IDF ký tự với nhiều cấu hình n-gram và Linear SVM.
4. Huấn luyện cấu hình chọn được trên train và đánh giá một lần trên tập test độc lập đã phát hành.
5. Báo cáo precision, recall, F1 cho từng lớp, macro F1, ma trận nhầm lẫn và phân tích lỗi; không dùng test để chọn mô hình.
6. Xây dựng giao diện web cho nhập văn bản, xem cảnh báo, đặc trưng góp phần vào dự đoán và hướng dẫn xác minh an toàn.

## 7. Sản phẩm dự kiến
- Bộ dữ liệu SMS công khai theo giấy phép và mô tả nguồn/nhãn.
- Mã huấn luyện, mô hình lưu trữ và báo cáo đánh giá.
- Giao diện web để kiểm tra văn bản.
- Báo cáo kết quả, phân tích lỗi và giới hạn nghiên cứu.

## 8. Kế hoạch
| Giai đoạn | Nội dung |
|---|---|
| 1 | Chốt yêu cầu với giảng viên; khảo sát nguồn và giấy phép |
| 2 | Chốt quy tắc nhãn; tuyển chọn dữ liệu và ẩn thông tin cá nhân |
| 3 | Tiền xử lý, loại trùng, thống kê và chia tập |
| 4 | Huấn luyện mô hình cơ sở; thử mô hình nâng cao nếu khả thi |
| 5 | Đánh giá, phân tích lỗi và hoàn thiện giao diện |
| 6 | Hoàn thiện báo cáo, demo và trình bày giới hạn |

## 9. Rủi ro và xử lý
- Thiếu dữ liệu theo kênh: giới hạn kết luận vào SMS; không tuyên bố mô hình được kiểm chứng trên Zalo/email.
- Nhãn/nguồn dữ liệu có giới hạn: ghi rõ đây là nhãn và quy trình do nhà phát hành công bố, nhóm không tự xác minh toàn bộ nguồn gốc từng tin nhắn.
- Mất cân bằng lớp: báo cáo macro F1 và chỉ số từng lớp, không chỉ dùng accuracy.
- Dữ liệu nhạy cảm: ẩn danh trước khi lưu; không dùng tin nhắn riêng tư khi chưa có quyền/căn cứ phù hợp.
- Cảnh báo sai: giải thích dấu hiệu, hướng dẫn xác minh; không tự động chặn tin nhắn hoặc khẳng định tuyệt đối.

## 10. Tài liệu tham khảo ban đầu
- Bộ Công an, “Cần làm gì trước các cuộc gọi và tin nhắn lừa đảo bằng hình thức thông báo khóa thuê bao”, https://bocongan.gov.vn/tin-tuc-su-kien/su-kien-chao-mung-ngay-thanh-lap-nganh/can-lam-gi-truoc-cac-cuoc-goi-va-tin-nhan-lua-dao-bang-hinh-thuc-thong-bao-khoa-thue-bao-s14-t34656.html
- Vietnamese SMS Dataset, Hugging Face, https://huggingface.co/datasets/trannguyenthaituan/vietnamese_sms_dataset (cần thẩm định giấy phép/cấu trúc trước khi dùng).
- Nguyen Tan Cam et al., “VNSED: Vietnamese Spam Email Detection Using Multi Deep Learning Models”, https://vjs.ac.vn/jcc/article/download/22392/2543256498
