# Hợp đồng dữ liệu

Tài liệu này mô tả snapshot trong `datasets/` và kho làm việc do collector tạo ra. Các trường được giữ để người dùng có thể tải, kiểm tra và tái sử dụng dữ liệu mà không cần biết nội bộ parser.

## Bố cục snapshot

| Đường dẫn | Nội dung |
| --- | --- |
| `datasets/draws/<product>/YYYY-MM.csv` | Kỳ quay của Keno và Bingo18, phân vùng theo tháng |
| `datasets/draws/<product>/all.csv` | Kỳ quay của các sản phẩm còn lại |
| `datasets/prizes/<product>/all.csv` | Các dòng giải thưởng |
| `datasets/prize_rules.csv` | Luật giải được chuẩn hóa |
| `datasets/exclusions.csv` | Ngoại lệ trạng thái có nguồn chính thức |
| `datasets/metadata/dataset-summary.json` | Số dòng, sản phẩm và khoảng ngày |
| `datasets/metadata/quality-report.json` | Kết quả kiểm tra dữ liệu |
| `datasets/metadata/snapshot-manifest.json` | Hash, kích thước và phiên bản collector |

Khóa của một kỳ quay là `(product, draw_id)`. Không được gộp các sản phẩm chỉ vì chúng có cùng mã kỳ.

## Bảng kỳ quay

Các cột trong `draws` luôn theo đúng thứ tự sau:

| Cột | Ý nghĩa |
| --- | --- |
| `product` | Mã chuẩn, ví dụ `mega645`, `keno` |
| `draw_id` | Mã kỳ quay, giữ số 0 ở đầu |
| `draw_date` | Ngày ISO theo lịch công bố |
| `draw_status` | `confirmed` hoặc `not_confirmed` |
| `result_json` | Kết quả chuẩn hóa theo sản phẩm |
| `attributes_json` | Thuộc tính bổ sung và lịch sử quan sát nguồn |
| `official_pdf_urls_json` | Danh sách PDF chính thức được tìm thấy |
| `source_url` | URL của quan sát được lưu |
| `prize_status` | Trạng thái thông tin giải: `complete`, `rules_available`, `empty`, `not_applicable` hoặc trạng thái chuyển tiếp |
| `validation_status` | Kết quả kiểm tra cấu trúc: `valid`, `warning` hoặc `unchecked` |
| `validation_warnings_json` | Cảnh báo không làm mất bản ghi |
| `fetched_at` | Thời điểm lấy dữ liệu UTC |

`result_json` là object JSON. Tập số thường có `numbers` và có thể có `special_numbers`; sản phẩm chữ số dùng `digits` hoặc các trường được parser ghi rõ. Không tự sửa JSON bằng tay nếu chưa chạy lại `validate`.

## Bảng giải thưởng

Khóa logic là `(product, draw_id, game_variant, prize_tier, winning_rule, prize_value_vnd)`.

| Cột | Ý nghĩa |
| --- | --- |
| `product`, `draw_id` | Liên kết về kỳ quay |
| `game_variant` | Biến thể hoặc bảng giải |
| `prize_tier` | Hạng giải được công bố |
| `winning_rule` | Điều kiện trúng |
| `winner_count` | Số người trúng; để trống nếu nguồn không nêu |
| `prize_value_vnd` | Giá trị giải bằng VND; để trống nếu nguồn không nêu |
| `details_json` | Cột gốc và vị trí bảng |
| `source_url`, `fetched_at` | Provenance của dòng |

Giá trị trống và số 0 không đồng nghĩa. Collector không điền số 0 khi nguồn để trống.

## Provenance và trạng thái

`attributes_json` có thể chứa `data_source`, `official_verification_status`, `secondary_source_url`, `consensus_sources`, `official_list_verified_at` và `source_history`. Đây là dấu vết nguồn, không phải đánh giá chất lượng thay thế cho `validation_status`.

- `draw_status=confirmed` chỉ nói kỳ được chấp nhận theo thông báo nguồn hiện có.
- `draw_status=not_confirmed` được giữ lại để không mất dấu vết, không bị xóa khỏi snapshot.
- `validation_status=valid` là kiểm tra tất định về mã, số lượng, miền giá trị và tính duy nhất.
- Nguồn phụ luôn được gắn nhãn chờ đối chiếu; nguồn chính thức có quyền ưu tiên khi cập nhật lại.

## Cách đọc an toàn

1. Đọc `snapshot-manifest.json` và kiểm tra hash nếu cần chứng minh phiên bản.
2. Đọc đúng cột bằng `dtype` chuỗi cho `product` và `draw_id` để giữ số 0 đầu.
3. Tôn trọng `draw_status`, `validation_status` và provenance thay vì suy đoán từ mã kỳ.
4. Dùng `vietlott-repository-data validate --source-dir datasets` trước khi phát hành bản sao.
