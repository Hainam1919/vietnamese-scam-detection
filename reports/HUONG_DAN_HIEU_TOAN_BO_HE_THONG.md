# Tài liệu hiểu toàn bộ hệ thống nhận diện tin nhắn rác/lừa đảo tiếng Việt

**Sinh viên thực hiện: Diệp Hải Nam**  
**Phiên bản tài liệu: 06/11/2026**  
**Phạm vi đối chiếu:** mã nguồn và báo cáo hiện có trong dự án. Tài liệu không khẳng định hệ thống đã triển khai thực tế hoặc đã kiểm định trên Zalo/email.

## 1. Hệ thống này làm gì?

Đây là nguyên mẫu ứng dụng web hỗ trợ phân tích nội dung tin nhắn tiếng Việt. Người dùng nhập văn bản, mô hình tính điểm phân loại, giao diện hiển thị kết quả cùng dấu hiệu và hướng dẫn xác minh.

Ví dụ, người dùng nhận một tin yêu cầu chuyển phí để nhận thưởng. Họ có thể dán nội dung vào hệ thống để xem cảnh báo, các cụm từ đáng chú ý và bước nên làm tiếp theo.

Hệ thống không xác minh danh tính người gửi, không biết một giao dịch có thật hay không và không tự động chặn tin nhắn. Đầu ra là gợi ý hỗ trợ người dùng.

### Dán văn bản rồi kiểm tra có đúng đề tài không?

Có, trong phạm vi nguyên mẫu mà đề cương đã nêu. Phần nhập văn bản chỉ là giao diện nhìn thấy được. Phía sau còn có dữ liệu, biểu diễn văn bản, huấn luyện, lựa chọn mô hình, đánh giá và lưu trữ phản hồi.

Tuy nhiên, nếu tên đề tài được hiểu là tự động bảo vệ cả SMS, Zalo và email thì hệ thống hiện chưa đáp ứng cách hiểu đó. Chọn nguồn “Zalo” không tạo kết nối tới tài khoản Zalo. Cần trình bày rõ giới hạn này khi bảo vệ.

Tên phù hợp để trao đổi với giảng viên: **“Xây dựng nguyên mẫu hỗ trợ phát hiện tin nhắn rác/lừa đảo tiếng Việt bằng học máy”**. Không tự thay tên đề tài đã được giảng viên phê duyệt.

## 2. Những phần đã có và chưa có

| Hạng mục | Trạng thái hiện tại |
|---|---|
| Phân tích văn bản một tin | Đã có |
| Chọn nguồn SMS/Zalo/Email | Đã có, chỉ là nguồn văn bản người dùng chọn |
| Huấn luyện TF-IDF + Linear SVM | Đã có |
| Giải thích đặc trưng tác động tới điểm | Đã có |
| Đánh dấu từ khóa và hướng dẫn xác minh | Đã có |
| Kiểm tra nhiều mẫu, đối chiếu nhãn, tải JSON | Đã bổ sung |
| Lịch sử tùy chọn và thống kê cục bộ | Đã có |
| Hàng chờ phản hồi, gán nhãn thủ công, xuất CSV | Đã có |
| Tự đọc SMS/Zalo/email | Chưa có |
| Đọc ảnh chụp bằng OCR | Chưa có |
| Kiểm tra uy tín tên miền qua dịch vụ ngoài | Chưa có |
| Phân quyền người dùng/người duyệt | Chưa có |
| Tự động học từ phản hồi | Chưa có |
| Kiểm định riêng cho Zalo/email | Chưa có |

## 3. Kiến trúc tổng thể

Luồng xử lý một tin:

1. Người dùng nhập nội dung trên giao diện Streamlit.
2. Mã loại bỏ khoảng trắng ở hai đầu và kiểm tra nội dung rỗng.
3. Pipeline TF-IDF chuyển văn bản thành các giá trị số.
4. Linear SVM tính điểm quyết định.
5. Mã so sánh điểm với ngưỡng và áp dụng quy tắc trạng thái chưa rõ.
6. Giao diện hiển thị nhãn, điểm, đặc trưng và dấu hiệu từ khóa.
7. Hệ thống cập nhật bộ đếm. Nội dung chỉ vào lịch sử nếu người dùng bật lưu.

Ba nhóm thành phần chính:

- **Giao diện:** nhập liệu, hiển thị kết quả, lịch sử, phản hồi và kiểm tra bộ mẫu.
- **Xử lý:** mô hình học máy, tìm dấu hiệu từ khóa, giải thích điểm và che dữ liệu thường gặp.
- **Lưu trữ:** mô hình joblib, báo cáo JSON/CSV và cơ sở dữ liệu SQLite.

Ứng dụng dùng mô hình đã lưu để dự đoán. Mỗi lần bấm phân tích không huấn luyện lại mô hình.

## 4. Công nghệ sử dụng

| Công nghệ | Vai trò |
|---|---|
| Python | Ngôn ngữ xử lý và xây dựng hệ thống |
| Streamlit | Tạo giao diện web |
| pandas | Đọc và xử lý dữ liệu dạng bảng |
| scikit-learn | TF-IDF, SVM, kiểm định chéo và các chỉ số đánh giá |
| joblib | Lưu và nạp pipeline đã huấn luyện |
| SQLite | Lưu dữ liệu sử dụng cục bộ |
| Biểu thức chính quy | Tìm mẫu từ khóa và che một số thông tin nhạy cảm |

Phiên bản thư viện được ghi trong `requirements.txt`. Nên dùng môi trường ảo của dự án để tránh nạp mô hình bằng phiên bản scikit-learn khác bản đã huấn luyện.

## 5. Dữ liệu và ý nghĩa nhãn

Theo hồ sơ `DATASET.md`, dự án sử dụng Vietnamese Quality-Assured SMS Scam Dataset, tải train/test ngày 15/10/2026. Hồ sơ dự án ghi giấy phép CC BY 4.0. Khi nộp hoặc phát hành lại dữ liệu, cần đối chiếu nguồn chính thức và ghi công đầy đủ.

| Tập dữ liệu | Bình thường | Rác/lừa đảo | Tổng |
|---|---:|---:|---:|
| Huấn luyện | 1.754 | 640 | 2.394 |
| Kiểm tra | 439 | 158 | 597 |

