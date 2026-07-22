# Từ điển dữ liệu

Tài liệu này mô tả dữ liệu công khai trong `datasets` và các artifact phân tích
trong `site/data`. Mọi timestamp có offset `+00:00` được hiểu là UTC.

## Dữ liệu kỳ quay

Đường dẫn

- sản phẩm quay dày `datasets/draws/<product>/YYYY-MM.csv`
- sản phẩm còn lại `datasets/draws/<product>/all.csv`

Khóa logic là cặp `(product, draw_id)`.

| Trường | Kiểu | Ý nghĩa |
| --- | --- | --- |
| `product` | chuỗi | Mã sản phẩm chuẩn hóa |
| `draw_id` | chuỗi | Mã kỳ quay, giữ số 0 ở đầu |
| `draw_date` | ngày ISO | Ngày quay theo lịch Việt Nam |
| `draw_status` | enum | `confirmed`, `not_confirmed` hoặc trạng thái chuyển tiếp được tài liệu hóa |
| `result_json` | JSON object | Kết quả chuẩn hóa theo loại sản phẩm |
| `attributes_json` | JSON object | Thuộc tính bổ sung như nguồn dữ liệu, Jackpot và lịch sử nguồn |
| `official_pdf_urls_json` | JSON array | Danh sách PDF chính thức đã tìm thấy |
| `source_url` | URL | Trang hoặc endpoint dùng cho quan sát hiện tại |
| `prize_status` | enum | Mức độ đầy đủ của thông tin giải thưởng |
| `validation_status` | enum | Kết quả kiểm tra cấu trúc |
| `validation_warnings_json` | JSON array | Cảnh báo không làm mất bản ghi |
| `fetched_at` | datetime ISO | Thời điểm thu thập |

### Cấu trúc `result_json`

Sản phẩm tập số

```json
{
  "numbers": [2, 17, 33, 37, 38, 45],
  "special_numbers": []
}
```

Sản phẩm chuỗi chữ số có thể dùng `digits` hoặc `tiers` tùy cấu trúc công bố.
Lớp phân tích chuyển chúng thành danh sách chuỗi có độ dài cố định trước khi tính.

### Provenance dẫn xuất

Các trường dưới đây không ghi đè dữ liệu thô. Chúng được tính bởi
`src/vietlott_analytics/provenance.py`.

| Trường | Giá trị chính | Ý nghĩa |
| --- | --- | --- |
| `structural_validity` | `valid`, `invalid`, `unchecked` | Bản ghi có đúng schema và luật sản phẩm hay không |
| `source_origin` | `official`, `community`, `secondary`, `unknown` | Nguồn gốc quan sát |
| `source_verification` | `cross_checked`, `single_source`, `conflicted`, `unknown` | Mức đối chiếu giữa các quan sát |
| `status_evidence` | chuỗi | Bằng chứng dùng để giải thích trạng thái kỳ quay |

## Dữ liệu giải thưởng

Đường dẫn `datasets/prizes/<product>/all.csv`.

Khóa phân tích thường gồm `(product, draw_id, game_variant, prize_tier, row_index)`.

| Trường | Kiểu | Ý nghĩa |
| --- | --- | --- |
| `product` | chuỗi | Mã sản phẩm |
| `draw_id` | chuỗi | Mã kỳ quay |
| `game_variant` | chuỗi | Biến thể hoặc bảng giải |
| `prize_tier` | chuỗi | Tên hạng giải |
| `winning_rule` | chuỗi | Mẫu hoặc điều kiện trúng được công bố |
| `winner_count` | số nguyên rỗng được | Số lượng giải được báo cáo |
| `prize_value_vnd` | số nguyên rỗng được | Giá trị một giải bằng VND |
| `details_json` | JSON object | Cột gốc và vị trí bảng |
| `source_url` | URL | Nguồn của dòng giải |
| `fetched_at` | datetime ISO | Thời điểm thu thập |

Không suy diễn `winner_count = 0` khi nguồn để trống. Giá trị trống và số 0 có ý
nghĩa khác nhau.

## Dữ liệu khí tượng

Đường dẫn `datasets/weather/daily.csv`.

