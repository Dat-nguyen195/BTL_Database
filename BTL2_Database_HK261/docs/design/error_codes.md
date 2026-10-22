# Mã lỗi dùng chung – đã chốt

TD ánh xạ mã sang HTTP, HT dùng cùng mã khi SIGNAL; TT hiển thị thông báo theo `error.code`, không phân tích chuỗi thông báo SQL. `requestId` là mã log mỗi HTTP request, khác khóa chống lặp nghiệp vụ.

| error.code | HTTP | MYSQL_ERRNO cho SIGNAL | Ý nghĩa / cách xử lý |
|---|---|---|---|
| INVALID_INPUT | 422 | 60001 | Sai kiểu, miền, số tiền/lượng hoặc tham số; sửa dữ liệu nhập. |
| NOT_FOUND | 404 | 60002 | Đối tượng không tồn tại. |
| FORBIDDEN | 403 | 60003 | Không đủ vai trò/quyền trên tài nguyên. |
| MACHINE_UNAVAILABLE | 409 | 60004 | Máy không AVAILABLE; tải lại danh sách. |
| ACTIVE_SESSION_EXISTS | 409 | 60005 | Máy/hội viên đã có phiên đang hoạt động. |
| INSUFFICIENT_FUNDS | 409 | 60006 | Không đủ số dư khả dụng sau giữ chỗ. |
| INSUFFICIENT_STOCK | 409 | 60007 | Thiếu tồn ít nhất một dòng; toàn bộ thao tác bị rollback. |
| INVALID_STATE | 409 | 60008 | Chuyển trạng thái hoặc hình thức thu không hợp lệ. |
| IDEMPOTENCY_CONFLICT | 409 | 60009 | Cùng khóa/mã đối tượng nhưng nội dung nghiệp vụ khác. |
| INVENTORY_SNAPSHOT_STALE | 409 | 60010 | Ảnh kiểm kê không khớp tồn hiện tại; kiểm kê lại. |
| IMMUTABLE_DOCUMENT | 409 | 60011 | Chứng từ/dòng đã chốt, không cho sửa/xóa. |
| INVALID_WALLET_OWNER | 403 | 60012 | Ví không thuộc chủ phiên/đơn. |
| ACCOUNT_INACTIVE | 403 | 60013 | Tài khoản Khoa/TamDung. |
| PREPAID_EXPIRED | 409 | 60014 | Đã hết hạn dùng trả trước; không cấp thêm quyền dùng/đặt dịch vụ. |
| DEPENDENCY_CONFLICT | 409 | 60015 | Khóa tham chiếu/quan hệ hiện có không cho thao tác. |
| UNAUTHENTICATED | 401 | — | Chưa đăng nhập hoặc đăng nhập thất bại. |
| CSRF_INVALID | 403 | — | Token CSRF thiếu/sai; lấy lại ngữ cảnh đăng nhập. |
| BAD_JSON | 400 | — | JSON không đọc được. |
| TX_RETRY_EXHAUSTED | 503 | — | Deadlock/lock timeout còn sau retry; người dùng có thể thử lại với cùng mã nghiệp vụ. |
| DATABASE_UNAVAILABLE | 503 | — | Không kết nối được DB; không hiển thị dữ liệu giả thay thế. |
| INTERNAL_ERROR | 500 | — | Lỗi ngoài hợp đồng; log theo requestId, không trả SQL/mật khẩu/stack trace. |

HT dùng `SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60006, MESSAGE_TEXT='INSUFFICIENT_FUNDS'` (thay mã tương ứng). Không bắt rồi nuốt lỗi hoặc tự commit phần đã chạy.

TD xử lý lỗi MySQL 1213/1205 theo transactions.md. Với 1062: nhận diện tên UNIQUE; uq_phien_may_active/uq_phien_nguoi_active → ACTIVE_SESSION_EXISTS; các khóa ví/mã nghiệp vụ → đọc lại kết quả sau rollback và kiểm tra replay, khác nội dung → IDEMPOTENCY_CONFLICT. Không coi mọi duplicate đều là thành công. FK 1451/1452 → DEPENDENCY_CONFLICT; CHECK/NOT NULL/kiểu dữ liệu sai → INVALID_INPUT nếu là lỗi đầu vào đã biết, còn lại log INTERNAL_ERROR để sửa mã.

Ví dụ trả lỗi:

```json
{"ok":false,"error":{"code":"INSUFFICIENT_STOCK","message":"Không đủ tồn cho đơn hàng.","details":{"MaDichVu":"DV01"}},"requestId":"7da354d1-9d78-4cae-9443-5c0514baa9e0"}
```

Chi tiết trả ra chỉ chứa trường nghiệp vụ người gọi được phép xem. Tất cả lỗi ghi dữ liệu phải đi kèm rollback toàn bộ transaction trước khi trả response.