- `message`: nội dung tin nhắn.
- `label = 0`: bình thường/hợp lệ.
- `label = 1`: rác/lừa đảo.

**Lưu ý quan trọng:** nhãn 1 gộp tin rác và lừa đảo. Mô hình hiện không tách riêng quảng cáo phiền nhiễu với hành vi lừa đảo tài chính, cũng không phân loại chính xác từng chiêu trò.

Dữ liệu có mô tả ẩn danh từ nhà phát hành. Đó không phải bằng chứng rằng nhóm đã kiểm toán độc lập nguồn gốc và nhãn của mọi tin.

## 6. TF-IDF hoạt động thế nào?

Máy học cần đầu vào dạng số. TF-IDF biểu diễn văn bản bằng trọng số của từ hoặc chuỗi ký tự:

- TF phản ánh mức xuất hiện của đặc trưng trong một văn bản.
- IDF giảm trọng số của đặc trưng phổ biến trong nhiều văn bản.
- Kết quả là một vector thưa: phần lớn giá trị bằng 0 vì mỗi tin chỉ chứa một phần nhỏ kho đặc trưng.

Pipeline hiện kết hợp:

1. TF-IDF từ với n-gram 1–2: ví dụ “chuyển” và “chuyển tiền”.
2. TF-IDF ký tự: khai thác các đoạn ký tự liên tiếp, hữu ích để biểu diễn biến thể cách viết.

Cấu hình chọn được dùng ký tự dài 2–5. Cả hai nhánh dùng `min_df=2` và TF dưới dạng log. Giới hạn số đặc trưng là 120.000 ở nhánh từ và 180.000 ở nhánh ký tự, không có nghĩa mỗi lần huấn luyện chắc chắn dùng đủ các giới hạn đó.

TF-IDF không tự hiểu ý nghĩa như con người. Các chuỗi từ giống nhau có thể xuất hiện trong cả lời cảnh báo an toàn và lời dụ dỗ.

## 7. Linear SVM hoạt động thế nào?

Có thể hình dung mô hình học một ranh giới phân chia hai nhóm văn bản trong không gian đặc trưng.

Điểm quyết định có dạng:

**s = w·x + b**

Trong đó `x` là vector TF-IDF, `w` là trọng số mô hình học được và `b` là hệ số chặn. Mô hình không dùng riêng danh sách từ khóa viết tay để tạo điểm này.

Cấu hình cuối sử dụng LinearSVC với `C = 1,0`, trọng số lớp cân bằng và seed 42. Trọng số lớp cân bằng giúp thay đổi mức phạt theo tần suất lớp; nó không tự thêm tin lừa đảo vào dữ liệu.

**Điểm SVM 0,8 không có nghĩa 80% là lừa đảo.** Đây là điểm quyết định, chưa được hiệu chỉnh thành xác suất.

## 8. Cách chọn mô hình và ngưỡng

`train.py` thử ba cấu hình:

| Cấu hình ký tự | C | Macro F1 trung bình kiểm định chéo |
|---|---:|---:|
| 2–5 | 1,0 | 0,9698 |
| 3–6 | 2,0 | 0,9692 |
| 3–5 | 1,0 | 0,9688 |

Các cấu hình đều thuộc họ TF-IDF + Linear SVM. Chưa thể nói dự án đã so sánh SVM với Naive Bayes, Logistic Regression hay PhoBERT.

Quy trình:

1. Chia train thành 5 phần có duy trì tương quan lớp.
2. Luân phiên dùng 4 phần học và 1 phần đánh giá.
3. Chọn cấu hình theo Macro F1, rồi recall khi cần phân hạng.
4. Tạo điểm dự đoán ngoài fold trên train để chọn ngưỡng.
5. Tìm ngưỡng không âm, ưu tiên recall trong các ngưỡng đạt precision ít nhất 0,90 trên dự đoán ngoài fold.
6. Huấn luyện cấu hình chọn được trên toàn bộ train và đánh giá trên test.

Ngưỡng lưu hiện tại khoảng **0,0301**. Mục tiêu precision 90% khi chọn ngưỡng không bảo đảm precision 90% ở dữ liệu mới.

Tập test đã được xem ở lần chạy trước trong lịch sử dự án. Vì vậy cần mô tả kết quả hiện tại là đánh giá tham khảo trên tập test có sẵn, không gọi là đánh giá mù hoàn toàn.

## 9. Bốn trạng thái trên giao diện

| Trạng thái | Cách xử lý hiện tại |
|---|---|
| Chưa đủ ngữ cảnh | Tin có tối đa 3 từ, không khớp dấu hiệu |
| Cần xem xét | Điểm vượt ngưỡng nhưng thấp hơn ngưỡng + 0,20 và không khớp dấu hiệu |
| Cảnh báo | Điểm vượt ngưỡng, không thuộc hai trường hợp trên |
| Bình thường | Điểm dưới ngưỡng, không thuộc trường hợp thiếu ngữ cảnh |

Đây là luật giao diện bổ sung bên ngoài SVM. Chỉ số trong báo cáo test là của bộ phân loại dùng ngưỡng; không tự động chứng minh chất lượng toàn bộ hệ thống có thêm các trạng thái này.

Một tin không khớp từ khóa vẫn có thể bị cảnh báo nếu điểm đủ cao. Ngược lại, xuất hiện từ “OTP” hoặc “ngân hàng” không tự chứng minh lừa đảo.

## 10. Giải thích kết quả và quy tắc từ khóa

Hệ thống có hai dạng giải thích:

- **Đóng góp đặc trưng:** lấy trọng số SVM nhân giá trị TF-IDF để tìm cụm đẩy điểm về mỗi lớp. Danh sách chỉ hiển thị một số đặc trưng nổi bật, không phải toàn bộ phép tính.
- **Dấu hiệu theo quy tắc:** tìm từ/cụm liên quan ngân hàng, thông tin đăng nhập, trúng thưởng, thúc giục, chuyển tiền, việc làm/đầu tư và đường dẫn.

