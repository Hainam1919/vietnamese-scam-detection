# Quy cách dữ liệu

Tạo CSV UTF-8 có hai cột tối thiểu:

```csv
text,label
"Ví dụ nội dung đã ẩn thông tin cá nhân",scam
"Ví dụ thông báo hợp lệ đã ẩn thông tin cá nhân",legitimate
```

Nhãn: `legitimate` (bình thường), `suspicious` (đáng ngờ nhưng chưa đủ căn cứ), `scam` (có căn cứ lừa đảo). Nếu nguồn chỉ có hai nhãn, giữ nguyên hai nhãn. Có thể lưu thêm `source`, `source_url`, `collection_date`, `annotator`, `notes` để truy xuất nguồn và kiểm soát chất lượng.

## Quy trình gán nhãn

1. Viết quy tắc và ví dụ nhãn trước khi gán hàng loạt.
2. Hai thành viên gán độc lập một mẫu con, thảo luận bất đồng và cập nhật hướng dẫn.
3. Lưu nguồn/căn cứ nhãn; chỉ có URL hoặc giọng điệu khẩn cấp chưa đủ kết luận lừa đảo.
4. Loại bản sao và kiểm tra mẫu gần trùng để tránh rò rỉ train/test.
5. Xóa/che OTP, số tài khoản, điện thoại, email, token URL và thông tin định danh.
6. Đánh dấu rõ dữ liệu tổng hợp/viết lại; không trộn với dữ liệu thật mà không ghi nhận.

## Nguồn khởi đầu cần thẩm định

Có thể khảo sát Vietnamese SMS Dataset công khai trên Hugging Face (được giới thiệu có 5.982 dòng) và nghiên cứu công bố bộ email rác tiếng Việt. Trước khi dùng, kiểm tra giấy phép, định dạng, cách gán nhãn và tính phù hợp; không mặc định dữ liệu công khai được phép tái phân phối.
