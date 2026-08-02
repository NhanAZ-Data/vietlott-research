# Nguồn và quy trình thu thập

Collector ưu tiên trang kết quả công khai của Vietlott. Mỗi quan sát được lưu cùng URL, thời điểm lấy, trạng thái xác nhận, trạng thái giải thưởng và dấu vết nguồn.

## Nguồn chính

- [Mega 6/45](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-645)
- [Power 6/55](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-655)
- [Lotto 5/35](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-535)
- [Max 3D](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-max-3D)
- [Max 3D Pro](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-max-3Dpro)
- [Max 4D](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-max-4d)
- [Keno](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-keno)
- [Bingo18](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-bingo18)

Trang đầu chứa các kỳ gần nhất. Các trang tiếp theo được đọc qua AjaxPro khi cần; trang chi tiết được dùng để lấy bảng giải và PDF nếu có. Khóa AjaxPro được đọc động từ HTML, không lưu cứng.

## Nguồn đối chiếu

Khi HTML và AjaxPro chính thức đều không truy cập được, collector có thể đọc trang kết quả công khai của [Xổ Số Minh Ngọc](https://xosominhngoc.net.vn/kqxs-vietlott). Parser yêu cầu đúng mã kỳ, ngày, số lượng kết quả và cấu trúc giải; chỉ một điều kiện sai là từ chối toàn bộ trang.

Bản ghi từ nguồn đối chiếu phải có provenance trong `attributes_json`, gồm nguồn, URL và trạng thái chờ đối chiếu. Khi nguồn Vietlott hoạt động lại, collector đọc lại và thay thế thông tin nguồn phụ.

## Keno và Bingo18

Hai sản phẩm tần suất cao có collector lịch sử riêng. Khoảng trống mã kỳ chỉ được bổ sung khi có quan sát độc lập đủ cấu trúc; mã bị thông báo không phát hành được ghi vào `datasets/exclusions.csv` hoặc giữ với `draw_status=not_confirmed`. Không suy ra kết quả từ mã trước và sau.

## Quy trình một lượt

1. Khôi phục CSV từ `datasets` vào SQLite.
2. Đọc nguồn chính thức và các trang mới hoặc vùng cần đối chiếu.
3. Chạy parser, validation và upsert theo khóa.
4. Nếu nguồn chính thức lỗi, thử nguồn đối chiếu theo chính sách rate limit.
5. Áp dụng ngoại lệ chính thức và lưu lịch sử nguồn cũ.
6. Xuất CSV, tạo metadata và kiểm tra snapshot.
7. Chỉ phát hành dữ liệu nếu `validate` không có lỗi.

## Giới hạn truy cập

HTTP client dùng retry, backoff, jitter và tôn trọng `Retry-After`. Không tăng tốc độ để vượt giới hạn nguồn. Nếu HTML thay đổi bất thường, parser dừng và ghi lỗi thay vì đoán dữ liệu.