Các quy tắc hiện chủ yếu khớp mẫu văn bản. Chúng có thể nhầm câu “không cung cấp OTP” thành dấu hiệu liên quan yêu cầu OTP vì chưa hiểu đầy đủ phủ định.

Khi phân tích sai, không nên đoán chắc nguyên nhân chỉ từ vài từ xuất hiện trong tin. Cần xem đặc trưng đóng góp, dữ liệu và ngưỡng. Không nên sửa bằng cách coi tất cả tin chứa chữ “không” là an toàn.

## 11. Kết quả đánh giá và cách đọc

| Chỉ số | Giá trị |
|---|---:|
| Accuracy | 93,63% |
| Macro F1 | 0,9219 |
| Precision lớp rác/lừa đảo | 82,97% |
| Recall lớp rác/lừa đảo | 95,57% |
| F1 lớp rác/lừa đảo | 0,8882 |

Ma trận nhầm lẫn:

| Nhãn thật | Dự đoán bình thường | Dự đoán rác/lừa đảo |
|---|---:|---:|
| Bình thường | 408 | 31 |
| Rác/lừa đảo | 7 | 151 |

Diễn giải:

- **Precision = 151/(151+31):** trong các tin mô hình cảnh báo, khoảng 82,97% khớp lớp rác/lừa đảo của bộ dữ liệu.
- **Recall = 151/(151+7):** mô hình tìm được khoảng 95,57% tin thuộc lớp rác/lừa đảo.
- **Accuracy = (408+151)/597:** tỷ lệ dự đoán đúng trên tất cả mẫu.
- **F1:** trung bình điều hòa của precision và recall.
- **Macro F1:** trung bình F1 của hai lớp, mỗi lớp có trọng số bằng nhau.

Không nên chỉ báo cáo accuracy vì lớp bình thường đông hơn. Hai lỗi cần quan tâm riêng là 31 cảnh báo nhầm và 7 tin bị bỏ sót.

## 12. Bộ 12 ví dụ minh họa

Các ví dụ tự soạn dùng để phát hiện điểm yếu, không thay thế tập kiểm định.

| Nhóm kỳ vọng | Kết quả hệ thống |
|---|---|
| 5 tin bình thường | 1 bình thường, 3 cảnh báo, 1 cần xem xét |
| 7 tin lừa đảo | 6 cảnh báo, 1 bình thường |

Có **7/12** mẫu khớp nhãn minh họa khi ánh xạ “Cảnh báo” sang nhãn kỳ vọng “Lừa đảo”. Trạng thái cần xem xét không tính là khớp nhãn nhị phân.

Các lỗi quan sát được: cảnh báo tin trao đổi bạn bè, thông báo giao dịch an toàn và nhắc giữ kín OTP; bỏ sót mẫu dụ cài ứng dụng. Đây là bằng chứng hệ thống còn hạn chế khi gặp cách diễn đạt mới.

Các thông tin 8/12 và 2 cảnh báo nhầm từng xuất hiện trong trao đổi trước không phải kết quả đã đối chiếu mới nhất. Dùng số liệu trong mục này khi thuyết trình.

## 13. Hướng dẫn sử dụng bốn mục

### Phân tích tin nhắn

1. Che dữ liệu cá nhân trước khi dán.
2. Chọn nguồn tin. Nguồn không làm đổi mô hình.
3. Nhập nội dung rồi bấm phân tích.
4. Đọc nhãn, điểm và cả hai nhóm đặc trưng đóng góp.
5. Xem dấu hiệu và hướng dẫn xác minh.
6. Nếu sai, phản hồi và kiểm tra mẫu đã ẩn danh trước khi đưa vào hàng chờ.

### Kiểm tra nhiều mẫu

1. Mỗi dòng là một tin, tối đa 100 tin và 2.000 ký tự mỗi tin.
2. Có thể nhập nhãn 0/1 cách nhau bằng dấu phẩy; số nhãn phải khớp số tin.
3. Hệ thống hiển thị kết quả, điểm và đối chiếu: khớp, cảnh báo nhầm, bỏ sót hoặc chưa kết luận.
4. Nếu chưa nhập nhãn, hệ thống ghi chưa có nhãn, không tính đó là dự đoán sai.
5. Có thể tải JSON hoặc xóa kết quả.

Bộ mẫu không ghi vào lịch sử hay bộ đếm phân tích thông thường. Kết quả giữ trong phiên. Tệp tải xuống chứa nội dung người dùng đã nhập, vì vậy cần dùng dữ liệu đã ẩn danh.

### Tổng quan

Xem bộ đếm, lịch sử đã bật lưu và mẫu phản hồi đang chờ. Người duyệt chọn bình thường/rác-lừa đảo hoặc từ chối, sau đó xuất CSV mẫu đã duyệt để xem xét.

Nút phản hồi hiện cộng bộ đếm khi bấm. Chưa có cơ chế bảo đảm mỗi người chỉ phản hồi một lần, nên không dùng tỷ lệ phản hồi làm độ chính xác.

### Hướng dẫn & an toàn

Giải thích các trạng thái, giới hạn theo nguồn, dữ liệu, cách đánh giá và cách xử lý khi gặp tin đáng ngờ.

## 14. Dữ liệu lưu ở đâu?

SQLite nằm tại `reports/feedback.sqlite`.

| Bảng | Nội dung |
|---|---|
| feedback_counts | Tổng số phản hồi |
| analysis_counts | Tổng lượt theo nguồn và kết quả |
| app_settings | Cài đặt lưu lịch sử |
| analysis_history | Nội dung và kết quả khi bật lịch sử |
| review_queue | Mẫu chờ duyệt, trạng thái và nhãn được duyệt |

Tắt lưu lịch sử không xóa lịch sử cũ. Nút xóa lịch sử không đồng nghĩa xóa hàng chờ phản hồi. Mẫu bị từ chối vẫn còn trong cơ sở dữ liệu hiện tại.

Che tự động bằng quy tắc chỉ xử lý một số dạng email, số điện thoại, chuỗi số dài, OTP và đường dẫn. Tên người, địa chỉ hoặc thông tin viết khác mẫu có thể còn sót.

