# Tự động cập nhật dữ liệu

Workflow lịch chỉ là lịch thăm dò; collector không tạo kỳ chỉ vì đồng hồ đến giờ.

## Lịch hiện tại

- `update-fast.yml`: Keno và Bingo18 trong các khung phát hành dày.
- `update-scheduled.yml`: Mega 6/45, Power 6/55, Lotto 5/35, Max 3D và Max 3D Pro sau các mốc công bố.
- Max 4D được giữ như dữ liệu lịch sử và chỉ thu thập khi chạy thủ công.

Các mốc lịch có thể thay đổi; nguồn chính thức có giá trị cao hơn tài liệu này.

## Một lần chạy

1. Checkout `main` và cài package.
2. `hydrate` snapshot vào kho SQLite.
3. Chạy `vietlott-auto-update` cho nhóm sản phẩm.
4. Nếu nguồn chính thức lỗi, thử nguồn đối chiếu được khai báo.
5. `publish`, `validate`, `audit` và kiểm tra hồi quy chất lượng.
6. Đồng bộ lại `main` để tránh ghi đè một lần chạy khác.
7. Commit `datasets` nếu và chỉ nếu snapshot hợp lệ thay đổi.

Báo cáo JSON của lượt chạy được lưu trong thư mục tạm của Actions; dữ liệu lâu dài chỉ là `datasets` và metadata đã kiểm tra.

## Chịu lỗi

- Kết quả trễ: lượt sau đọc lại vùng gần nhất.
- Nhiều kỳ xuất hiện: collector tiếp tục qua các trang cho tới vùng đã biết.
- Kỳ hủy hoặc sản phẩm dừng: không tạo bản ghi giả.
- Mạng lỗi: retry, backoff, jitter và `Retry-After`.
- HTML thay đổi: parser dừng với lỗi để sửa có kiểm soát.
- Một sản phẩm lỗi: phần hợp lệ của sản phẩm khác vẫn được giữ, sau đó workflow báo đỏ.

Không có workflow build/deploy website hoặc sinh artifact dự đoán/phân tích.
