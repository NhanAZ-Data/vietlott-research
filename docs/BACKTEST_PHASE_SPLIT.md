# Tách phase chọn công thức và đánh giá cuối

Tài liệu này khóa cách đọc `backtest.phase_split` trong từng báo cáo sản phẩm.
Mục tiêu là tránh tối ưu quá mức: phần đầu của cửa sổ walk-forward chỉ dùng để
khóa/công bố công thức và kiểm tra chẩn đoán, còn kết luận backtest công bố dùng
riêng phase đánh giá cuối.

## Quy tắc chia phase

Mỗi report complete có `phase_split` gồm:

- `method = chronological_formula_selection_then_final_evaluation`: chia theo
  thứ tự thời gian, không xáo trộn kỳ quay.
- `walk_forward_target_draw_count`: tổng số kỳ walk-forward đã chạy qua cả hai
  phase.
- `selection_fraction = 0.5`: mặc định nửa đầu cửa sổ walk-forward là
  `selection_phase`.
- `selection_phase`: phase chọn/khóa công thức, có `scope_id`, `draw_count`,
  `first_draw_id`, `latest_draw_id` và `draw_ids_sha256`.
- `final_evaluation_phase`: phase đánh giá cuối, có cùng cấu trúc với
  `selection_phase`.
- `formulas_frozen_before_final_evaluation = true`: công thức phải được cố định
  trước khi đọc phase đánh giá cuối.
- `selection_result_used_to_choose_formulas = false`: kết quả selection phase
  không được dùng để chọn lại công thức cuối.
- `final_evaluation_feedback_used_for_model_selection = false`: kết quả phase
  cuối không được hồi tiếp vào chọn mô hình.

## Quan hệ với target_scope

`backtest.target_scope` hiện đại diện cho đúng phase đánh giá cuối. Vì vậy:

- `backtest.samples` phải bằng
  `backtest.phase_split.final_evaluation_phase.draw_count`.
- `backtest.target_scope.scope_id` phải bằng
  `backtest.phase_split.final_evaluation_phase.scope_id`.
- `backtest.target_scope.target_draw_ids_sha256` phải bằng hash danh sách kỳ
  của phase đánh giá cuối.
- `model`, `recent_model`, `audit_model`, `baseline`, `comparison`,
  `recent_comparison` và `audit_comparison` đều phải dùng chung target scope này.

## Kiểm soát tự động

`finalize_backtests` gọi kiểm tra phase trước khi hiệu chỉnh Benjamini-Hochberg.
Nếu thiếu `phase_split`, tổng số kỳ không khớp, phase cuối lệch `target_scope`,
hoặc công thức không được khóa trước phase cuối, lệnh tạo báo cáo sẽ dừng bằng
`ValueError`.

`manifest.backtest_summary.phase_split_validation` công bố trạng thái validate
toàn hệ thống, gồm số kỳ selection/final của từng sản phẩm và scope của phase
đánh giá cuối.
