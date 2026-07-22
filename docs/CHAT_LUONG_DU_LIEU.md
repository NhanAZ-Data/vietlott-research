# Chất lượng dữ liệu và provenance

Ngày rà soát gần nhất là 15/06/2026.

Tài liệu này định nghĩa các trạng thái dữ liệu và giải thích cách đọc báo cáo
`datasets/metadata/quality-report.json`. Mục tiêu là tránh dùng một nhãn duy nhất
để trả lời nhiều câu hỏi khác nhau.

## Ba trục phải đọc riêng

| Trục | Giá trị chính | Câu hỏi được trả lời |
| --- | --- | --- |
| Xác nhận kỳ quay | `confirmed`, `not_confirmed` | Kỳ này có được đưa vào mẫu phân tích mặc định không |
| Hợp lệ cấu trúc | `valid`, `warning`, `unchecked` | Mã kỳ, ngày và kết quả có đúng cấu trúc luật chơi không |
| Provenance nguồn | `official`, `secondary`, `community`, `unknown` | Dòng chuẩn hiện có xuất phát từ loại nguồn nào |

`confirmed` không có nghĩa là repo đã đối chiếu trực tiếp dòng đó với Vietlott.
Một dòng có thể hợp lệ về cấu trúc nhưng chỉ đến từ nguồn phụ. Một dòng cũng có
thể đến từ nguồn chính thức nhưng chưa được đối chiếu độc lập với nguồn thứ hai.

## Mức xác minh nguồn

| Giá trị | Ý nghĩa |
| --- | --- |
| `official_direct` | Dòng có nhãn nguồn Vietlott trực tiếp |
| `official_verified_match` | Metadata cho thấy dòng chính thức khớp với quan sát đã có |
| `multi_source_consensus` | Ít nhất hai nguồn độc lập cùng xác nhận kết quả |
| `pending_official` | Nguồn phụ đang chờ đối chiếu với Vietlott |
| `single_secondary_source` | Hiện chỉ có một nguồn phụ hoặc mirror |
| `unknown` | Dấu vết lịch sử chưa đủ để phân loại |

URL có tên miền Vietlott không đủ để tự gắn nhãn `official`. Một số bộ dữ liệu
mirror lưu URL gốc của Vietlott dù dòng được nhập từ mirror. Vì vậy báo cáo chỉ
coi một dòng là nguồn chính thức khi metadata thể hiện điều đó.

## Chuyển trạng thái

- `confirmed` sang `not_confirmed` cần thông báo chính thức
- `not_confirmed` sang `confirmed` cần văn bản khôi phục hoặc xác nhận lại chính thức
- Giữ nguyên trạng thái không cần bằng chứng mới
- `unchecked` thuộc trục kiểm tra cấu trúc, không phải trạng thái xác nhận kỳ quay

Các quy tắc này được kiểm tra ở cả lớp thu thập và lớp phân tích trong
`src/vietlott_collector/provenance.py`, `src/vietlott_analytics/provenance.py`,
`tests/test_provenance.py` và `tests/test_analytics_io.py`.

## Báo cáo snapshot ngày 15/06/2026

Snapshot có 379.518 dòng kỳ quay và không có khóa kỳ trùng. Tất cả dòng có kết
quả, 379.488 dòng mang trạng thái cấu trúc `valid` và 30 dòng `unchecked`.

Keno có

- 284.713 dòng kết quả
- 30 kỳ có dòng giải thưởng chi tiết
- 15 dòng có dấu đối chiếu chính thức rõ ràng
- 97 dòng nguồn dự phòng đang chờ đối chiếu
- 75 mã kỳ cũ đã được quy trình lịch sử phân loại là không phát hành
- 48 khoảng mã gần cuối snapshot chưa có đủ bằng chứng để phân loại

Bingo18 có

- 88.669 dòng kết quả
- 30 kỳ có dòng giải thưởng chi tiết
- 958 dòng có nhãn nguồn chính thức
- 105 dòng nguồn dự phòng đang chờ đối chiếu
- 11.876 dòng legacy chưa có nhãn provenance đủ rõ
- 162 mã trống trong miền ID quan sát, hiện được giữ ở trạng thái chưa xác định

Các mã trống không tự động được gọi là kỳ bị thiếu. Chúng có thể là mã không
phát hành, kết quả công bố trễ hoặc dữ liệu chưa thu thập đủ.

## Vì sao Keno và Bingo18 chỉ có 30 kỳ giải thưởng

Đây là giới hạn phạm vi dữ liệu hiện tại, không phải 30 kỳ lịch sử duy nhất.

Lịch sử Keno và Bingo18 được khôi phục chủ yếu từ trang danh sách, archive và
mirror. Các nguồn này cung cấp kết quả quay nhưng không cung cấp đầy đủ bảng
người trúng và giá trị chi tiết cho mọi kỳ. Collector đánh dấu các kỳ lịch sử là
`rules_available` vì luật trả thưởng đã được lưu có cấu trúc. Chỉ các kỳ gần đây
được đọc từ trang chi tiết chính thức mới có các dòng giải cụ thể.

Vì vậy website và export phải tách

- độ phủ kết quả
- độ phủ dòng giải thưởng theo kỳ
- độ phủ luật trả thưởng

Không được dùng độ phủ kết quả 100 phần trăm để diễn giải rằng lịch sử giải thưởng
cũng đầy đủ.

## Audit và manifest

Chạy kiểm toán toàn bộ dữ liệu bằng

```powershell
vietlott-repository-data audit --source-dir datasets
vietlott-repository-data validate --source-dir datasets
```

Lệnh audit tạo

- `datasets/metadata/quality-report.json`
- `datasets/metadata/snapshot-manifest.json`

Manifest lưu hash SHA-256, kích thước và số dòng từng tệp CSV, khoảng ngày,
phiên bản parser, phiên bản từng nhóm phương pháp và commit tạo snapshot.

## Giới hạn còn lại

Các dòng legacy chỉ giữ bản ghi chuẩn cuối cùng, không giữ đầy đủ mọi phản hồi thô
từ từng nguồn. Vì vậy số xung đột lịch sử được ghi là không khả dụng, không phải
bằng 0.

Từ phiên bản này, quá trình đối chiếu giữ quan sát cũ trong
`attributes_json.source_history` trước khi thay bản ghi chuẩn bằng nguồn chính thức.
Độ phủ đối chiếu sẽ tăng dần ở các kỳ mới, nhưng không thể tái tạo hoàn toàn lịch
sử đã bị thiếu provenance nếu không thu thập lại nguồn.
