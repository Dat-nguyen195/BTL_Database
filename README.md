# BTL2 — Hệ thống quản lý quán Net

Hệ Cơ sở dữ liệu (CO2013), HK261 · L09 · Nhóm 09
**GVHD: ThS. Trần Thị Quế Nguyệt**

MySQL 8.4.13 / InnoDB · Python 3.12 / Flask 3.1.3 · HTML/CSS/JavaScript.

[Báo cáo PDF](docs/report/latex/BTL2_L09_Nhom09_P1_P2.pdf) · [Nguồn LaTeX](docs/report/latex/main.tex) · [Hướng dẫn demo](docs/demo/runbook.md) · [Yêu cầu bài tập](docs/requirements/requirements.md)

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
│   └── report/latex/     # Nguồn báo cáo chính, PDF nộp, SQL, TikZ và tài sản vector
├── tests/                # API, integration, SQL và E2E
├── evidence/             # Kết quả SQL, benchmark, JUnit và minh chứng trình duyệt
├── infrastructure/       # Docker Compose cho MySQL local
└── scripts/              # Cài đặt, kiểm tra, tạo báo cáo và đóng gói
```

## Chạy demo

Cần Python 3.12+ và Docker đang hoạt động. Sau khi lấy dự án về máy:

### Linus/MacOs 

```bash
git clone https://github.com/Dat-nguyen195/BTL_Database.git
cd BTL_Database
python3 -m venv apps/backend/.venv                
apps/backend/.venv/bin/pip install -r apps/backend/requirements.lock        
apps/backend/.venv/bin/python scripts/start_backend_demo.py
```

### Windows PowerShell 
Mở PowerShell tại thư mục muốn lưu dự án:
```bash
git clone https://github.com/Dat-nguyen195/BTL_Database.git
cd BTL_Database

python -m venv apps/backend/.venv
.\apps\backend\.venv\Scripts\python.exe -m pip install -r apps/backend\requirements.lock
.\apps\backend\.venv\Scripts\python.exe scripts\start_backend_demo.py
```

Mở **http://127.0.0.1:5000**. Tài khoản demo `admin`, mật khẩu `MatKhau123!`. Đây là dữ liệu giả trong seed.

Lần đầu script tạo `.env` riêng, dựng MySQL ở `127.0.0.1:13307`, cài schema và seed P1–2 vào database `quan_net_btl2`. Những lần sau giữ dữ liệu hiện có. Dùng MySQL đã có hoặc nạp seed vào bản cũ: xem [runbook](docs/demo/runbook.md). Cấu hình mẫu là `.env.example`; `.env` và môi trường Python không được đưa lên GitHub.

## Thao tác Database

- MySQL 8.4.13 / InnoDB chạy trong Docker.
- Không yêu cầu bắt buộc phải cài MySQL Server. 

### 1. Kết nối MySQL

Sau khi Docker container `quan-net-btl2-mysql` đã được khởi chạy, mở terminal tại thư mục gốc dự án:

```bash
docker exec -it quan-net-btl2-mysql mysql -u root -p
```

Nhập mật khẩu MySQL root được cấu hình trong `.env`.

### 2. Kiểm tra database và dữ liệu

```sql
-- Chọn database demo
USE quan_net_btl2;

-- Liệt kê các bảng
SHOW TABLES;

-- Xem cấu trúc bảng
DESCRIBE <TenBang> ;

-- Truy vấn dữ liệu
SELECT * FROM <TenBang>;
```

Thay `TenBang` bằng tên bảng thực tế trong database.

### 3. Thực hành SQL

Có thể thực hiện các thao tác SELECT, INSERT, UPDATE, DELETE, JOIN, GROUP BY và transaction trực tiếp trong MySQL client.

Các thủ tục CRUD khu vực, truy vấn báo cáo, trigger và function được tổng duyệt theo các file SQL trong `database/` và `evidence/dbms/`.

**Lưu ý:** Không thực hiện UPDATE hoặc DELETE thiếu điều kiện WHERE. Không reset hoặc nạp lại seed trên database demo đang có dữ liệu nếu chưa kiểm tra tác động.

Hướng dẫn cài đặt, tổng duyệt SQL và demo giao diện chi tiết: [docs/demo/runbook.md](docs/demo/runbook.md).

Hướng dẫn chạy kiểm thử tự động: [tests/README.md](tests/README.md).
## Kiểm thử và minh chứng
Cần cài dependency kiểm thử từ apps/backend/requirements-dev.lock.

### Linux / macOS
```bash
apps/backend/.venv/bin/pip install -r apps/backend/requirements-dev.lock
set -a
. ./.env
set +a
export TD_TEST_DB_HOST="$DB_HOST" TD_TEST_DB_PORT="$DB_PORT"
export TD_TEST_DB_PASSWORD="$MYSQL_ROOT_PASSWORD"
apps/backend/.venv/bin/python -m pytest tests -q
```
### Windows PowerShell
Mở terminal, gõ lệnh: 

```bash
.\apps\backend\.venv\Scripts\python.exe -m pip install -r apps/backend\requirements-dev.lock

# Nạp cấu hình từ .env
Get-Content .env | ForEach-Object{
    if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim().Trim('"').Trim("'")
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

$env:TD_TEST_DB_HOST = $env:DB_HOST
$env:TD_TEST_DB_PORT = $env:DB_PORT
$env:TD_TEST_DB_PASSWORD = $env:MYSQL_ROOT_PASSWORD
$env:TD_BROWSER_EVIDENCE_DIR = "evidence/app"

New-Item -ItemType Directory -Force evidence/final_verification | Out-Null

.\apps\backend\.venv\Scripts\python.exe -m pytest tests -q --junitxml=evidence/final_verification/all.xml

```
Tài khoản test cần quyền tạo/xóa database và user tạm. Test dùng tài nguyên ngẫu nhiên riêng; không reset database demo. Ca trình duyệt cần Chrome/Chromium. Hướng dẫn và phạm vi kiểm tra: [tests/README.md](tests/README.md). Kết quả mới nhất nằm trong [evidence](evidence/README.md).

## Báo cáo và gói nộp

PDF chính: [BTL2 Phần 1–2](docs/report/latex/BTL2_L09_Nhom09_P1_P2.pdf). Nguồn chỉnh sửa: [main.tex](docs/report/latex/main.tex).

```bash
# Biên dịch nguồn hiện có bằng XeLaTeX; không cần database
./scripts/build_report_latex.sh

# Tạo ZIP nguồn LaTeX, ZIP bàn giao và SHA256SUMS trong docs/report/latex/
apps/backend/.venv/bin/python scripts/package_deliverables.py
```

Cần TeX Live/XeLaTeX và latexmk; cấu hình VS Code/latexmk đã kèm trong dự án, phông mã nguồn đã được đóng gói. Chi tiết trong [README LaTeX](docs/report/latex/README.md). ZIP là sản phẩm sinh lại từ nguồn, được giữ local và không commit để tránh lặp toàn bộ repository. Tệp đầu ra được lưu trực tiếp trong `docs/report/latex/`.

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