Ứng dụng dự đoán cục bộ bằng mô hình đã lưu. Nếu sau này đặt ứng dụng lên máy chủ, “cục bộ” sẽ là máy chủ đó, không tự động là máy của từng người truy cập. Chưa có phân quyền, nên không nên coi bản hiện tại là dịch vụ nhiều người dùng đã hoàn thiện.

## 15. Bản đồ tệp và hàm cần biết

| Tệp | Mục đích |
|---|---|
| app.py | Giao diện, dự đoán, giải thích, thống kê và phản hồi |
| train.py | Xây mô hình, chọn cấu hình/ngưỡng, tạo báo cáo |
| requirements.txt | Phiên bản thư viện |
| data/train.csv | Dữ liệu huấn luyện |
| data/test.csv | Dữ liệu kiểm tra |
| models/scam_classifier.joblib | Pipeline đã huấn luyện |
| reports/evaluation.json | Chỉ số, cấu hình và ngưỡng hiện tại |
| reports/RESULTS.md | Báo cáo thực nghiệm và giới hạn |
| DATASET.md | Hồ sơ nguồn và giấy phép dữ liệu |
| proposal.md | Phạm vi và mục tiêu đề tài |

Các hàm trong `app.py`:

- `load_artifacts`: nạp mô hình và báo cáo, dùng cache.
- `classify_message`: tính điểm, so ngưỡng và chọn trạng thái.
- `find_signals`: tìm dấu hiệu bằng quy tắc.
- `explain_linear_prediction`: tìm đặc trưng đóng góp theo hướng mỗi lớp.
- `redact_sensitive_text`: che một số dữ liệu thường gặp.
- `save_history`: lưu một lượt nếu tính năng lịch sử đang bật.
- `add_review_sample` và `update_review_status`: quản lý mẫu duyệt.

## 16. Chạy và dừng hệ thống

Với môi trường ảo có sẵn, mở Terminal và chạy:

```bash
cd /Users/hainam1919/Documents/vietnamese-scam-detection
.venv/bin/python -m streamlit run app.py --server.port 8502
```

Mở `http://localhost:8502/`. Dừng bằng Ctrl+C tại cửa sổ Terminal đang chạy ứng dụng.

Chỉ chạy lại huấn luyện khi thực sự muốn tạo lại mô hình và báo cáo:

```bash
.venv/bin/python train.py
```

Lệnh huấn luyện có thể ghi lại các tệp mô hình và báo cáo hiện có. Nên lưu bản cũ trước khi thực nghiệm để so sánh. Không cần huấn luyện lại chỉ để mở giao diện.

Nếu báo thiếu thư viện, kiểm tra đang dùng đúng môi trường ảo. Nếu cổng bận, dùng cổng khác hoặc dừng đúng tiến trình ứng dụng cũ. Nếu cảnh báo phiên bản scikit-learn khác lúc lưu mô hình, dùng môi trường phù hợp trước khi tin vào kết quả.

## 17. Những phần còn thiếu và thứ tự ưu tiên

**Ưu tiên 1: chất lượng và tính đúng của đánh giá.** Kiểm tra mẫu trùng trong và giữa train/test; tạo tập test mới có nhãn xác nhận; đánh giá cả SVM lẫn các trạng thái giao diện. Không chỉnh ngưỡng liên tục dựa vào test rồi gọi test là độc lập.

**Ưu tiên 2: giảm cảnh báo nhầm và bỏ sót.** Thu thập tin bình thường có từ nhạy cảm, câu phủ định và chiêu thức mới. So sánh các mô hình cơ sở trên cùng quy trình. Phản hồi đã duyệt không tự bảo đảm là nhãn đúng, vẫn cần kiểm tra.

**Ưu tiên 3: quản lý dữ liệu.** Thêm phân quyền người duyệt, chống phản hồi lặp, xóa mẫu theo yêu cầu và quản lý phiên bản mô hình/dữ liệu.

**Ưu tiên 4: mở rộng đầu vào.** OCR ảnh chụp, nhập tệp và tích hợp nguồn tin chỉ nên triển khai sau khi xác định quyền truy cập, bảo mật và cách đánh giá từng nguồn.

Thêm tính năng không tự làm mô hình chính xác hơn. Nếu phải lựa chọn, cần ưu tiên bằng chứng chất lượng trước các hiệu ứng giao diện.

## 18. Kịch bản demo trước giảng viên

1. Giới thiệu bài toán và phạm vi nhập văn bản chủ động.
2. Mở một mẫu bình thường và một mẫu yêu cầu nộp phí nhận thưởng.
3. Giải thích nhãn, điểm SVM và dấu hiệu tìm được.
4. Mở mẫu cảnh báo an toàn OTP để cho thấy mô hình có thể nhận diện nhầm.
5. Chạy bộ nhiều mẫu có nhãn tham chiếu, đọc các nhóm lỗi.
6. Giới thiệu lịch sử tùy chọn và hàng chờ duyệt.
7. Trình bày ma trận nhầm lẫn và hướng cải thiện.

Không cần che giấu ví dụ sai. Phân tích được lỗi và giới hạn là một phần của báo cáo nghiên cứu.

## 19. Câu hỏi thường gặp khi bảo vệ

**Vì sao chọn SVM?** Mô hình tuyến tính phù hợp làm nền tảng cho biểu diễn văn bản TF-IDF, có thể chạy trên máy cá nhân và giải thích đóng góp đặc trưng. Dự án chưa chứng minh SVM tốt nhất trong mọi mô hình.

**Hệ thống có dùng AI không?** Có dùng học máy có giám sát. Mô hình học trọng số từ mẫu gán nhãn. Ngoài ra có các quy tắc viết tay để hỗ trợ giải thích và trình bày.

**Sao “xin chào” lại bị cảnh báo?** Tin ngắn có thể thiếu ngữ cảnh và mô hình có thể học tương quan chưa tốt từ dữ liệu. Luật giao diện chuyển một số tin quá ngắn sang chưa đủ ngữ cảnh; đây chưa phải giải pháp cho mọi lỗi.

**Có link nghĩa là lừa đảo không?** Không. Hệ thống chỉ phát hiện dạng đường dẫn trong văn bản, chưa truy vấn uy tín tên miền hoặc xác minh trang đích.

