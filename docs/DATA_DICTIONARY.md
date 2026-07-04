# Từ Điển Dữ Liệu Collector

Repo này xuất bản snapshot trong thư mục `datasets`. Tất cả CSV/JSON/JSONL trong
snapshot dùng UTF-8 và LF.

## `datasets/draws/<product>/*.csv`

Mỗi dòng là một kỳ quay hoặc một kết quả phát hành.

| Cột | Kiểu | Nội dung |
| --- | --- | --- |
| `product` | chuỗi | Mã sản phẩm, ví dụ `mega645`, `keno`, `bingo18` |
| `draw_id` | chuỗi | Mã kỳ quay giữ nguyên dạng nguồn |
| `draw_date` | ngày | Ngày quay theo múi giờ Việt Nam |
| `draw_status` | chuỗi | `confirmed` hoặc `not_confirmed` |
| `result_json` | JSON | Kết quả đã chuẩn hóa |
| `attributes_json` | JSON | Metadata nguồn, trạng thái đối chiếu và ghi chú |
| `official_pdf_urls_json` | JSON array | Link PDF/chứng từ chính thức nếu có |
| `source_url` | chuỗi | URL nguồn của dòng canonical |
| `prize_status` | chuỗi | Trạng thái dữ liệu giải thưởng |
| `validation_status` | chuỗi | `valid`, `warning` hoặc `unchecked` |
| `validation_warnings_json` | JSON array | Cảnh báo kiểm tra cấu trúc |
| `fetched_at` | timestamp | Thời điểm thu thập, có offset |

## `datasets/prizes/<product>/all.csv`

Mỗi dòng là một hạng giải của một kỳ.

| Cột | Kiểu | Nội dung |
| --- | --- | --- |
| `product` | chuỗi | Mã sản phẩm |
| `draw_id` | chuỗi | Mã kỳ quay |
| `draw_date` | ngày | Ngày quay |
| `tier` | chuỗi | Mã hoặc tên hạng giải |
| `tier_rank` | số | Thứ tự hạng giải |
| `winners` | số | Số giải trúng |
| `prize_value` | số | Giá trị tiền thưởng |
| `currency` | chuỗi | Đơn vị tiền tệ |
| `source_url` | chuỗi | Nguồn dữ liệu |
| `fetched_at` | timestamp | Thời điểm thu thập |

## Metadata

| Tệp | Nội dung |
| --- | --- |
| `datasets/exclusions.csv` | Kỳ cần loại khỏi phân tích mặc định |
| `datasets/prize_rules.csv` | Luật trả thưởng ổn định theo sản phẩm |
| `datasets/metadata/dataset-summary.json` | Tổng số dòng, số kỳ xác nhận và mốc cập nhật |
| `datasets/metadata/quality-report.json` | Chất lượng nguồn, độ phủ và provenance theo sản phẩm |
| `datasets/metadata/snapshot-manifest.json` | Kích thước, số dòng và SHA-256 của từng tệp snapshot |

## Provenance

`attributes_json.data_source` mô tả nguồn canonical. Các giá trị thường gặp:

- `official_vietlott`
- `secondary_source`
- `community_mirror`
- `gap_consensus`

`src/vietlott_collector/provenance.py` phân loại nguồn thành `official`,
`secondary`, `community` hoặc `unknown`, đồng thời tách mức xác minh như
`official_direct`, `official_verified_match`, `multi_source_consensus` và
`pending_official`.

## Quan Hệ Với Website

Repo web [NhanAZ-Data/vietlott-prediction-web](https://github.com/NhanAZ-Data/vietlott-prediction-web)
checkout repo này trong workflow build và đọc trực tiếp `datasets`. Collector không
commit `site/data` và không triển khai GitHub Pages.
