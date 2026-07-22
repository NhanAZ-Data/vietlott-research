# Nhật ký trial thất bại và cấu hình bị loại

Tài liệu này khóa cách đọc `backtest.trial_disposition_log` trong từng báo cáo
sản phẩm. Trường này tồn tại để không làm mất dấu các thử nghiệm âm hoặc các
cấu hình đã bị loại trước khi đánh giá cuối cùng.

## Phạm vi lưu giữ

Mỗi report complete phải có:

- `method = registered_trial_disposition_log`.
- `retention_policy = record_included_failed_and_rejected_backtest_configs`.
- `included_trials`: bản tóm tắt mọi trial đã chạy và đã đưa vào
  `multiple_testing_trials`.
- `rejected_configurations`: cấu hình bị loại trước phase đánh giá cuối.
- `included_trial_count`, `failed_trial_count`,
  `raw_unadjusted_winning_trial_count`, `adjusted_winning_trial_count`.
- `rejected_configuration_count` và `retained_record_count`.

`failed_trial_count` đếm mọi trial không đạt kết luận thắng sau hiệu chỉnh toàn
hệ thống. Vì vậy một trial có p thô nhỏ nhưng q toàn hệ thống không đạt vẫn được
lưu là thử nghiệm không thắng sau hiệu chỉnh.

## Cấu hình bị loại

Mỗi dòng trong `rejected_configurations` phải có:

- `config_id` và `label`.
- `disposition = rejected_before_final_evaluation`.
- `reason_code` và `reason`.
- `included_in_multiple_testing = false`.
- `evaluated_on_final_scope = false`.

Các cấu hình này không được chạy trên phase đánh giá cuối và không tham gia
Benjamini-Hochberg, nhưng vẫn được lưu để người đọc thấy chúng đã bị chặn vì lý
do phương pháp, ví dụ rò rỉ dữ liệu, thiếu độ phủ giải thưởng hoặc mục tiêu không
so sánh được giữa sản phẩm.

## Kiểm soát tự động

`finalize_backtests` validate `trial_disposition_log` trước và sau khi gắn
q-value toàn hệ thống. Lệnh tạo báo cáo sẽ dừng nếu:

- thiếu log hoặc thiếu danh sách cấu hình bị loại;
- số trial trong log không khớp `multiple_testing_trials`;
- trial trong log lệch `target_scope`;
- cấu hình bị loại không có lý do;
- số trial thất bại không khớp trạng thái sau hiệu chỉnh.

`manifest.backtest_summary.trial_disposition_validation` công bố trạng thái
validate toàn hệ thống và tổng số trial/cấu hình được giữ lại.