**Phản hồi sai có làm hệ thống thông minh hơn ngay không?** Không. Mẫu cần duyệt và được xem xét đưa vào dữ liệu trong một lần huấn luyện có đánh giá lại.

**Độ chính xác bao nhiêu?** Trên tập test có sẵn: accuracy 93,63%, Macro F1 0,9219, precision lớp rác/lừa đảo 82,97%, recall 95,57%. Các con số không bảo đảm hiệu quả tương tự ngoài thực tế.

**Tại sao chỉ có 7/12 ví dụ đúng dù test cao?** Hai bộ mẫu khác nhau, bộ minh họa rất nhỏ và có những tình huống khó. Một số kết quả giao diện chưa kết luận cũng không tính là khớp nhãn. Không so sánh hai tỷ lệ như cùng một phép kiểm định.

**Có hỗ trợ Zalo/email không?** Có thể nhập văn bản từ các nguồn đó. Chưa tích hợp tài khoản và chưa có kiểm định riêng.

**Điểm yếu lớn nhất là gì?** Khả năng tổng quát hóa sang ngữ cảnh mới, cảnh báo nhầm, nhãn gộp rác/lừa đảo và thiếu tập kiểm tra mới độc lập.

## 20. Đoạn giới thiệu ngắn để luyện nói

“Em là Diệp Hải Nam. Em xây dựng nguyên mẫu hỗ trợ phân tích tin nhắn rác/lừa đảo tiếng Việt. Hệ thống sử dụng TF-IDF kết hợp Linear SVM, có giao diện nhập văn bản, giải thích đặc trưng, kiểm tra nhiều mẫu và quản lý phản hồi cục bộ. Trên 597 SMS kiểm tra, mô hình phát hiện đúng 151 mẫu rác/lừa đảo, bỏ sót 7 mẫu và cảnh báo nhầm 31 tin bình thường. Kết quả hiện chỉ phản ánh bộ SMS có sẵn, chưa xác nhận chất lượng trên Zalo/email. Hướng tiếp theo là xây dựng tập kiểm tra mới và giảm lỗi do khác biệt ngữ cảnh.”

## 21. Nguồn số liệu và lưu ý phiên bản

Tài liệu dựa vào `app.py`, `train.py`, `proposal.md`, `README.md`, `DATASET.md`, `reports/evaluation.json` và `reports/RESULTS.md` trong dự án ngày 06/11/2026.

Tệp `HOI_DAP_BAO_VE.md` cũ đang chứa số liệu của phiên bản trước (Macro F1 0,914, precision 0,812, 35 cảnh báo nhầm). Không dùng lẫn với báo cáo hiện tại. Ưu tiên số liệu trong `reports/evaluation.json` và kiểm tra phiên bản mô hình tương ứng trước khi trình bày.

## 22. Hướng dẫn báo cáo với bộ 17 slide

Phần này tương ứng bộ slide phiên bản v7, có trang cảm ơn ở cuối. Lời nói bên dưới là gợi ý để luyện tập; nên hiểu ý rồi trình bày bằng cách nói tự nhiên của mình.

### Phân bổ thời gian đề xuất

Nếu có khoảng 15 phút trình bày và demo, có thể phân bổ:

| Phần | Slide | Thời lượng |
|---|---|---:|
| Mở đầu, mục tiêu và phạm vi | 1–3 | 2 phút |
| Thành phần, huấn luyện và giải thích | 4–6 | 3 phút |
| Quy trình sử dụng, dữ liệu cá nhân và chức năng bổ sung | 7–10 | 2 phút |
| Dữ liệu và kết quả thực nghiệm | 11–15 | 4 phút |
| Demo trực tiếp | Sau slide 15 | 3 phút |
| Kết luận và cảm ơn | 16–17 | 1 phút |

Thời gian hỏi đáp tính riêng theo yêu cầu giảng viên. Nếu chỉ có 10 phút, rút phần mô tả tính năng và demo, dành đủ thời gian cho phương pháp và kết quả. Không tăng tốc đọc toàn bộ chữ trên slide.

### Slide 1 — Giới thiệu đề tài

**Mục tiêu:** giới thiệu bản thân và sản phẩm trong khoảng 20–30 giây.

Lời nói gợi ý:

“Em kính chào thầy cô và các bạn. Em là Diệp Hải Nam. Hôm nay em trình bày hệ thống hỗ trợ nhận diện tin nhắn rác và lừa đảo tiếng Việt. Báo cáo gồm phạm vi hệ thống, phương pháp học máy, kết quả thực nghiệm và những hạn chế cần cải thiện.”

**Chuyển ý:** “Trước hết, em xin trình bày hệ thống giải quyết nhu cầu gì.”

### Slide 2 — Mục tiêu và cách hệ thống hỗ trợ

“Hệ thống nhận nội dung tin nhắn và hỗ trợ ba việc: phân loại, giải thích dấu hiệu và đưa hướng dẫn xác minh. Khi có cảnh báo, người dùng vẫn cần kiểm tra người gửi và thông tin qua kênh chính thức.”

Chỉ vào ba phần trên slide, mỗi phần giải thích một câu. Không đọc lại nguyên đoạn chữ.

**Chuyển ý:** “Để hiểu đúng khả năng của sản phẩm, em xin làm rõ phạm vi hiện tại.”

### Slide 3 — Phạm vi đề tài và mức độ hoàn thiện

“Trong phạm vi nguyên mẫu, người dùng chủ động nhập hoặc dán văn bản. Chọn nguồn SMS, Zalo hay email chỉ giúp ghi nhận nguồn nội dung, chưa tạo kết nối tới tài khoản. Mô hình hiện mới có dữ liệu đánh giá trên SMS.”

Nếu tên đề tài chính thức có cả ba kênh, nói rõ đó là phạm vi định hướng, còn kết luận thực nghiệm hiện giới hạn trên SMS. Không tự đổi tên đề tài đã duyệt ngay trong buổi bảo vệ.

**Chuyển ý:** “Phía sau ô nhập văn bản là các thành phần sau.”

### Slide 4 — Các thành phần của hệ thống

