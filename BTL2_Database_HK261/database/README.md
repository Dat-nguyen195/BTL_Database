# SQL hỗ trợ backend BTL2

Đã hiện thực bộ cài mới phục vụ kiểm chứng phần TD trên MySQL 8.4.13: 23 bảng theo model.json, PK/FK/UQ/CHECK, năm cột sinh/UNIQUE, ThanhTien generated; sáu procedure nghiệp vụ, hai helper procedure, hai hàm nghiệp vụ/hai helper và trigger cho phạm vi API demo.

Không thay đổi baseline. SQL mới nằm trong các tệp đã phân công để backend có thể cài và kiểm tra thật; việc bổ sung này không tự xác nhận checklist/báo cáo của MD/BD/HT đã hoàn tất.

## Cài mới

Dùng tài khoản có quyền CREATE DATABASE/routine/trigger. CLI mặc định không xóa hay ghi đè database hiện có:

```bash
DB_OWNER_USER=root DB_OWNER_PASSWORD='<mật khẩu tại máy chạy>' DB_PORT=3306   apps/backend/.venv/bin/python scripts/bootstrap_backend.py --database quan_net_btl2 --create-app-user
```

Cung cấp DB_PASSWORD (mật khẩu runtime), DB_USER (mặc định quan_net_app) trong môi trường. Không ghi mật khẩu thật vào lệnh bàn giao; có thể nạp biến từ `.env` riêng. CLI này dành cho tài khoản quản trị có quyền tạo user/cấp quyền; không dùng runtime.

Thứ tự bộ cài: 01_schema → 02_constraints → 03_indexes → 07_functions → 06_procedures → 08_triggers → 04_seed. Bootstrap tạo DB utf8mb4_0900_as_cs, không tắt FK/CHECK. Một số DDL gây implicit commit nên lỗi cài đặt cần xem/sửa DB mới chưa hoàn chỉnh; không coi bootstrap là transaction DDL nguyên tử. Script demo tạo routine bằng quản trị nhưng đặt definer quan_net_owner chỉ có quyền trong DB; không thay log_bin_trust_function_creators.

Seed giả có tài khoản/vai và danh mục để tạo nghiệp vụ qua API; chưa là bộ seed bao phủ mọi bảng/lịch sử theo phần BD. Các tệp 05_queries vẫn là phạm vi BD; query backend thật hiện ở repositories và được đối chiếu bằng tests/integration.

## Quyền ứng dụng

Runtime chỉ SELECT, EXECUTE và INSERT vào bốn bảng nháp. Khóa hàng qua sp_khoa_dong (whitelist cố định), không có UPDATE ví/tồn hoặc DDL. Sáu routine chính/hai helper không tự START TRANSACTION/COMMIT/ROLLBACK. Tham số khóa ASCII/ascii_bin khớp schema.

## Kiểm chứng và giới hạn

Bộ test tạo DB/user ngẫu nhiên riêng, kiểm tra quyền thật, rollback, gửi lặp, tranh máy/tồn/ví và 1213/1205 thật. Xem evidence/app/TD_repair_verification.md. Trigger bảo vệ lịch sử và chuyển trạng thái trong luồng demo; API không hỗ trợ hủy/hoàn, tái phân loại hay quản trị tài khoản/ca. Chưa xác nhận bao phủ mọi BR của toàn nhóm hoặc mọi thao tác SQL quản trị. Q07 dùng ngày đặt đơn làm mốc bán do baseline thiếu thời điểm tiếp nhận.

Nếu đã có database khác, dùng migration được review riêng; không chạy lại CREATE TABLE/ALTER lặp trên dữ liệu hiện hữu. Bản cài mới được kiểm tra, chưa có cam kết migration cho các schema tự tạo bên ngoài.
