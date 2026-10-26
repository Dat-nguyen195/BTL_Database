# Chạy phần backend đã hoàn thiện sau review

Từ thư mục này: `apps/backend/.venv/bin/python scripts/start_backend_demo.py`, sau khi cài thư viện theo [README backend](apps/backend/README.md). Mở http://127.0.0.1:5000; tài khoản demo `admin`, mật khẩu `MatKhau123!`. MySQL Docker và cấu hình local được chuẩn bị tự động nếu chưa có.

Phần TD có [78 ca kiểm chứng riêng biệt](evidence/app/TD_repair_verification.md), gồm MySQL và Chrome thật. SQL/UI bổ sung phục vụ tích hợp không tự xác nhận các phần việc thành viên khác hoàn tất. Checklist TD-08 giữ mở cho review chéo/bàn giao trực tiếp với HT.

---

# BTL2 – Hệ thống quản lý quán Net

L09 – Nhóm 10. **BTL2 là phần hiện thực tiếp nối trực tiếp BTL1**, sử dụng mô hình 23 bảng, các UC và ràng buộc đã thiết kế.

**Ngày bắt đầu: 23/10/2026. Hạn nội bộ: thứ Ba 03/11/2026.**

## Bắt đầu từ đây

1. Đọc [PLAN.md](PLAN.md) để xem phân công, cây thư mục có người phụ trách và danh mục sản phẩm bàn giao của từng thành viên.
2. Mỗi thành viên mở checklist riêng trong [docs/team](docs/team).
3. Đọc [yêu cầu chính thức và phạm vi kế hoạch](docs/requirements/requirements.md).
4. Đối chiếu [mốc kế thừa BTL1](docs/btl1_baseline/README.md) và [bảng chuyển tiếp sang BTL2](docs/design/btl1_to_btl2.md).

## Trạng thái hiện tại

Backend/API, SQL hỗ trợ và giao diện demo phần TD đã được hiện thực và kiểm thử. Lần review ngày 26/10/2026 chạy lại 78 test hiện có đều đạt; 3 ca bổ sung còn lỗi, xem [review lần 2](evidence/app/review_round2/README.md). TD-08 còn review/bàn giao trực tiếp với HT; trạng thái các thành viên xem checklist và TASKS.json.

## Cấu trúc

```text
BTL2_Database_HK261/
├── README.md, PLAN.md, CONTRIBUTING.md, TASKS.json
├── .env.example, .gitignore
├── docs/
│   ├── requirements/       # Đề bài, nguồn và tiêu chí đối chiếu
│   ├── btl1_baseline/      # Báo cáo, draw.io, model JSON đã chụp từ BTL1
│   ├── design/             # Chuyển tiếp BTL1, API, truy vấn, SQL nghiệp vụ
│   ├── team/               # Năm checklist cá nhân
│   ├── report/sections/    # Từng người viết phần báo cáo của mình
│   └── demo/               # Kịch bản, hướng dẫn chạy, hỏi đáp
├── database/
│   ├── 00_bootstrap/       # CSDL và cấu hình phiên
│   ├── 01_schema/          # 23 bảng, chia năm nhóm
│   ├── 02_constraints/    # FK và các ràng buộc bổ sung
│   ├── 03_indexes/         # Chỉ mục gắn Q-ID/quy tắc
│   ├── 04_seed/            # Dữ liệu mẫu
│   ├── 05_queries/         # Truy vấn nghiệp vụ/báo cáo
│   ├── 06_procedures/      # Giao dịch nghiệp vụ
│   ├── 07_functions/       # Hàm dùng trong nghiệp vụ
│   ├── 08_triggers/        # Kiểm soát ràng buộc/lịch sử
│   └── migrations/         # Thay đổi có ghi nhận sau mốc đã chốt
├── apps/backend/src/      # routes, services, repositories
├── apps/frontend/src/     # pages, components, services
├── tests/                 # sql, api, e2e: kịch bản và kết quả thực chạy
├── infrastructure/        # Môi trường và cách dựng hệ thống
├── scripts/               # Cài mới, kiểm tra, sao lưu và đóng gói
├── evidence/              # Bằng chứng SQL và ứng dụng
└── deliverables/          # PDF/ZIP cuối sau nghiệm thu
```

## Công nghệ và hợp đồng đã chốt

MySQL Community Server **8.4.13**; giữ 23 bảng và tên cột nghiệp vụ BTL1. Backend **Python 3.12 / Flask 3.1.3 / Connector-Python 26.7.0**; frontend **HTML/CSS/JavaScript** do Flask phục vụ cùng origin cổng 5000. Backend service sở hữu transaction; thủ tục SQL không tự commit.

Đọc [quyết định kỹ thuật](docs/design/decisions.md), [hợp đồng lược đồ](docs/design/schema_contract.md), [API](docs/design/api_contract.md), [mã lỗi](docs/design/error_codes.md) và [giao dịch](docs/design/transactions.md) để triển khai trực tiếp. Mỗi thành viên có **12 tác vụ**, 60 tác vụ toàn nhóm. SQL/ứng dụng chưa được hiện thực; các lệnh chạy thực tế sẽ do người phụ trách bổ sung sau khi triển khai và kiểm tra.

Nguồn yêu cầu: [thư mục lớp trên Drive](https://drive.google.com/drive/u/9/folders/1v_9W2CMeLXQi4SlCZRHUT_k7J5sAouoQ). Không ghi hay tải tệp của nhóm vào thư mục đề bài của giảng viên.