“Hệ thống gồm giao diện Streamlit, phần xử lý bằng mô hình và quy tắc, cùng phần lưu trữ. Giao diện nhận nội dung; pipeline đã huấn luyện tính điểm; các quy tắc tìm dấu hiệu. SQLite lưu thống kê, lịch sử theo lựa chọn và mẫu phản hồi chờ duyệt.”

**Ý cần nhớ:** bấm phân tích là dự đoán bằng mô hình đã lưu, không phải huấn luyện lại.

**Chuyển ý:** “Mô hình đó được xây dựng qua quy trình huấn luyện như sau.”

### Slide 5 — Quy trình huấn luyện mô hình

“Em dùng TF-IDF từ và ký tự kết hợp Linear SVM. Mã huấn luyện thử ba cấu hình, đánh giá bằng kiểm định chéo 5 phần trên tập train rồi chọn cấu hình phù hợp. Ngưỡng cảnh báo được chọn từ dự đoán ngoài fold của train trước khi tính kết quả trên test.”

Nếu cần giải thích ngoài fold: mỗi mẫu nhận điểm từ một lần huấn luyện không sử dụng chính mẫu đó trong phần học của fold tương ứng.

**Không nói:** “Em đã so sánh nhiều thuật toán và SVM là tốt nhất.” Hiện dự án mới so sánh các cấu hình trong cùng họ SVM.

**Chuyển ý:** “Khi đưa một tin mới vào, người dùng sẽ đọc kết quả như thế nào?”

### Slide 6 — Cách đọc kết quả phân tích

“Điểm SVM được so với ngưỡng khoảng 0,0301. Ngoài nhãn bình thường hoặc cảnh báo, giao diện có trạng thái chưa đủ ngữ cảnh và cần xem xét. Các đặc trưng đóng góp giúp giải thích điểm; các từ khóa giúp chỉ ra nội dung cần chú ý.”

**Nhấn mạnh:** “Điểm SVM không phải phần trăm chắc chắn. Có từ OTP cũng không có nghĩa tin đó chắc chắn lừa đảo.”

**Chuyển ý:** “Từ kết quả này, hệ thống hỗ trợ quy trình sử dụng và phản hồi.”

### Slide 7 — Quy trình sử dụng và phản hồi

“Người dùng dán nội dung đã che thông tin cá nhân, xem phân tích và hướng dẫn xác minh. Nếu kết quả chưa đúng, họ có thể gửi mẫu đã kiểm tra vào hàng chờ. Người duyệt gán nhãn trước khi xuất dữ liệu để xem xét.”

**Nhấn mạnh:** phản hồi không tự động cập nhật mô hình ngay lập tức.

**Chuyển ý:** “Do tin nhắn có thể chứa dữ liệu riêng tư, việc lưu trữ cần được giải thích rõ.”

### Slide 8 — Tổng quan và quyền riêng tư

“Lịch sử nội dung mặc định tắt. Khi người dùng bật, ứng dụng lưu nội dung trên máy đang chạy hệ thống và có chức năng xóa lịch sử. Bộ đếm phản hồi chỉ phản ánh đánh giá người dùng, không thay thế nhãn đã xác nhận.”

“Ngoài ra, cơ chế che thông tin bằng quy tắc có thể bỏ sót tên hoặc địa chỉ. Bản hiện tại chưa có phân quyền người duyệt.”

**Chuyển ý:** “Để kiểm tra hệ thống thuận tiện hơn, em bổ sung khả năng xử lý một bộ mẫu.”

### Slide 9 — Bổ sung kiểm tra nhiều mẫu

“Mỗi dòng là một tin nhắn, tối đa 100 tin. Người dùng có thể nhập nhãn tham chiếu 0 hoặc 1 để đối chiếu. Hệ thống thống kê mẫu khớp, cảnh báo nhầm, bỏ sót và chưa kết luận, đồng thời cho tải báo cáo JSON.”

**Ý cần nhớ:** bộ mẫu người dùng nhập không tự trở thành một tập kiểm định độc lập.

**Chuyển ý:** “Chức năng này giúp kiểm thử thuận tiện, nhưng hệ thống vẫn còn những việc cần làm trước khi triển khai.”

### Slide 10 — Những phần cần bổ sung trước triển khai

“Em xác định ba nhóm việc còn thiếu: cải thiện chất lượng nhận diện, bổ sung đánh giá độc lập và hoàn thiện khả năng sử dụng thực tế. Các chức năng OCR đọc ảnh, kết nối hộp thư và phân quyền người duyệt hiện chưa triển khai.”

Không trình bày danh sách định hướng như chức năng đã hoạt động.

**Chuyển ý:** “Tiếp theo là dữ liệu và bằng chứng thực nghiệm của phiên bản hiện tại.”

### Slide 11 — Dữ liệu và phương pháp

“Tập huấn luyện có 2.394 tin, tập kiểm tra có 597 tin. Nhãn gồm bình thường và rác/lừa đảo. TF-IDF chuyển văn bản thành vector đặc trưng, sau đó Linear SVM tính điểm phân loại.”

**Nhấn mạnh:** nhãn rác/lừa đảo được gộp, chưa tách quảng cáo với lừa đảo tài chính.

Khi được hỏi nguồn, dẫn hồ sơ DATASET.md và nguồn bộ dữ liệu. Không nói dữ liệu do mình tự thu thập nếu thực tế dùng dữ liệu công khai.

**Chuyển ý:** “Kết quả trên tập kiểm tra được thể hiện qua các chỉ số sau.”

### Slide 12 — Kết quả trên tập SMS kiểm tra

“Macro F1 đạt khoảng 0,922. Precision lớp rác/lừa đảo khoảng 83%, recall khoảng 95,6%. Recall cao cho thấy mô hình phát hiện được phần lớn mẫu rác/lừa đảo trong tập này, nhưng precision thấp hơn mục tiêu 90% khi chọn ngưỡng.”

Giải thích bằng ngôn ngữ đơn giản: precision hỏi trong những tin đã cảnh báo có bao nhiêu tin đúng lớp; recall hỏi trong những tin thật sự thuộc lớp rác/lừa đảo, mô hình tìm được bao nhiêu.

**Chuyển ý:** “Ma trận nhầm lẫn cho thấy cụ thể các lỗi này.”

