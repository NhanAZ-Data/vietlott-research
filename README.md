# Vietlott Data Collector

`vietlott-data-collector` là kho thu thập, chuẩn hóa và phát hành dữ liệu kết quả Vietlott để người khác dùng trong công cụ riêng của họ.

Đây là tên package/project mới. URL repository Git hiện vẫn là `NhanAZ-Data/vietlott-research`; có thể đổi tên repository từ xa sau khi kiểm tra các consumer đang dùng URL cũ.

Phạm vi duy nhất của project:

- đọc dữ liệu từ nguồn Vietlott và nguồn đối chiếu đã khai báo;
- chuẩn hóa kỳ quay, giải thưởng, luật giải và provenance;
- lưu kho làm việc SQLite/CSV;
- xuất snapshot CSV phân vùng, kiểm tra tính toàn vẹn và cập nhật tự động.

Project không chứa dự đoán, mô hình, backtest, phân tích thống kê, dashboard hay website. Các thư mục và workflow thuộc các phần đó đã được loại bỏ để toàn bộ công suất còn lại dành cho thu thập dữ liệu.

## Dữ liệu phát hành

Snapshot trong `datasets/` bao gồm:

- Mega 6/45 (`mega645`)
- Power 6/55 (`power655`)
- Lotto 5/35 (`lotto535`)
- Max 3D (`max3d`)
- Max 3D Pro (`max3dpro`)
- Max 4D (`max4d`)
- Keno (`keno`)
- Bingo18 (`bingo18`)

Các tệp quan trọng:

- `datasets/draws/<product>/...csv`: một dòng cho mỗi `(product, draw_id)`;
- `datasets/prizes/<product>/all.csv`: các dòng giải thưởng đã thu thập;
- `datasets/prize_rules.csv`: luật giải ổn định;
- `datasets/exclusions.csv`: các kỳ có thông báo trạng thái đặc biệt;
- `datasets/metadata/dataset-summary.json`: phạm vi và số dòng;
- `datasets/metadata/quality-report.json`: kiểm tra cấu trúc, nguồn và độ phủ;
- `datasets/metadata/snapshot-manifest.json`: hash và kích thước từng tệp.

`draw_status`, `validation_status` và các trường provenance phải được giữ nguyên khi xuất dữ liệu. Collector không tự suy ra kỳ bị thiếu từ mã số hoặc lịch dự kiến.

## Cài đặt và sử dụng

```powershell
git clone https://github.com/NhanAZ-Data/vietlott-research.git
cd vietlott-research
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Liệt kê sản phẩm được hỗ trợ:

```powershell
vietlott-data-collector products
```

Thu thập các kỳ mới vào kho SQLite/CSV:

```powershell
vietlott-data-collector collect `
  --products keno bingo18 `
  --output-dir data `
  --format parquet `
  --contact-email you@example.com
```

Chạy backfill lịch sử hoặc bỏ qua bảng giải thưởng khi cần tốc độ:

```powershell
vietlott-collector collect --products all --output-dir data --backfill
vietlott-collector collect --products all --output-dir data --without-prizes
```

Kiểm tra kho làm việc:

```powershell
vietlott-collector validate --output-dir data --format parquet
```

Để dùng snapshot đã phát hành bằng công cụ khác, ghép các phân vùng thành CSV:

```powershell
vietlott-repository-data hydrate --source-dir datasets --destination-dir data
```

Sau khi cập nhật kho làm việc, đóng gói lại và kiểm tra snapshot:

```powershell
vietlott-repository-data publish --source-dir data --destination-dir datasets
vietlott-repository-data validate --source-dir datasets
vietlott-repository-data audit --source-dir datasets
```

## Tài liệu cho người dùng dữ liệu

- [Nguồn và quy trình thu thập](docs/THU_THAP_DU_LIEU.md)
- [Hợp đồng dữ liệu](docs/DATA_DICTIONARY.md)
- [Chất lượng và provenance](docs/CHAT_LUONG_DU_LIEU.md)
- [Tự động cập nhật](docs/TU_DONG_CAP_NHAT.md)
- [Kiến trúc collector](docs/ARCHITECTURE.md)

`SOURCE_SURVEY.md` chỉ là đường dẫn tương thích tới tài liệu nguồn. Không có tài liệu hoặc artifact nào mô tả dự đoán hay phân tích trong project này.

## Tự động cập nhật

GitHub Actions chạy hai lịch thu thập: nhóm sản phẩm có tần suất cao và nhóm sản phẩm theo mốc giờ. Mỗi lượt:

1. khôi phục kho làm việc từ snapshot;
2. đọc nguồn chính thức, dùng nguồn đối chiếu khi nguồn chính thức không truy cập được;
3. đối chiếu một vùng kỳ gần nhất;
4. áp dụng ngoại lệ chính thức;
5. validate, audit và kiểm tra hồi quy chất lượng;
6. chỉ commit `datasets` khi dữ liệu hợp lệ thực sự thay đổi.

Không có workflow triển khai website hoặc sinh báo cáo phân tích.

## Nguồn và trách nhiệm

Collector ưu tiên các trang kết quả công khai của [Vietlott](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/) và lưu URL, thời điểm, trạng thái xác nhận cùng lịch sử nguồn. Khi cần, nguồn đối chiếu được ghi rõ trong `attributes_json`; dữ liệu không được nâng trạng thái chỉ vì URL có vẻ chính thức.

Repo không liên kết hoặc đại diện cho Vietlott. Người dùng dữ liệu tự kiểm tra điều khoản nguồn, quyền sở hữu trí tuệ và quy định áp dụng. Dữ liệu lịch sử là dữ liệu tham khảo, không phải tư vấn tài chính.

## Giấy phép

Mã nguồn phát hành theo MIT. Dữ liệu gốc vẫn chịu quyền và điều kiện của nguồn tương ứng.
