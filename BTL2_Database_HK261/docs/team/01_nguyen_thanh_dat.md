# Checklist – Nguyễn Thành Đạt (2410709)

- [x] **TD-01 – Áp dụng hợp đồng API/DTO và kiến trúc đã chốt**
  - Làm tại: `docs/design/api_contract.md`, `docs/design/error_codes.md`, `docs/design/transactions.md`, `docs/design/architecture.md`, `apps/backend/src/routes/`.
  - Đọc quyết định kỹ thuật rồi lập route/DTO đúng /api/v1, trường nghiệp vụ và envelope đã ghi; đối chiếu tên/tham số CALL với routines_catalog.md. Đã bổ sung cơ chế tái dựng CanUseUntil khi khởi động lại và ngữ cảnh worker trong transactions.md.

- [x] **TD-02 – Dựng backend và kết nối CSDL theo cấu hình môi trường**
  - Làm tại: `apps/backend/`.
  - Đã dựng hoàn chỉnh kiến trúc phân tầng trong `apps/backend/src/` (app factory `app.py`, cấu hình `config.py`, kết nối `db.py`, lỗi `errors.py`, entrypoint `run.py`). Đã tạo `requirements.in` và `requirements.lock` khóa đúng Flask 3.1.3, mysql-connector-python 26.7.0, Werkzeug 3.1.9 trên Python 3.12.3; README chi tiết cách cài/chạy tại cổng 5000; minh chứng tại `evidence/app/TD-02_backend_startup.md`.

- [x] **TD-03 – Hiện thực API đọc máy, phiên, đơn, tồn và lịch sử ví**
  - Làm tại: `apps/backend/src/routes/read_routes.py`, `apps/backend/src/repositories/`.
  - Đã hiện thực đủ 14 API đọc và báo cáo Q01–Q08 với SQL tham số hóa, phân trang page/pageSize, lọc ngày FromDate/ToDate, lọc quyền tại server; tính phí hiện tại và CanUseUntil theo giờ server; doanh thu loại trừ nạp ví theo BR-16; minh chứng tại `evidence/app/TD-03_read_apis_and_reports.md`.

- [x] **TD-04 – Hiện thực API mở/đóng phiên, nạp ví, nhận/thu đơn và ghi sổ kho**
  - Làm tại: `apps/backend/src/services/`, `apps/backend/src/routes/write_routes.py`.
  - Đã hiện thực đủ 8 API ghi; gọi Stored Procedure qua CALL adapter; service sở hữu transaction. Đơn nháp và phiếu nháp được tạo nguyên tử, chụp giá/tồn từ DB, không ghi đè cột sinh GENERATED và không trừ tiền/tồn khi tạo nháp; minh chứng tại `evidence/app/TD-04_write_apis_and_drafts.md`.

- [x] **TD-05 – Kiểm tra đầu vào, quyền thao tác và lỗi trả về**
  - Làm tại: `tests/api/`.
  - Đã viết bộ kiểm thử tự động toàn diện trong `tests/api/` (`test_auth.py`, `test_read_validation.py`, `test_write_and_idempotency.py`, `test_transactions_and_retries.py`, `test_prepaid_and_worker.py`), kiểm tra kỹ lưỡng phân trang, định dạng ngày, quyền hạn vai trò và trả mã lỗi HTTP chuẩn. Có 78 ca kiểm thử riêng biệt đạt sau sửa lỗi, dùng MySQL/Chrome thật theo evidence/app/TD_repair_verification.md; fault injection được ghi rõ.

- [x] **TD-06 – Tích hợp backend với UI và kiểm tra yêu cầu lặp**
  - Làm tại: `tests/e2e/`, `evidence/app/`.
  - Đã kiểm chứng ba luồng HTTP/MySQL trong `tests/e2e/test_e2e_scenarios.py` và Chrome/UI/HTTP/MySQL trong `tests/e2e/test_browser_flows.py`; thử nghiệm gửi lặp không nhân đôi tiền/kho; minh chứng tại `evidence/app/TD-06_e2e_three_scenarios.md`.

- [x] **TD-07 – Viết phần backend và lưu bằng chứng chạy thật**
  - Làm tại: `docs/report/sections/03_backend.md`, `evidence/app/`.
  - Đã hoàn thiện toàn bộ báo cáo phần backend tại `docs/report/sections/03_backend.md` gồm liên hệ BTL1, thiết kế kiến trúc, kết quả chạy và bảng tổng hợp kiểm thử; lưu đầy đủ 8 file minh chứng chi tiết trong `evidence/app/`.