### Slide 13 — Ma trận nhầm lẫn

“Đọc theo hàng nhãn thật: trong 439 tin bình thường, mô hình phân loại đúng 408 và cảnh báo nhầm 31. Trong 158 tin rác/lừa đảo, mô hình phát hiện 151 và bỏ sót 7.”

Chỉ lần lượt vào bốn ô. Sau đó nói: “Cả hai lỗi đều cần quan tâm: cảnh báo nhầm làm giảm sự tin tưởng, còn bỏ sót khiến người dùng có thể không nhận được cảnh báo cần thiết.”

**Lưu ý:** tập test này đã từng được xem trong lịch sử phát triển, nên cần thêm một tập test mới trước khi đưa ra kết luận mạnh hơn.

### Slide 14 — Thử thêm 12 kịch bản minh họa

“Em bổ sung 12 ví dụ tự soạn để tìm điểm yếu. Trong 5 ví dụ bình thường, một mẫu được xếp bình thường, ba mẫu bị cảnh báo và một mẫu cần xem xét. Trong 7 ví dụ lừa đảo, sáu mẫu bị cảnh báo, một mẫu bị bỏ sót.”

“Có 7/12 mẫu khớp nhãn minh họa. Đây là một bộ ví dụ nhỏ để phân tích lỗi, không phải số đo độ chính xác tổng quát.”

**Chuyển ý:** “Hai trường hợp sau cho thấy vì sao cần kiểm tra ngữ cảnh kỹ hơn.”

### Slide 15 — Phân tích các trường hợp nhận diện sai

“Tin nhắc giữ kín OTP có thể bị cảnh báo dù mang ý nghĩa an toàn. Mẫu dụ cài ứng dụng lại có thể bị xếp bình thường. Điều này cho thấy mô hình chưa xử lý tốt mọi cách diễn đạt.”

“Để cải thiện, cần xem đóng góp đặc trưng, bổ sung mẫu có nhãn xác nhận và đánh giá lại trên dữ liệu tách biệt. Chỉ thêm một từ vào danh sách cảnh báo chưa đủ để chứng minh đã sửa được lỗi.”

**Chuyển sang demo:** “Em xin minh họa một lượt phân tích và một bộ mẫu trực tiếp trên hệ thống.”

### Slide 16 — Giới hạn và hướng hoàn thiện

“Bản hiện tại đã có quy trình huấn luyện, dự đoán, giải thích và phản hồi. Ưu tiên tiếp theo là dữ liệu có nhãn xác nhận, tập kiểm tra mới và giảm lỗi nhận diện. Việc mở rộng sang Zalo/email cần phép đánh giá riêng.”

Kết phần chuyên môn bằng một câu: “Hệ thống hỗ trợ sàng lọc nội dung, còn người dùng cần xác minh qua kênh chính thức.”

### Slide 17 — Cảm ơn

“Phần trình bày của em đến đây là kết thúc. Em cảm ơn thầy cô và các bạn đã lắng nghe. Em xin tiếp nhận câu hỏi và góp ý.”

Dừng lại để nghe câu hỏi, không tiếp tục giải thích thêm khi chưa cần.

## 23. Hướng dẫn demo trong khoảng 3 phút

### Chuẩn bị trước buổi báo cáo

- Mở đúng file slide mới nhất có 17 trang.
- Chạy thử ứng dụng trước giờ báo cáo, kiểm tra trang truy cập được.
- Chuẩn bị các tin mẫu đã ẩn danh trong một tệp văn bản.
- Tắt lưu lịch sử nếu không cần và tránh đưa dữ liệu cá nhân lên màn hình chiếu.
- Mở sẵn báo cáo kết quả để đối chiếu nếu giảng viên hỏi số liệu.
- Nếu cần ảnh demo dự phòng, chụp từ bản ứng dụng thực tế và ghi rõ đó là ảnh chụp, không gọi là đang chạy trực tiếp.

### Thực hiện demo

**Bước 1 — Phân tích một tin:** chọn SMS, nhập một tin mẫu và bấm phân tích. Giải thích nhãn và điểm, tránh chỉ nói “đây là kết quả”.

**Bước 2 — Xem giải thích:** chỉ ra một đặc trưng tác động tới điểm và một dấu hiệu từ khóa. Nói rõ hai phần có cách tạo khác nhau.

**Bước 3 — Kiểm tra bộ mẫu:** chuyển sang Kiểm tra nhiều mẫu, nhập ba dòng đã chuẩn bị, nhập nhãn minh họa tương ứng rồi phân tích. Giải thích khớp, chưa kết luận hoặc lỗi theo kết quả đang hiển thị.

Có thể dùng ba dòng sau để luyện demo trước:

```text
Nhóm mình học lúc 3 giờ chiều ở thư viện nha.
Chúc mừng bạn đã trúng thưởng. Nộp phí nhận quà ngay hôm nay.
Ngân hàng không bao giờ yêu cầu bạn cung cấp OTP. Hãy giữ kín mã xác thực và chỉ liên hệ tổng đài chính thức.
```

Nhãn kỳ vọng minh họa: `0,1,0`. Những nhãn này mô tả ý đồ của ví dụ tự soạn, không phải dữ liệu kiểm định đã xác nhận độc lập. Hãy chạy trước để biết kết quả thực tế; không hứa trước rằng cả ba tin đều được phân loại đúng.

**Bước 4 — Kết thúc demo:** giới thiệu chức năng tải báo cáo và hàng chờ duyệt. Không cần thực hiện mọi nút trong buổi trình bày nếu thời gian ít.

### Nếu demo bị lỗi

- Nếu trang không mở, kiểm tra máy chủ ứng dụng có đang chạy không.
- Nếu kết quả khác dự kiến, đọc đúng kết quả hiện tại và giải thích đó là trường hợp cần phân tích thêm.
- Nếu lỗi kỹ thuật chưa xử lý nhanh được, chuyển sang báo cáo đã chuẩn bị, nói rõ demo trực tiếp đang gặp lỗi.
- Không đổi nhãn mẫu hoặc sửa số liệu ngay tại chỗ chỉ để làm kết quả trông đúng hơn.

