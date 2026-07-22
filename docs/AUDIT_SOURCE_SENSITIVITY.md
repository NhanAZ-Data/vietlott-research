# Độ nhạy khi loại từng nguồn dữ liệu

Tài liệu này khóa cách đọc `source_leave_one_out` trong tham số của phép kiểm
`digit_position_chi_square`. Mục tiêu là xem tín hiệu vị trí chữ số có phụ thuộc
quá mạnh vào một nguồn, parser, mirror hoặc vùng provenance cụ thể hay không.

## Phạm vi áp dụng

`source_leave_one_out` áp dụng cho các sản phẩm chuỗi chữ số khi observation có
thông tin nguồn từ `attributes_json.data_source`, hoặc fallback theo host trong
`source_url` nếu dữ liệu cũ chưa gắn `data_source`.

Phiên bản hiện tại chạy trên cùng lát dữ liệu với `source_breakdown`, gồm các
outcome có độ dài hợp lệ và chỉ chứa chữ số. Kết quả nằm trong
`digit_position_chi_square.parameters.source_leave_one_out`.

## Cách đọc

Trường `baseline` là kiểm định vị trí chữ số trên toàn bộ dữ liệu dùng được.
Mỗi dòng trong `excluded_sources` loại một nguồn rồi tính lại thống kê trên phần
còn lại.

Mỗi dòng có:

- `excluded_source_key`, `excluded_source_label`: nguồn bị loại.
- `excluded_draws`, `excluded_outcomes`: số kỳ và outcome của nguồn bị loại.
- `remaining_draws`, `remaining_outcomes`: lát dữ liệu còn lại sau khi loại nguồn.
- `sample_status`: `usable` khi phần còn lại có tối thiểu 30 kỳ; `too_small` khi
  mẫu còn lại quá nhỏ.
- `statistic`, `statistic_delta`: chi-square sau khi loại nguồn và chênh lệch so
  với baseline.
- `effect_size`, `effect_size_delta`, `relative_effect_shift`: độ lớn hiệu ứng
  sau khi loại nguồn, chênh lệch tuyệt đối và chênh lệch tương đối so với baseline.
- `max_abs_standardized_residual`: residual tuyệt đối lớn nhất của lát còn lại.
- `top_residuals`: các ô vị trí và chữ số nổi bật nhất sau khi loại nguồn.

`strongest_effect_shift` tóm tắt nguồn có `effect_size_delta` tuyệt đối lớn nhất
trong các lát còn đủ mẫu. Nếu không có lát đủ mẫu, trường này dùng dòng mô tả
mạnh nhất còn lại và phải đọc với trạng thái `too_small`.

## Không tạo kiểm định mới

`source_leave_one_out.no_new_p_values` luôn là `true`. Bảng này không sinh
p-value, q-value hoặc trạng thái thống kê mới. Nó chỉ là kiểm tra độ nhạy của
một kiểm định đã có, nhằm trả lời câu hỏi: nếu bỏ một nguồn dữ liệu, tín hiệu mô
tả còn ổn định hay biến mất.

Nếu `effect_size_delta` lớn hoặc trạng thái là `limited_comparison`, ưu tiên rà
parser, provenance, mapping hạng giải và nguồn mirror trước khi diễn giải thống
kê. Nếu tín hiệu chỉ còn khi giữ một nguồn nhỏ, đó là dấu hiệu cần kiểm tra dữ
liệu trước, không phải bằng chứng về tính ngẫu nhiên của quay số.
