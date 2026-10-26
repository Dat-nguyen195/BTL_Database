# Review lần 2 phần Nguyễn Thành Đạt — 26/10/2026

Bộ test hiện có: **78 passed**, 0 failure/error/skip, 267,42 giây, dùng MySQL 8.4.13 và Chrome thật. Xem [JUnit](TD_review2_existing_tests.xml).

Ba ca bổ sung: **3 failed**, 0 error/skip, 9,44 giây, tái hiện các lỗi cần sửa trong [mã probe](TD_review_round2_repro.py) và [JUnit probe](TD_review_round2_repro.xml):

| Ưu tiên | Lỗi đã tái hiện | Hướng sửa |
|---|---|---|
| P1 | Trả đơn của phiên cũ bỏ qua tiền giữ chỗ của phiên mới. Ví 100.000đ, phí phiên mới đã phát sinh 90.000đ, vẫn trả được đơn cũ 15.000đ; ví còn 85.000đ và hạn dùng lùi về trước hiện tại. | Mọi khoản trừ ví phải khóa và tính lại giữ chỗ của phiên đang hoạt động của chủ ví, dù đơn thuộc phiên nào; trả 409 INSUFFICIENT_FUNDS khi không đủ phần khả dụng. |
| P2 | Gửi lại mã phiếu NhapKho với loại KiemKe phát sinh int(None), trả 500 thay vì 409 IDEMPOTENCY_CONFLICT. | So loại phiếu trước khi chuyển kiểu các cột phụ thuộc loại. |
| P3 | page=100000000000000000000 tạo OFFSET vượt miền MySQL, trả 500. | Giới hạn page/offset tại helper phân trang; trả 422 INVALID_INPUT khi vượt miền. |

Vị trí: `apps/backend/src/services/order_service.py`, `database/06_procedures/02_wallet_orders.sql`, `apps/backend/src/services/inventory_service.py`, `apps/backend/src/routes/read_routes.py` (đường dẫn tính từ gốc dự án).

Chưa sửa ba lỗi này trong lần cập nhật GitHub. Cần xử lý P1 trước nghiệm thu. TD-08 vẫn còn bước review/bàn giao trực tiếp với HT. Kết quả 78 test đạt không bao phủ ba tình huống lỗi bổ sung.

Chạy từ thư mục BTL2_Database_HK261 sau khi cài dependency dev và chuẩn bị MySQL test riêng:

```bash
TD_TEST_DB_PORT=13306 apps/backend/.venv/bin/python -m pytest tests/api tests/integration tests/e2e -q
PYTHONPATH=tests TD_TEST_DB_PORT=13306 apps/backend/.venv/bin/python -m pytest -p conftest evidence/app/review_round2/TD_review_round2_repro.py -q -s
```

Mỗi test tạo database/user ngẫu nhiên và tự dọn. Probe dùng clock kiểm soát để mô phỏng 6 giờ; SQL/CALL và thao tác HTTP chạy thật. Ba assertion đang thất bại là bằng chứng lỗi, không phải kết quả nghiệm thu đạt. PDF gốc và cấu hình .env chỉ giữ trên máy, theo quy định repo công khai.
