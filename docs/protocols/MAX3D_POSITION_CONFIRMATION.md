# Giao thức tái kiểm tra tín hiệu vị trí Max 3D

Trạng thái `đăng ký trước cục bộ`. Giao thức chỉ có hiệu lực công khai sau khi
commit chứa file này được push. Không dùng các kỳ nằm trước commit công khai làm
dữ liệu xác nhận.

## Mục tiêu

Kiểm tra trên dữ liệu tương lai xem phân bố chữ số theo ba vị trí của Max 3D và
Max 3D Pro có lệch đủ mạnh khỏi mô hình đồng đều hay không.

Đây là phép xác nhận thống kê. Nó không xác định nguyên nhân, không kiểm toán máy
quay và không tự chứng minh quy trình vận hành có vấn đề.

## Mốc khám phá bị khóa

Snapshot dữ liệu có SHA-256 của manifest

```text
bc8ca2e203e7e0317ec3f37f162a1105c1f3ec52e28aa5dd533e252b2cc6e58f
```

Max 3D

- cutoff kỳ `01092`, ngày 12/06/2026
- p khám phá `0,00000058`
- q toàn hệ thống `0,00004118`
- Cohen's w `0,034814`

Max 3D Pro

- cutoff kỳ `00739`, ngày 13/06/2026
- p khám phá `0,00013377`
- q toàn hệ thống `0,00474883`
- Cohen's w `0,037527`

Các con số trên chỉ là dữ liệu khám phá và không được cộng vào mẫu xác nhận.

## Mẫu xác nhận

Mỗi sản phẩm dùng 300 kỳ `confirmed` đầu tiên sau cutoff tương ứng. Với cấu trúc
hiện tại có 20 chuỗi ba chữ số mỗi kỳ, một sản phẩm dự kiến cung cấp 18.000 quan
sát vị trí-chữ số.

Chỉ dùng bản ghi

- có đủ ba chữ số cho mỗi kết quả
- chữ số nằm trong 0 đến 9
- hợp lệ theo parser đã công bố
- không bị đánh dấu xung đột nguồn chưa giải quyết

Không thay thế kỳ bị loại bằng dữ liệu trước cutoff. Nếu cấu trúc sản phẩm hoặc
parser thay đổi, phải công bố amendment trước khi xem kết quả kiểm định của mẫu
xác nhận.

## Phép kiểm chính

Với mỗi sản phẩm, lập ba bảng tần suất chữ số 0 đến 9 theo vị trí. Kỳ vọng của mỗi
ô là tổng số chuỗi hợp lệ của vị trí đó chia 10.

Thống kê chính

```text
chi_square = tổng((quan_sát - kỳ_vọng)^2 / kỳ_vọng)
df = 3 × (10 - 1) = 27
w = sqrt(chi_square / tổng_số_quan_sát_vị_trí)
```

Hai sản phẩm tạo thành một họ xác nhận. Dùng Bonferroni với
`alpha_mỗi_sản_phẩm = 0,025`.

Một sản phẩm chỉ được gọi là "xác nhận sai lệch thực dụng" khi đồng thời

- p nhỏ hơn `0,025`
- Cohen's w lớn hơn hoặc bằng `0,05`

Nếu chỉ đạt một điều kiện, báo cáo phải dùng đúng nhãn "nổi bật thống kê nhưng
hiệu ứng nhỏ" hoặc "hiệu ứng đạt ngưỡng nhưng chưa đủ thống kê".

## Phân rã thứ cấp

Residual chuẩn hóa và đóng góp chi-square của toàn bộ 30 ô sẽ được công bố, không
chỉ các ô lớn nhất.

Ô vị trí 3, chữ số 6 đang dương mạnh ở cả hai tập khám phá. Hướng này được ghi
trước để đọc khả năng tái lập, nhưng không phải tiêu chí xác nhận chính và không
được thay bằng một ô khác sau khi có dữ liệu tương lai.

## Độ ổn định theo thời gian

Sau khi đủ 300 kỳ, chia mẫu xác nhận thành hai khối 150 kỳ không chồng lấn.

- báo cáo Cohen's w riêng từng khối
- báo cáo residual của toàn bộ ô trong từng khối
- không tính lại cutoff để tối đa hóa chênh lệch
- không tuyên bố ổn định nếu tín hiệu tổng chỉ đến từ một khối

Phân tích hai khối là kiểm tra độ nhạy. Tiêu chí xác nhận chính vẫn dùng toàn bộ
300 kỳ theo công thức đã khóa.

## Quy tắc dừng và công bố

- Không kiểm định sớm trước 300 kỳ
- Có thể công bố tiến độ số kỳ nhưng không công bố p tạm thời
- Không kéo dài mẫu chỉ vì kết quả ở 300 kỳ chưa đạt ngưỡng
- Công bố cả kết quả xác nhận, bác bỏ và không đủ dữ liệu
- Lưu snapshot, hash, phiên bản parser, phiên bản phương pháp và toàn bộ mã chạy

## Tiêu chí bác bỏ giả thuyết tái lập

Tín hiệu khám phá được xem là chưa tái lập nếu tại mốc 300 kỳ sản phẩm không đạt
đồng thời p nhỏ hơn `0,025` và Cohen's w ít nhất `0,05`.

Kết quả chưa tái lập không chứng minh dữ liệu hoàn toàn ngẫu nhiên. Nó chỉ nói
rằng sai lệch khám phá không đạt tiêu chí xác nhận đã khóa.
