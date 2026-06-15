# Báo cáo lần dự đoán đúng Bingo18 kỳ 0171884

## Kết quả quan sát

- Sản phẩm `bingo18`
- Kỳ quay `0171884`
- Ngày quay 14/06/2026
- Kết quả thật `231`
- Chiến lược `recent_frequency`
- Dự đoán đã lưu `231`
- Mã dự đoán `302775a7f15a0c0972ca39bc`
- Dữ liệu được khóa tại kỳ `0171883`
- Thời điểm sinh dự đoán `14/06/2026 14:28:43 UTC`
- Phiên bản mô hình `1.0.0`
- Hash sự kiện đánh giá
  `34340ec8702f57b627c2d9badd2dd16c5ca7fbbc6004ef1c6931d1f8aa7b325c`

Dự đoán đã tồn tại trước khi kết quả kỳ `0171884` được ghi vào ledger. Chuỗi hash
hiện tại cho phép phát hiện việc sửa nội dung lịch sử sau khi ledger đã được niêm
phong.

## Xác suất nền

Baseline hiện tại mô hình hóa Bingo18 bằng ba vị trí, mỗi vị trí nhận một chữ số
từ 1 đến 6. Có `6^3 = 216` chuỗi có thể xảy ra.

Xác suất một dự đoán cố định đúng toàn bộ là

```text
P(đúng toàn bộ) = 1 / 216 = 0,00462963 = 0,462963%
```

Chiến lược `recent_frequency` đã có 10 lượt được đối chiếu và đúng 1 lượt. Nếu
tạm giả định 10 kỳ độc lập và mỗi dự đoán có xác suất nền `1/216`, xác suất có ít
nhất một lần đúng là

```text
1 - (215 / 216)^10 = 0,0453436 = 4,53436%
```

Số lần đúng kỳ vọng sau 10 lượt là `10 / 216 = 0,0462963`. Quan sát 1 lần đúng
cao hơn kỳ vọng mô tả, nhưng chưa hiếm đến mức đủ để kết luận chiến lược có lợi
thế dự báo.

## Phạm vi nhiều chiến lược

Tại snapshot này, Bingo18 có 32 lượt dự đoán đã đối chiếu trên 8 kỳ quay độc lập
và 4 chiến lược. Tổng kết là

- 1 lượt đúng toàn bộ
- 0 lượt gần đúng theo quy tắc nghiêm
- 31 lượt sai
- 8 lượt có trùng một phần
- 23 lượt không trùng vị trí nào

Không được dùng trực tiếp công thức độc lập cho cả 32 lượt vì nhiều chiến lược
cùng dự đoán một kỳ và cùng học từ một lịch sử. Các lượt đó có tương quan. Con số
`1 - (215 / 216)^32 = 13,7993%` chỉ là mốc tham khảo ngây thơ, không phải p-value
hợp lệ của toàn hệ thống.

## Kết luận

Đây là một lần dự đoán đúng có dấu vết và đáng được lưu, nhưng chưa phải bằng
chứng rằng `recent_frequency` tốt hơn cách chọn đồng đều. Kết luận chỉ nên thay
đổi khi số kỳ ngoài mẫu tăng lên, mọi lần thử đều được tính và chiến lược thắng
baseline bằng phép so sánh đã đăng ký trước.

Nguồn tái kiểm tra

- `predictions/ledger.jsonl`
- `site/data/predictions.json`
- `src/vietlott_analytics/predictions.py`
- `tests/test_prediction_ledger.py`
