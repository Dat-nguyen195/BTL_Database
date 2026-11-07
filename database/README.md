# Cơ sở dữ liệu

MySQL 8.4.13/InnoDB; giữ 23 bảng nghiệp vụ từ BTL1. SQL nguồn được chia theo thứ tự công việc:

| Thư mục | Nội dung |
|---|---|
| `00_bootstrap/` | Khởi tạo database và cấu hình ký tự |
| `01_schema/` | 23 bảng, PK/UNIQUE/CHECK và cột sinh |
| `02_constraints/` | Khóa ngoại |
| `03_indexes/` | Chỉ mục cho các truy vấn vận hành |
| `04_seed/` | Danh mục/tài khoản demo và dữ liệu P1–2 |
| `05_queries/` | Truy vấn vận hành và tổng hợp Q-P12-01..05 |
| `06_procedures/` | Phiên, ví/đơn, kho, CRUD khu vực và báo cáo |
| `07_functions/` | Hàm nghiệp vụ và hai hàm P1–2 |
| `08_triggers/` | Trạng thái/lịch sử và tổng tiền đơn từ chi tiết |

## Cài mới

Cách thuận tiện nhất: chạy `scripts/start_backend_demo.py` theo README gốc. Với MySQL đã có, nạp cấu hình riêng từ `.env` rồi dùng tài khoản có quyền tạo database/user/routine/trigger:

```bash
set -a
. ./.env
set +a
apps/backend/.venv/bin/python scripts/bootstrap_backend.py --database quan_net_btl2_moi --create-app-user --p12
```

CLI từ chối ghi đè database đã tồn tại. Thứ tự cài: schema → constraints → indexes → functions → procedures → triggers → seed. DDL có thể implicit commit; database cài lỗi cần được kiểm tra riêng, không coi bootstrap là giao dịch DDL nguyên tử.

Seed P1–2 có hai đơn DH_P12_01/DH_P12_02 và dữ liệu liên quan. Trên seed sạch, Q04 trả TK03 một ca/năm giờ; Q05 trả TK09 số dư 250.000đ. Chạy `scripts/seed_demo_p12.py` lần hai giữ nguyên bộ dữ liệu đầy đủ và từ chối bộ dữ liệu một phần.

## Giao dịch và quyền

Service giữ ranh giới giao dịch; routine không tự COMMIT/ROLLBACK. Runtime chỉ SELECT/EXECUTE và INSERT các bảng nháp được cấp, không UPDATE ví/tồn trực tiếp. Mã định danh dùng ASCII/ascii_bin; dữ liệu Unicode utf8mb4; thời gian kết nối +07:00, READ COMMITTED.

Thiết kế chi tiết ở `docs/design/`; ca kiểm tra tại `tests/sql/`, `tests/integration/` và `tests/api/`. Minh chứng cuối tại `evidence/final_verification/` và `evidence/dbms/`.

Bộ cài dành cho database mới. Nâng cấp database bên ngoài cần migration riêng. API demo chưa bao gồm hủy/hoàn hoặc CRUD quản trị đầy đủ; không suy diễn rằng mọi thao tác SQL quản trị đều đã được bảo vệ/kiểm thử bởi API.
