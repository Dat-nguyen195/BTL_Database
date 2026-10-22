# Checklist – Nguyễn Thành Đạt

- [ ] **TD-01 – Áp dụng hợp đồng API/DTO và kiến trúc đã chốt**
  - Làm tại: `docs/design/api_contract.md`, `docs/design/error_codes.md`, `docs/design/transactions.md`, `docs/design/architecture.md`, `apps/backend/src/routes/`.
  - Đọc quyết định kỹ thuật rồi lập route/DTO đúng /api/v1, trường nghiệp vụ và envelope đã ghi; đối chiếu tên/tham số CALL với routines_catalog.md. Triển khai theo hợp đồng, không chờ họp chọn lại API hoặc tầng commit.

- [ ] **TD-02 – Dựng backend và kết nối CSDL theo cấu hình môi trường**
  - Làm tại: `apps/backend/`.
  - Dùng Python 3.12, Flask 3.1.3 và mysql-connector-python 26.7.0; tạo entrypoint phục vụ UI và API cùng cổng 5000. Thêm requirements.in/requirements.lock khóa thư viện, cấu hình môi trường và README cài/chạy; thử kết nối MySQL 8.4.13 và đóng kết nối đúng cách.

- [ ] **TD-03 – Hiện thực API đọc máy, phiên, đơn, tồn và lịch sử ví**
  - Làm tại: `apps/backend/src/routes/`, `apps/backend/src/repositories/`.
  - Trả dữ liệu từ CSDL thật; lọc và phân trang có ví dụ; không dùng danh sách giả làm kết quả demo.

- [ ] **TD-04 – Hiện thực API mở/đóng phiên, nạp ví, nhận/thu đơn và ghi sổ kho**
  - Làm tại: `apps/backend/src/services/`.
  - Gọi đúng sáu thủ tục và thứ tự tham số đã chốt; service sở hữu transaction, không commit trong repository/routine. Bổ sung POST tạo đơn/phiếu nháp bằng SQL tham số, chụp giá/tính tổng tại server; chèn đầu và toàn bộ dòng nguyên tử, chưa trừ tiền/tồn khi tạo nháp.

- [ ] **TD-05 – Kiểm tra đầu vào, quyền thao tác và lỗi trả về**
  - Làm tại: `tests/api/`.
  - Dùng tham số truy vấn; từ chối dữ liệu sai/quyền sai; chứng minh lỗi không để dữ liệu cập nhật dở.

- [ ] **TD-06 – Tích hợp backend với UI và kiểm tra yêu cầu lặp**
  - Làm tại: `tests/e2e/`, `evidence/app/`.
  - Ba luồng demo chạy từ UI qua API xuống DB; gửi lặp không nhân đôi tiền/kho; HT cùng kiểm tra tranh chấp.

- [ ] **TD-07 – Viết phần backend và lưu bằng chứng chạy thật**
  - Làm tại: `docs/report/sections/03_backend.md`, `docs/design/architecture.md`, `evidence/app/`.
  - Có kiến trúc gọi DB, ví dụ API hợp lệ/lỗi, log đã bỏ thông tin bí mật và lệnh tái hiện.

- [ ] **TD-08 – Kiểm tra thủ tục cùng HT, sửa lỗi và bàn giao backend**
  - Làm tại: `apps/backend/`, `docs/design/api_contract.md`, `database/06_procedures/`.
  - Cùng HT chạy lại API ghi và đối chiếu hợp đồng giao dịch; sửa lỗi ở backend, chuyển lỗi SQL cho HT. Hướng dẫn người khác khởi động backend và giải thích một luồng ghi, một ca lỗi cùng liên hệ UC BTL1.

- [ ] **TD-09 – Hiện thực đăng nhập, session, CSRF và phân quyền tài nguyên**
  - Làm tại: `apps/backend/src/routes/`, `apps/backend/src/services/`, `tests/api/`, `docs/design/api_contract.md`.
  - Làm đủ bốn API auth, kiểm tra hash bằng Werkzeug và tài khoản HoatDong; đổi session/CSRF sau login, cookie HttpOnly/SameSite=Lax. Suy quyền từ hồ sơ/ChucVu và chủ phiên/đơn/ví; thử 401/403, tài khoản hai lớp con và Khoa/TamDung. Không dùng nhóm giá làm quyền.

- [ ] **TD-10 – Tạo service transaction và cơ chế retry thống nhất**
  - Làm tại: `apps/backend/src/services/`, `apps/backend/src/repositories/`, `tests/api/`, `docs/design/transactions.md`.
  - Một kết nối cho toàn thao tác ghi, +07:00, autocommit=False, READ COMMITTED; lấy hết result set CALL, commit sau hậu kiểm, mọi lỗi rollback. Repository không commit. Lỗi 1213/1205 rollback toàn bộ rồi retry tối đa hai lần với cùng mã/khóa; lỗi nghiệp vụ không retry.

- [ ] **TD-11 – Ánh xạ mã lỗi và chống lặp ở toàn bộ API ghi**
  - Làm tại: `apps/backend/src/services/`, `apps/backend/src/routes/`, `tests/api/`, `docs/design/error_codes.md`.
  - Dùng error_codes.md, requestId chỉ cho log; không lộ SQL/stack trace. Giữ mã tạo phiên/đơn/phiếu và nap:{UUID} khi retry, dùng gio:{MaPhien}/dv:{MaDonHang} cho thu ví. Cùng khóa khác nội dung trả 409, replay trả 200/meta.replayed; không trả thành công trước commit.

- [ ] **TD-12 – Kiểm soát hạn dùng trả trước và dừng phiên ở server**
  - Làm tại: `apps/backend/src/services/`, `tests/e2e/`, `evidence/app/`, `docs/design/transactions.md`.
  - Tính CanUseUntil theo ngân sách/công thức BTL1; mọi lệnh dùng phiên/đặt món kiểm tra hạn server. Sau chi ví cập nhật hạn dùng; worker mô phỏng gọi cùng service đóng ở mốc hạn đã cấp dù chạy muộn. Cùng HT thử gần hết tiền, chi đồng thời, nạp, qua ngày; ghi rõ đây là mô phỏng, chưa điều khiển máy vật lý.
