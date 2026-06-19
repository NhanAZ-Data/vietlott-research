# Tự Động Cập Nhật Dataset

GitHub Actions trong repo này chỉ cập nhật dữ liệu và metadata trong `datasets`.
Website được build ở repo riêng sau khi checkout snapshot này.

## Workflow

`update-fast.yml` chạy cho Keno và Bingo18.

`update-scheduled.yml` chạy cho Mega 6/45, Power 6/55, Lotto 5/35, Max 3D và
Max 3D Pro.

Cả hai workflow gọi `update-dataset.yml` với danh sách sản phẩm tương ứng.

## Các Bước Chính

1. Checkout repo và đồng bộ `origin/main`.
2. Cài package collector.
3. Lưu metadata trước cập nhật vào artifact chẩn đoán.
4. Hydrate `datasets` sang thư mục làm việc `data`.
5. Chạy `vietlott-auto-update` với retry, jitter và strict validation.
6. Publish ngược từ `data` về `datasets`.
7. Chạy `vietlott-repository-data validate`.
8. Chạy `vietlott-repository-data audit`.
9. So sánh quality report trước/sau bằng `scripts/check_quality_regressions.py`.
10. Upload artifact chẩn đoán.
11. Đồng bộ lại `origin/main`, apply patch dữ liệu nếu main đã tiến.
12. Commit `datasets` nếu có thay đổi.

Nếu không có kỳ mới hoặc thay đổi chính thức, workflow không tạo commit.

## Kết Nối Với Web Repo

Repo web
[NhanAZ-Drops/vietlott-prediction-web](https://github.com/NhanAZ-Drops/vietlott-prediction-web)
có workflow riêng chạy theo lịch và thủ công. Workflow đó checkout repo này vào
`_data_repo`, đọc `_data_repo/datasets`, sinh lại `site/data`, chạy test web và
deploy Pages.

Thiết kế này giữ repo collector ổn định: collector không cần quyền Pages, không
commit artifact web, và không phụ thuộc vào code phân tích/dự đoán.