## 24. Cách trả lời câu hỏi của giảng viên

Trình tự nên dùng: **trả lời thẳng câu hỏi, đưa bằng chứng, nêu giới hạn nếu có**. Không cần mở đầu dài hoặc nhắc lại toàn bộ đề tài.

### “Hệ thống của em chỉ có dán chữ vào thôi sao?”

“Dán văn bản là đầu vào của nguyên mẫu. Phía sau có pipeline học máy, quy trình chọn cấu hình/ngưỡng, báo cáo đánh giá, giải thích và quản lý phản hồi. Em cũng đã bổ sung kiểm tra nhiều mẫu. Bản hiện tại chưa tự kết nối tài khoản để thu nhận tin.”

### “Vì sao em gọi là phát hiện lừa đảo khi nhãn có cả tin rác?”

“Bộ dữ liệu gộp rác và lừa đảo nên đầu ra hiện tại cũng gộp hai loại. Em cần ghi đúng là rác/lừa đảo và không suy diễn mọi cảnh báo thành lừa đảo tài chính. Muốn phân biệt riêng cần dữ liệu có nhãn chi tiết hơn.”

### “Sao bộ 12 mẫu có nhiều lỗi mà chỉ số test lại cao?”

“Hai bộ mẫu có phân bố và mục đích khác nhau. Bộ 12 ví dụ nhỏ có các tình huống khó để tìm lỗi. Kết quả cho thấy chỉ số trên bộ test có sẵn chưa đủ để bảo đảm khả năng tổng quát hóa. Em cần tập kiểm tra mới và nhiều mẫu có nhãn xác nhận hơn.”

### “Em đã chứng minh nguyên nhân sai do từ OTP chưa?”

“Em đã quan sát lỗi ở ví dụ có OTP, nhưng chỉ quan sát từ xuất hiện chưa đủ chứng minh nguyên nhân. Cần xem đóng góp đặc trưng và làm các phép thử đối chiếu để xác định yếu tố tác động.”

### “Hệ thống có tự học sau khi người dùng báo sai không?”

“Hiện chưa. Mẫu được duyệt và xuất để xem xét. Một lần huấn luyện mới cần kiểm tra dữ liệu, lưu phiên bản và đánh giá trước khi thay mô hình đang dùng.”

### “Em tự làm những phần nào?”

Trả lời đúng quá trình thực hiện của mình. Có thể giải thích vai trò trong lựa chọn bài toán, tìm hiểu dữ liệu, chạy và kiểm tra hệ thống, phân tích kết quả, tổ chức báo cáo và chỉnh sửa chức năng. Nếu có công cụ hỗ trợ tạo mã hoặc nội dung, trình bày trung thực khi được hỏi. Không nhận là tự viết toàn bộ mã nếu không đúng.

### Khi chưa biết câu trả lời

“Phần này em chưa kiểm chứng đầy đủ. Với phiên bản hiện tại, em mới xác nhận được … Em sẽ kiểm tra thêm bằng …”

Điền bằng điều thực sự biết và cách kiểm tra cụ thể. Không đưa ra số liệu hoặc khả năng của hệ thống theo suy đoán.

## 25. Nếu cần viết báo cáo thành văn bản

Có thể tổ chức thành các chương sau; điều chỉnh theo mẫu của trường:

| Phần | Nội dung nên có | Bằng chứng trong dự án |
|---|---|---|
| Mở đầu | Lý do chọn đề tài, mục tiêu, phạm vi và sản phẩm | proposal.md |
| Cơ sở lý thuyết | Phân loại văn bản, TF-IDF, SVM, các chỉ số | Giải thích phương pháp và tài liệu học thuật đã đọc |
| Phân tích và thiết kế | Người dùng, chức năng, luồng xử lý, lưu trữ | app.py và thiết kế hệ thống |
| Dữ liệu và thực nghiệm | Nguồn, nhãn, chia tập, cấu hình, cách chọn ngưỡng | DATASET.md, train.py |
| Cài đặt và giao diện | Các màn hình, hướng dẫn sử dụng, xử lý phản hồi | Ảnh chụp bản ứng dụng đang hoạt động |
| Kết quả và thảo luận | Chỉ số, ma trận nhầm lẫn, ví dụ sai, giới hạn | evaluation.json, RESULTS.md và kết quả bộ mẫu |
| Kết luận | Phần đạt được, phần còn thiếu, hướng phát triển | Đối chiếu mục tiêu với sản phẩm thực tế |
| Tài liệu tham khảo | Nguồn dữ liệu, tài liệu phương pháp và thư viện | Nguồn thực sự đã sử dụng, đúng quy cách trường yêu cầu |

Không lấy danh sách tài liệu tham khảo làm bằng chứng rằng đã đọc các tài liệu đó. Kiểm tra tác giả, năm, tiêu đề và nguồn trước khi nộp. Đưa các hình/bảng vào phần có giải thích tương ứng, đánh số và ghi nguồn.

## 26. Checklist trước khi báo cáo

- [ ] Họ tên sinh viên trên bìa đúng: Diệp Hải Nam.
- [ ] Tên và phạm vi đề tài khớp nội dung giảng viên đã duyệt.
- [ ] Hiểu vì sao chọn TF-IDF + SVM và cách mô hình tạo điểm.
- [ ] Phân biệt điểm SVM với xác suất, từ khóa với bằng chứng lừa đảo.
- [ ] Nhớ quy mô dữ liệu: 2.394 train, 597 test.
- [ ] Nhớ ma trận nhầm lẫn: 408, 31, 7, 151.
- [ ] Dùng số liệu hiện tại: Macro F1 0,9219, precision 82,97%, recall 95,57%.
- [ ] Bộ minh họa là 7/12 khớp nhãn, không phải 8/12 và không phải đánh giá độc lập.
- [ ] Không tuyên bố đã tích hợp tài khoản hoặc kiểm định Zalo/email.
- [ ] Demo dùng dữ liệu đã ẩn danh và đã chạy thử trước.
- [ ] Có thể giải thích ít nhất một cảnh báo nhầm và một trường hợp bỏ sót.
- [ ] Luyện nói theo thời lượng được giao, dành chỗ cho hỏi đáp.
