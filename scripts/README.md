# Công cụ dự án

Chạy từ gốc dự án. Các công cụ kết nối MySQL dùng Python trong `apps/backend/.venv`; cài thư viện từ `apps/backend/requirements-dev.lock` khi cần Playwright.

| Công cụ | Mục đích |
|---|---|
| `start_backend_demo.py` | Sinh cấu hình local, khởi động MySQL, cài database mới và chạy Flask/worker |
| `bootstrap_backend.py` | Cài schema/routine/seed và tài khoản hạn quyền; từ chối ghi đè database hiện có |
| `seed_demo_p12.py` | Nạp seed P1–2, không ghi đè bộ dữ liệu đã có hoặc chưa đầy đủ |
| `check_backend.py` | Đọc phiên bản, số bảng/routine, múi giờ và danh tính runtime |
| `submission_queries.py` | Đọc năm truy vấn báo cáo từ SQL chính thức |
| `benchmark_index.py` | Đo Q-P12-02 trên database tạm; lưu kế hoạch và số đo JSON |
| `capture_dbms_evidence.py` | Chạy 28 minh chứng SQL thật, lưu SQL/JSON, ảnh PNG và PDF giữ văn bản |
| `export_eer_vectors.py` | Xuất SVG đã kèm trong bộ nguồn thành PDF vector, không cần thư mục BTL1 bên ngoài |
| `build_latex_report.py` | Cập nhật nội dung LaTeX/SQL từ nguồn dự án và dữ liệu phân công JSON |
| `build_report_latex.sh` | Biên dịch XeLaTeX và cập nhật PDF bàn giao |
| `package_deliverables.py` | Tạo ZIP LaTeX và ZIP bàn giao, quét bí mật cấu hình, kiểm tra CRC/hash và ghi SHA256SUMS |

```bash
# Tạo lại minh chứng: cần MySQL và Chrome/Chromium
apps/backend/.venv/bin/python scripts/capture_dbms_evidence.py

# Cập nhật SQL/nội dung báo cáo rồi biên dịch
./scripts/build_report_latex.sh --refresh-sources

# Đóng gói bộ hiện tại
apps/backend/.venv/bin/python scripts/package_deliverables.py
```

Lượt chạy minh chứng/benchmark tạo database tạm và chỉ dọn database do chính lượt đó tạo. Cấu hình kết nối được đọc từ `.env` riêng; không đưa giá trị bí mật vào tài liệu hoặc mã nguồn.
