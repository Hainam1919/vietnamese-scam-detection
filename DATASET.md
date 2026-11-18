# Dữ liệu và ghi công

**Bộ dữ liệu:** Vietnamese Quality-Assured SMS Scam Dataset  
**Nguồn:** https://huggingface.co/datasets/trannguyenthaituan/vietnamese_sms_dataset  
**Tệp dùng:** `data/train.csv` và `data/test.csv`, tải ngày 2026-10-15 từ nhánh `main`.  
**Quy mô:** train 2.394 mẫu; test 597 mẫu.  
**Nhãn nguồn:** `0` = hợp lệ/bình thường, `1` = rác/lừa đảo.  
**Giấy phép công bố:** Creative Commons Attribution 4.0 International (CC BY 4.0).

Tác giả mô tả tin nhắn được thu thập từ người đóng góp tự nguyện, ẩn danh bằng các token như `[PHONE]`, `[BANK_ACC]`, `[MONEY]`, `[NUMBER]`, `[TIME]`, `[DATE]`. Tập kiểm tra được nhà phát hành mô tả là tập độc lập nhằm hạn chế rò rỉ dữ liệu. Báo cáo của dự án vẫn cần nêu đây là mô tả từ nhà phát hành, không phải kiểm toán độc lập của nhóm.

## Ghi công

Tran, Nguyen Thai Tuan; Le, Hoang Khang; Nguyen, Minh Tai; Nguyen, Van Thang; Mai, Hoang Dinh. “Vietnamese SMS Dataset with Quality Assurance.” IEEE Access, 2026. Dataset card cung cấp trích dẫn BibTeX; nhóm cần kiểm tra và dùng trích dẫn chính thức mới nhất khi nộp báo cáo.

## Thay đổi trong dự án

Các tệp gốc `train.csv` và `test.csv` được giữ nguyên. Mã dự án huấn luyện mô hình và tạo báo cáo đầu ra; không phát hành lại dữ liệu đã biến đổi. Nếu nhóm chia sẻ lại các tệp dữ liệu, phải tuân thủ CC BY 4.0, ghi công, dẫn liên kết giấy phép và đánh dấu thay đổi nếu có.
