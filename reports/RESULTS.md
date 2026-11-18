# Báo cáo thực nghiệm mô hình

## Thiết lập

- **Dữ liệu:** Vietnamese Quality-Assured SMS Scam Dataset; `train.csv` có 2.394 mẫu, `test.csv` có 597 mẫu; nhãn 0=bình thường, 1=rác/lừa đảo.
- **Mô hình:** TF-IDF từ (1–2 gram) và ký tự, kết hợp Linear SVM; trọng số lớp cân bằng.
- **Chọn mô hình:** stratified 5-fold cross-validation trên train, chọn char 2–5 gram, C=1.0.
- **Chọn ngưỡng:** dự đoán ngoài fold của tập huấn luyện; tối đa hóa recall với precision lừa đảo ít nhất 0,90, chỉ xét ngưỡng không thấp hơn 0. Ngưỡng chọn được là 0,0301, precision ngoài fold 0,9507.
- **Đánh giá:** báo cáo dưới đây dùng test do nhà phát hành cung cấp. Tệp test đã được chạy ở phiên bản trước của dự án, nên đây là kết quả tham khảo cho cấu hình cập nhật, không còn là đánh giá mù hoàn toàn trong lịch sử phát triển.

## Kết quả trên tập test

| Chỉ số | Kết quả |
|---|---:|
| Accuracy | 0,9363 |
| Macro F1 | 0,9219 |
| Precision lớp rác/lừa đảo | 0,8297 |
| Recall lớp rác/lừa đảo | 0,9557 |
| F1 lớp rác/lừa đảo | 0,8882 |

Ma trận nhầm lẫn (hàng là nhãn thật, cột là dự đoán):

|  | Dự đoán bình thường | Dự đoán rác/lừa đảo |
|---|---:|---:|
| Bình thường | 408 | 31 |
| Rác/lừa đảo | 7 | 151 |

## Diễn giải

Ngưỡng được hiệu chỉnh trên dự đoán chéo của train để ưu tiên precision, nhưng precision trên tập test là 0,8297, thấp hơn mục tiêu 0,90. Trong 597 mẫu test, 31 tin bình thường bị cảnh báo nhầm và 7 tin lừa đảo bị bỏ sót. Đây là dấu hiệu dữ liệu test khác phân bố với các fold train; không nên coi mục tiêu precision là bảo đảm. Điểm SVM không phải xác suất.

Giao diện dùng trạng thái “chưa đủ ngữ cảnh” cho tin cực ngắn không khớp dấu hiệu từ khóa nhằm tránh khẳng định quá mức với các trường hợp như lời chào. Đây là quy tắc giao diện, chưa được hiệu chỉnh hay đánh giá như một bộ phân loại riêng.

## Giới hạn

1. Chỉ có một bộ SMS; Zalo và email chưa được đánh giá riêng.
2. Nhãn gộp “rác/lừa đảo” không xác định chắc chắn ý đồ hoặc phân loại dạng lừa đảo.
3. Hiệu quả có thể giảm khi chiến thuật và cách viết thay đổi.
4. Tập test đã được xem ở một lần chạy trước đó trong dự án; nên có bộ test mới, tách biệt trước khi dùng kết quả cho quyết định triển khai.
5. Ví dụ trong giao diện là ví dụ minh họa, không được thêm vào dữ liệu huấn luyện.

## Tệp kết quả

- `evaluation.json`: cấu hình, ngưỡng, chỉ số và ma trận nhầm lẫn.
- `cross_validation.csv`: kết quả chọn cấu hình.
- `confusion_matrix.csv`: ma trận nhầm lẫn.
- `test_predictions.csv`: nhãn thật/dự đoán theo đúng thứ tự test, không lặp lại nội dung SMS.
