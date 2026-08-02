# Chất lượng dữ liệu và provenance

Chất lượng snapshot được kiểm tra ở ba lớp độc lập: cấu trúc bản ghi, nguồn quan sát và độ phủ kho. Kết quả được sinh vào `datasets/metadata/quality-report.json`.

## Kiểm tra cấu trúc

Collector kiểm tra:

- khóa `(product, draw_id)` và khóa dòng giải không trùng;
- đủ cột bắt buộc và JSON hợp lệ;
- mã kỳ, ngày, miền số, số lượng và tính duy nhất theo luật sản phẩm;
- liên kết giải thưởng không mồ côi;
- trạng thái kỳ và trạng thái giải thuộc enum đã biết;
- kích thước tệp không vượt giới hạn phát hành.

## Provenance

Mỗi dòng giữ `source_url`, `fetched_at` và các thuộc tính nguồn. `data_source` phân biệt nguồn chính thức, nguồn phụ và nguồn cộng đồng. `source_history` lưu quan sát cũ trước khi một bản ghi được cập nhật bởi nguồn ưu tiên.

`draw_status` không đồng nghĩa với nguồn chính thức. Một kỳ chỉ được đổi từ `confirmed` sang `not_confirmed`, hoặc ngược lại, khi có bằng chứng chính thức phù hợp.

## Độ phủ và khoảng trống

Quality report ghi số dòng, khoảng ngày, khoảng mã, trạng thái xác nhận, nguồn, số giải và các khoảng trống ứng viên. Khoảng trống chỉ là tín hiệu cần thu thập thêm; nó không được biến thành bản ghi giả.

## Lệnh kiểm tra

```powershell
vietlott-repository-data validate --source-dir datasets
vietlott-repository-data audit --source-dir datasets
```

Workflow còn so sánh report trước/sau để phát hiện giảm đột ngột về số dòng hợp lệ, nguồn chính thức hoặc đối chiếu. Các cảnh báo được lưu làm artifact của run để người khác có thể kiểm tra lại.