| Trường | Kiểu | Ý nghĩa |
| --- | --- | --- |
| `date` | ngày ISO | Ngày ghép với kỳ quay |
| `venue_id` | chuỗi | Mã địa điểm quay trong cấu hình |
| `venue_name` | chuỗi | Tên địa điểm |
| `address` | chuỗi | Địa chỉ công khai |
| `requested_latitude`, `requested_longitude` | số thực | Tọa độ yêu cầu |
| `grid_latitude`, `grid_longitude` | số thực | Ô lưới khí tượng thực tế |
| `temperature_2m_mean` | độ C | Nhiệt độ ngoài trời trung bình ngày |
| `temperature_2m_min`, `temperature_2m_max` | độ C | Nhiệt độ ngoài trời thấp nhất và cao nhất |
| `relative_humidity_2m_mean` | phần trăm | Độ ẩm tương đối trung bình ngày |
| `weather_model` | chuỗi | Mô hình tái phân tích, hiện là ERA5-Land |
| `source` | chuỗi | Dịch vụ cung cấp dữ liệu |

Đây là biến đại diện ngoài trời, không phải phép đo trong phòng quay.

## Sổ dự đoán

Đường dẫn `predictions/ledger.jsonl`. Mỗi dòng là một sự kiện JSON.

Sự kiện `prediction` lưu dự đoán trước kết quả

- `prediction_id`
- `product`
- `strategy`
- `model_version`
- `code_version`
- `generated_at` và timezone
- `dataset_cutoff_draw_id`, `dataset_cutoff_date` và timezone
- `dataset_fingerprint`
- `prediction`
- `parameters`

Sự kiện `evaluation` chỉ được nối thêm sau khi có kết quả

- `evaluation_id`
- `prediction_id`
- `evaluated_at`
- `actual_draw_id`
- `actual_draw_date`
- `actual_result`
- `metrics`

Mọi sự kiện đã niêm phong còn có `ledger_index`, `previous_event_hash` và
`event_hash`. `root_hash` trong `site/data/predictions.json` là hash của sự kiện
cuối.

`site/data/predictions.json` công bố baseline dự đoán theo từng sản phẩm:

- `outcome_summary.baseline_intervals` chứa khoảng dự đoán 95% cho số lượt
  `exact` và `near` dưới baseline đồng đều. Khoảng này dùng
  `poisson_binomial_exact_dp` trên xác suất riêng của từng lượt đã chấm.
- `baseline_summary.products.<slug>` giữ `score_kind`, `score_basis`,
  `expected_exact_by_chance`, `expected_near_by_chance`,
  `expected_score_by_chance`, `observed_score_sum` và `score_excess_vs_chance`.
- `strategy_baseline_comparisons` so sánh từng chiến lược với baseline trên cùng
  kỳ đích bằng chênh `observed_score - expected_score`.
- `outcome_summary.pooled_rate_suppressed` luôn là `true`: website không công bố
  tỷ lệ pooled giữa các trò chơi có không gian kết quả khác nhau.
- `minimum_evaluations_for_baseline_claim` là số lượt đã chấm tối thiểu trước khi
  website được phép công bố lợi thế của một chiến lược so với baseline.

## Artifact website

| Tệp | Nội dung |
| --- | --- |
| `site/data/manifest.json` | Tổng số và danh mục sản phẩm |
| `site/data/products/<slug>.json` | Báo cáo đầy đủ từng sản phẩm |
| `site/data/predictions.json` | Bản đọc của ledger và tổng kết dự đoán |
| `site/data/audit-summary.json` | Tổng kết fairness audit |
| `site/data/audit-log.jsonl` | Một dòng cho mỗi phép kiểm |
| `site/data/dataset-quality.json` | Chất lượng và provenance theo sản phẩm |
| `site/data/snapshot-manifest.json` | Hash và số dòng của snapshot |
| `site/data/analysis-export.json` | Gói phân tích hợp nhất |
| `site/data/analysis-export.schema.json` | JSON Schema của gói hợp nhất |

`analysis-export.json` không nhúng hàng trăm nghìn dòng kỳ quay. Trường
`raw_data_catalog` cung cấp đường dẫn, kích thước, số dòng và SHA-256 để phần mềm
khác tải đúng tệp thô.
