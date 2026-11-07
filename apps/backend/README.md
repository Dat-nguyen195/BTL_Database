# Backend Flask

Backend `/api/v1` và giao diện demo cùng origin cổng 5000. Python 3.12, Flask 3.1.3, Connector/Python 26.7.0 (pure Python), Werkzeug 3.1.9; MySQL 8.4.13/InnoDB. Routes xử lý HTTP/CSRF, services kiểm tra quyền hiện tại và sở hữu transaction; repositories SQL tham số/CALL không commit.

## Chạy nhanh với Docker

Từ gốc `BTL2_Database_HK261`:

```bash
python3 -m venv apps/backend/.venv
apps/backend/.venv/bin/pip install -r apps/backend/requirements.lock
apps/backend/.venv/bin/python scripts/start_backend_demo.py
```

Mở **http://127.0.0.1:5000**. Lần đầu script tạo `.env` với khóa ngẫu nhiên, dựng MySQL từ `infrastructure/compose.backend.yaml` trên localhost:13307, cài DB mới và seed; những lần sau giữ dữ liệu hiện có. Không chạy lại bootstrap lên database đã tồn tại. Docker daemon cần đang hoạt động.

Tài khoản demo, cùng mật khẩu `MatKhau123!`: `admin` (QuanLy), `cashier1` (ThuNgan), `barista` (PhaChe), `player1`/`player2` (người chơi), `dual_user` (người chơi + ThuNgan). `locked_user` và `paused_user` dùng để kiểm tra từ chối. Đây là dữ liệu giả cho demo; đổi tài khoản khi dùng ngoài demo.

Giao diện tối thiểu hỗ trợ ba luồng để kiểm chứng tích hợp backend: phiên chơi; nạp ví/đơn dịch vụ; phiếu kho/báo cáo. Nút yêu cầu mới sinh mã mới, gửi lại giữ mã cũ.

## Dùng MySQL có sẵn

Tạo môi trường bằng `.env.example`, cung cấp SECRET_KEY riêng và DB_PASSWORD. SECRET_KEY thiếu/rỗng làm ứng dụng dừng khởi động. Chạy bộ SQL theo `database/README.md` bằng tài khoản cài đặt; runtime dùng tài khoản ứng dụng hạn quyền. Sau đó:

```bash
apps/backend/.venv/bin/python scripts/check_backend.py
apps/backend/.venv/bin/python apps/backend/run.py
```

Định dạng tiền/lượng JSON là integer đúng miền, không bool/float/chuỗi số. Thời gian ISO 8601 +07:00. Không nhận giá bán/tổng/người thực hiện/giờ giao dịch từ client. CSRF được cấp bởi GET `/auth/csrf`, đổi sau login và gửi trong X-CSRF-Token trên mọi API ghi. Danh tính/quyền được nạp từ DB mỗi request và kiểm tra lại trên kết nối transaction ghi.

## API và giao dịch

Đủ 26 route theo `docs/design/api_contract.md`: 4 auth, 14 đọc/báo cáo, 8 ghi. Sáu procedure nghiệp vụ, hai procedure nội bộ để khóa và hai hàm nội bộ hỗ trợ được ghi ở routines_catalog.md. Các routine là SQL SECURITY DEFINER; runtime chỉ SELECT, INSERT bốn bảng nháp và EXECUTE. Không cấp UPDATE ví/tồn cho runtime.

Mỗi thao tác ghi dùng một kết nối +07:00, autocommit=False/READ COMMITTED. Service đọc hết kết quả CALL, hậu kiểm, commit rồi trả response. Lỗi rollback toàn bộ. 1213/1205 retry tối đa hai lần sau lần đầu. UNIQUE mã nghiệp vụ được đọc lại sau rollback để phân biệt replay với xung đột nội dung; không coi mọi duplicate là thành công.

Hội viên dùng số dư ví làm ngân sách giờ còn có thể cấp từ đầu phiên; TienGiuCho chỉ là tiền giờ đã phát sinh. Mọi thay đổi số dư được khóa cùng phiên. Nạp sau khi hết hạn quyết toán phiên cũ tại hạn cũ trước khi cộng tiền. Worker đọc lại DB và khóa/kiểm tra lại hạn trước khi đóng; không có hạn chỉ lưu trong RAM. Worker nội bộ dùng capability riêng, actor SQL NULL, không giả tài khoản nhân viên. Vãng lai trả trước đóng bằng TienMat/TienNhan=0 từ HTTP; service dùng tiền nạp đã lưu, không thu lại.

## Kiểm tra

```bash
apps/backend/.venv/bin/pip install -r apps/backend/requirements-dev.lock
# Trỏ tới MySQL dành riêng cho test; tài khoản owner có quyền tạo/xóa DB và user tạm.
TD_TEST_DB_PORT=13307 apps/backend/.venv/bin/python -m pytest tests/api tests/integration tests/e2e -q
```

Có thể đặt TD_TEST_DB_HOST, TD_TEST_DB_OWNER, TD_TEST_DB_PASSWORD. Mỗi test tích hợp tạo DB `quan_net_test_<random>` và user riêng, dọn đúng tài nguyên đó sau test; không reset DB ứng dụng. Không có TD_TEST_DB_PORT thì các test cần MySQL được ghi SKIP. Test trình duyệt dùng Playwright 1.56.0 và Chrome/Chromium cài sẵn. Fault injection dùng cho kiểm tra retry/commit mất kết nối; các ca khóa/rollback/tiền/tồn còn lại chạy MySQL thật. Bằng chứng: `evidence/final_verification/summary.json`.

## Giới hạn

Ứng dụng mô phỏng quyền dùng phiên, chưa khóa máy vật lý. Chưa có API hủy/hoàn, thu công nợ trả sau, CRUD tài khoản/danh mục/ca. Q07 phân nhóm lượng bán theo ngày đặt đơn vì baseline không lưu mốc tiếp nhận; không dùng báo cáo này để khẳng định thời điểm xuất hàng chính xác khi đặt/tiếp nhận khác ngày. Các thao tác SQL quản trị ngoài API cần kiểm tra thêm theo toàn bộ quy tắc BTL1. Một worker và một process backend cho demo; không bật Flask reloader.
