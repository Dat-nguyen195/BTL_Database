# Cài mới và tổng duyệt BTL2 P1–2

Từ thư mục giải nén `BTL2_L09_Nhom10`:

```bash
python3 -m venv apps/backend/.venv
apps/backend/.venv/bin/pip install -r apps/backend/requirements.lock
apps/backend/.venv/bin/python scripts/start_backend_demo.py
```

Docker cần đang chạy. Script tạo `.env` riêng với mật khẩu ngẫu nhiên và database `quan_net_btl2`; database mới có cả seed P1–2. Mở http://127.0.0.1:5000, đăng nhập `admin` / `MatKhau123!` (tài khoản demo giả). Những lần sau giữ nguyên database; không reset dữ liệu. Muốn dựng lại toàn bộ minh chứng, dùng database mới riêng.

Với MySQL đã có, tạo `.env` riêng theo `.env.example`. Nạp biến môi trường trước khi chạy bộ cài bằng tài khoản quản trị được cấp quyền tạo database/user; không ghi giá trị mật khẩu vào tài liệu:

```bash
set -a
. ./.env
set +a
apps/backend/.venv/bin/python scripts/bootstrap_backend.py --database quan_net_btl2_moi --create-app-user --p12
```

Dùng đúng DB_HOST/DB_PORT/DB_OWNER_USER/DB_OWNER_PASSWORD tại máy chạy. Nếu dùng database `quan_net_btl2_moi`, cập nhật DB_NAME trong cấu hình runtime. Với bản cũ chưa có dữ liệu P1–2, script `seed_demo_p12.py` chỉ nạp khi không trùng mã, không ghi đè bộ dữ liệu một phần.

## Demo SQL

1. Chạy `database/05_queries/01_operations.sql` rồi `02_reports.sql`. Q04: TK03 có 1 ca/5 giờ; Q05: TK09 có 250.000đ trên seed sạch.
2. Chạy ba thủ tục KHU_VUC: thêm KV99 → sửa → thử xóa KV01 bị chặn FK → xóa KV99 thành công.
3. Trigger: thử sửa/xóa biên lai BL_P12_01 bị chặn; trên đơn nháp mới, thêm/sửa/xóa chi tiết làm tổng thay đổi tương ứng. Trên đơn đã chốt, các thao tác bị từ chối.
4. Gọi hai thủ tục báo cáo và hai hàm với ca đúng/sai như các tệp `.sql` trong `evidence/dbms/`. Mỗi ảnh có tệp JSON kết quả tương ứng.

## Demo giao diện

- Phiên chơi: chọn máy → mở phiên → kết thúc → đối chiếu biên lai và máy AVAILABLE.
- Ví/dịch vụ: nạp ví → gửi lại cùng mã không cộng lần hai → tạo/tiếp nhận/thanh toán đơn → đối chiếu ví và tồn.
- Kho/báo cáo: phiếu nháp chưa đổi tồn → ghi sổ → gửi lại không đổi tồn lần hai → chọn khoảng ngày chứa dữ liệu vừa tạo khi xem doanh thu.

## Kiểm thử

```bash
apps/backend/.venv/bin/pip install -r apps/backend/requirements-dev.lock
set -a
. ./.env
set +a
export TD_TEST_DB_HOST="$DB_HOST" TD_TEST_DB_PORT="$DB_PORT"
export TD_TEST_DB_PASSWORD="$MYSQL_ROOT_PASSWORD"
apps/backend/.venv/bin/python -m pytest tests -q
```

Chrome/Chromium cần có sẵn cho ca trình duyệt. Các test tạo database/user ngẫu nhiên và dọn tài nguyên riêng, không reset database demo. Kiểm tra kết quả không SKIP trước tổng duyệt. Cả nhóm cần biết giải thích SQL, ca từ chối và tác động trước/sau. Tên bài và hạn nộp thực tế theo LMS của lớp.
