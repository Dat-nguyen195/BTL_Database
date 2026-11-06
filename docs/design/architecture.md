# Kiến trúc hệ thống

Trình duyệt → JavaScript `fetch('/api/v1/...')` → Flask routes → services → repositories/Connector-Python → MySQL 8.4.13/InnoDB. Flask phục vụ cả frontend và API tại `http://127.0.0.1:5000`; không có bước build giao diện hoặc frontend server riêng. Docker demo ánh xạ MySQL ra `127.0.0.1:13307`.

| Thành phần | Vị trí | Trách nhiệm |
|---|---|---|
| Giao diện | `apps/frontend/` | Màn hình đăng nhập, máy/phiên, ví/đơn, kho và báo cáo; CSRF, giữ mã yêu cầu khi gửi lại |
| Routes | `apps/backend/src/routes/` | HTTP/JSON, xác thực, kiểm tra đầu vào và mã lỗi |
| Services | `apps/backend/src/services/` | Quyền nghiệp vụ, một giao dịch trên một kết nối, khóa, chống lặp và retry |
| Repositories | `apps/backend/src/repositories/` | SQL tham số/CALL, đọc hết result set; không tự commit |
| Cơ sở dữ liệu | `database/` | 23 bảng, ràng buộc, chỉ mục, seed, truy vấn, procedure/function/trigger |
| Worker trả trước | `apps/backend/src/services/worker.py` | Đọc lại hạn dùng dưới khóa và quyết toán qua cùng service |

## Quyết định kỹ thuật

- Python 3.12, Flask 3.1.3, mysql-connector-python 26.7.0; dependency được khóa phiên bản trong `apps/backend/`.
- Giữ tên bảng/cột nghiệp vụ BTL1; dữ liệu Unicode dùng utf8mb4, mã định danh dùng ascii_bin. Tiền VND nguyên; thời gian kết nối +07:00, JSON ISO 8601 có múi giờ.
- Service sở hữu BEGIN/COMMIT/ROLLBACK; READ COMMITTED, autocommit=False. Routine và repository không tự chốt giao dịch.
- Signed session cookie HttpOnly/SameSite=Lax; CSRF cho API ghi. Quyền lấy từ người chơi/nhân viên và chủ tài nguyên; nhóm người dùng phục vụ nhóm giá.
- Runtime hạn quyền: SELECT/EXECUTE và INSERT các bảng nháp được cấp; không UPDATE trực tiếp ví/tồn. Giá/tổng/giờ giao dịch do server xác định.
- Khóa nghiệp vụ ổn định và đối chiếu nội dung phân biệt gửi lặp với xung đột. Deadlock/lock timeout có retry có giới hạn theo hợp đồng giao dịch.

## Phạm vi giao diện

Đăng nhập; mở/kết thúc phiên; xem/nạp ví; tạo/tiếp nhận/thanh toán đơn; tạo/ghi sổ phiếu kho; xem báo cáo. Client hiển thị số dư, giữ chỗ và khả dụng do server trả. Lỗi 401 yêu cầu đăng nhập; 403 thiếu quyền; 409 xung đột nghiệp vụ; 503 có thể gửi lại cùng mã yêu cầu.

Danh mục/tài khoản/ca trực được seed và đọc. Bản demo chưa có API hủy/hoàn, CRUD quản trị đầy đủ hoặc điều khiển máy vật lý; dùng một worker/process demo.

## Tài liệu liên quan

- [Lược đồ](schema_contract.md), [kế thừa BTL1](btl1_to_btl2.md), [ma trận quy tắc](rules_matrix.md).
- [API](api_contract.md), [mã lỗi](error_codes.md), [giao dịch](transactions.md).
- [Routine](routines_catalog.md), [truy vấn](query_catalog.md), [chỉ mục](index_catalog.md).
- Sơ đồ chỉnh sửa: [draw.io](backend_architecture.drawio), [SVG](backend_architecture.svg). Sơ đồ trong báo cáo dùng TikZ tại `docs/report/latex/diagrams/architecture.tex`.
- Kiểm chứng: `evidence/final_verification/`; cách chạy tại [runbook](../demo/runbook.md).