- [ ] **TD-08 – Kiểm tra thủ tục cùng HT, sửa lỗi và bàn giao backend**
  - Làm tại: `apps/backend/`, `docs/team/01_nguyen_thanh_dat.md`, `TASKS.json`.
  - Đã kiểm tra kỹ thuật chữ ký CALL, transaction và các luồng ghi trên MySQL thật; có hướng dẫn chạy/bộ test/minh chứng để bàn giao. Review chéo trực tiếp với HT và xác nhận người khác chạy lại chưa được thực hiện thay người đó; giữ mở bước phối hợp này.

- [x] **TD-09 – Hiện thực đăng nhập, session, CSRF và phân quyền tài nguyên**
  - Làm tại: `apps/backend/src/routes/auth_routes.py`, `apps/backend/src/services/auth_service.py`, `apps/backend/src/auth.py`.
  - Hiện thực đủ 4 API auth (`/auth/csrf`, `/auth/login`, `/auth/me`, `/auth/logout`), xác thực hash mật khẩu Werkzeug, chỉ cho tài khoản HoatDong, rotate token CSRF sau login, session signed cookie HttpOnly/SameSite=Lax. Quyền truy cập suy từ DB (NGUOI_CHOI, NHAN_VIEN.ChucVu) và quan hệ sở hữu tài nguyên; minh chứng tại `evidence/app/TD-09_auth_csrf_matrix.md`.

- [x] **TD-10 – Tạo service transaction và cơ chế retry thống nhất**
  - Làm tại: `apps/backend/src/services/transaction.py`, `tests/api/test_transactions_and_retries.py`.
  - Mỗi thao tác ghi sở hữu 1 connection riêng, +07:00, autocommit=False, READ COMMITTED. Đọc hết result set CALL, service commit một lần sau hậu kiểm, lỗi rollback toàn bộ. Bắt lỗi deadlock 1213/lock timeout 1205 rollback toàn bộ và retry tối đa 2 lần với cùng khóa/mã; lỗi nghiệp vụ không retry; hết lượt trả 503 TX_RETRY_EXHAUSTED; minh chứng tại `evidence/app/TD-10_transaction_retry_deadlock.md`.

- [x] **TD-11 – Ánh xạ mã lỗi và chống lặp ở toàn bộ API ghi**
  - Làm tại: `apps/backend/src/errors.py`, `apps/backend/src/services/`, `evidence/app/TD-11_replay_and_idempotency.md`.
  - Ánh xạ đầy đủ SIGNAL 60001–60015 và lỗi MySQL sang HTTP status và envelope chuẩn. Chống gửi lặp bằng mã nghiệp vụ và khóa nap:{UUID}, gio:{MaPhien}, dv:{MaDonHang}. Cùng khóa cùng nội dung trả 200 replayed=true; khác nội dung trả 409 IDEMPOTENCY_CONFLICT; requestId phục vụ log nội bộ, không lộ SQL/stack trace.

- [x] **TD-12 – Kiểm soát hạn dùng trả trước và dừng phiên ở server**
  - Làm tại: `apps/backend/src/services/session_service.py`, `apps/backend/src/services/worker.py`, `tests/api/test_prepaid_and_worker.py`.
  - Triển khai công thức số học nguyên $t_{\max} = \lfloor \frac{3600 \times (B + 1) - 1}{g} \rfloor$, tính chính xác CanUseUntil; kiểm tra hạn dùng trước mọi thao tác dùng phiên / đặt món; worker daemon ngầm quét và kết thúc phiên tại đúng mốc hạn CanUseUntil đã cấp mà không tăng phí do worker trễ; hỗ trợ tái dựng hạn dùng khi backend khởi động lại; minh chứng tại `evidence/app/TD-12_prepaid_can_use_until_worker.md`.


Kết quả sau sửa lỗi: [minh chứng kỹ thuật](../../evidence/app/TD_repair_verification.md). Các checkbox hiện phản ánh kỹ thuật đã kiểm tra; TD-08 giữ mở cho bước review/bàn giao trực tiếp với thành viên nhóm, không xác nhận giả cuộc review đã diễn ra.
