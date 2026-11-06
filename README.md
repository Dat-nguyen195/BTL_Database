# BTL2 — Hệ thống quản lý quán Net

Hệ Cơ sở dữ liệu (CO2013), học kỳ 261 · L09 · Nhóm 10
**GVHD: ThS. Trần Thị Quế Nguyệt**

MySQL 8.4.13 / InnoDB · Python 3.12 / Flask 3.1.3 · HTML/CSS/JavaScript.

[Báo cáo PDF](deliverables/BTL2_L09_Nhom10_P1_P2.pdf) · [Nguồn LaTeX](docs/report/latex/main.tex) · [Hướng dẫn demo](docs/demo/runbook.md) · [Yêu cầu bài tập](docs/requirements/requirements.md)

## Nội dung bài làm

- Lược đồ 23 bảng kế thừa BTL1, PK/FK/UNIQUE/CHECK, chỉ mục và dữ liệu mẫu Phần 1–2.
- Ba thủ tục CRUD khu vực; năm truy vấn; hai nhóm trigger; hai thủ tục báo cáo; hai hàm xử lý dữ liệu. Có ca đúng/sai và benchmark chỉ mục chạy trên MySQL thật.
- Ứng dụng demo: mở/kết thúc phiên chơi; ví và đơn dịch vụ; phiếu kho và báo cáo. Xác thực phiên, CSRF, quyền, giao dịch, khóa và chống gửi lặp được kiểm tra tại server.
- Báo cáo LaTeX 66 trang, có lưu đồ TikZ và EER/PDF vector. Minh chứng SQL gồm câu lệnh, kết quả JSON và ảnh thực thi.

## Cấu trúc

```text
BTL_Database/
├── apps/                 # Backend Flask và giao diện trình duyệt
├── database/             # SQL đánh số theo nhóm: schema, seed, query, routine
├── docs/
│   ├── requirements/     # Đề gốc và mẫu báo cáo của lớp
│   ├── btl1_baseline/    # Mô hình, báo cáo và sơ đồ BTL1 kế thừa
│   ├── design/           # Hợp đồng schema, API, nghiệp vụ và giao dịch
│   ├── demo/             # Hướng dẫn cài mới và kịch bản trình diễn
│   └── report/latex/     # Nguồn báo cáo chính, SQL, TikZ và tài sản vector
├── tests/                # API, integration, SQL và E2E
├── evidence/             # Kết quả SQL, benchmark, JUnit và minh chứng trình duyệt
├── infrastructure/       # Docker Compose cho MySQL local
├── scripts/              # Cài đặt, kiểm tra, tạo báo cáo và đóng gói
└── deliverables/          # PDF để nộp; ZIP và checksum được tạo khi đóng gói
```

## Chạy demo

Cần Python 3.12+ và Docker đang hoạt động. Sau khi lấy dự án về máy:

```bash
git clone https://github.com/Dat-nguyen195/BTL_Database.git
cd BTL_Database
python3 -m venv apps/backend/.venv
apps/backend/.venv/bin/pip install -r apps/backend/requirements.lock
apps/backend/.venv/bin/python scripts/start_backend_demo.py
```

Mở **http://127.0.0.1:5000**. Tài khoản demo `admin`, mật khẩu `MatKhau123!`. Đây là dữ liệu giả trong seed.

Lần đầu script tạo `.env` riêng, dựng MySQL ở `127.0.0.1:13307`, cài schema và seed P1–2 vào database `quan_net_btl2`. Những lần sau giữ dữ liệu hiện có. Dùng MySQL đã có hoặc nạp seed vào bản cũ: xem [runbook](docs/demo/runbook.md). Cấu hình mẫu là `.env.example`; `.env` và môi trường Python không được đưa lên GitHub.

## Kiểm thử và minh chứng

```bash
apps/backend/.venv/bin/pip install -r apps/backend/requirements-dev.lock
set -a
. ./.env
set +a
export TD_TEST_DB_HOST="$DB_HOST" TD_TEST_DB_PORT="$DB_PORT"
export TD_TEST_DB_PASSWORD="$MYSQL_ROOT_PASSWORD"
apps/backend/.venv/bin/python -m pytest tests -q
```

Tài khoản test cần quyền tạo/xóa database và user tạm. Test dùng tài nguyên ngẫu nhiên riêng; không reset database demo. Ca trình duyệt cần Chrome/Chromium. Hướng dẫn và phạm vi kiểm tra: [tests/README.md](tests/README.md). Kết quả mới nhất nằm trong [evidence](evidence/README.md).

## Báo cáo và gói nộp

PDF chính: [BTL2 Phần 1–2](deliverables/BTL2_L09_Nhom10_P1_P2.pdf). Nguồn chỉnh sửa: [main.tex](docs/report/latex/main.tex).

```bash
# Biên dịch nguồn hiện có bằng XeLaTeX; không cần database
./scripts/build_report_latex.sh

# Tạo ZIP nguồn LaTeX, ZIP bàn giao và SHA256SUMS
apps/backend/.venv/bin/python scripts/package_deliverables.py
```

Cần TeX Live/XeLaTeX và latexmk; cấu hình VS Code/latexmk đã kèm trong dự án, phông mã nguồn đã được đóng gói. Chi tiết trong [README LaTeX](docs/report/latex/README.md). ZIP là sản phẩm sinh lại từ nguồn, được giữ local và không commit để tránh lặp toàn bộ repository. Tên tệp đầu ra được liệt kê trong [deliverables](deliverables/README.md).

Muốn cập nhật báo cáo từ SQL hiện hành: chạy `python3 scripts/build_latex_report.py` rồi biên dịch. Muốn chạy lại SQL client hoặc benchmark: xem [danh mục công cụ](scripts/README.md).

## Thành viên

| MSSV | Họ và tên |
|---|---|
| 2410709 | Nguyễn Thành Đạt |
| 2410694 | Nguyễn Minh Đạt |
| 2410696 | Nguyễn Phúc Bảo Đạt |
| 2413095 | Nguyễn Hữu Tây |
| 2413181 | Trần Tiến Thành |

Phân công chi tiết nằm trong phụ lục báo cáo và `docs/report/latex/team_assignments.json`. Tỉ lệ đóng góp là đề xuất của nhóm, không phải điểm giảng viên đã chấm.

Ứng dụng hiện minh họa ba luồng trên; chưa điều khiển máy vật lý, chưa có API hủy/hoàn hoặc CRUD quản trị đầy đủ. Tên bài và hạn nộp trên LMS cần theo thông báo của lớp.
