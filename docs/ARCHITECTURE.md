# Kiến Trúc Collector

Repo này chỉ chịu trách nhiệm thu thập và xuất bản snapshot dữ liệu Vietlott.

```text
nguồn công khai
  -> parser theo sản phẩm
  -> store làm việc trong data/
  -> publish snapshot datasets/
  -> validate/audit metadata
  -> commit datasets trên main
```

## Thành Phần

- `src/vietlott_collector/sources`: client đọc nguồn chính thức và nguồn dự phòng.
- `src/vietlott_collector/parsers`: parser HTML/API thành bản ghi chuẩn.
- `src/vietlott_collector/storage.py`: lưu store SQLite/CSV làm việc.
- `src/vietlott_collector/incremental_update.py`: cập nhật tăng dần theo sản phẩm.
- `src/vietlott_collector/repository_data.py`: hydrate/publish/validate/audit
  snapshot `datasets`.
- `src/vietlott_collector/quality.py`: sinh metadata chất lượng và manifest hash.

## Workflow

- `update-fast.yml`: cập nhật Keno và Bingo18 trong khung phát hành dày.
- `update-scheduled.yml`: cập nhật các sản phẩm quay theo mốc giờ.
- `update-dataset.yml`: workflow dùng chung cho hydrate, update, publish, validate,
  audit, upload artifact chẩn đoán và commit `datasets`.
- `ci.yml`: lint, unit test và validate snapshot.

## Ranh Giới Repo

Repo này không chứa website dự đoán, backtest, fairness audit hoặc GitHub Pages.
Các phần đó nằm tại
[NhanAZ-Data/vietlott-prediction-web](https://github.com/NhanAZ-Data/vietlott-prediction-web)
và đọc dữ liệu từ snapshot của repo này.
