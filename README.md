# BTL Database – L09, Nhóm 10

Dự án **Hệ thống quản lý quán Net**. BTL2 hiện thực tiếp nối BTL1, kế thừa mô hình 23 bảng, các use case và quy tắc nghiệp vụ đã thiết kế.

**Bắt đầu: 23/10/2026 · Hạn nội bộ: thứ Ba 03/11/2026.** Lịch nộp chính thức đối chiếu LMS theo tài liệu môn học.

## Thành viên bắt đầu từ đây

1. Đọc [kế hoạch, cây thư mục và sản phẩm bàn giao](BTL2_Database_HK261/PLAN.md).
2. Mở checklist của mình trong bảng dưới; mỗi người có **12 tác vụ**, kèm hướng dẫn và vị trí tệp cần xử lý.
3. Triển khai theo [quyết định kỹ thuật đã chốt](BTL2_Database_HK261/docs/design/decisions.md).
4. Làm theo [hướng dẫn đóng góp](CONTRIBUTING.md) khi gửi thay đổi lên GitHub.

| Thành viên | Phụ trách | Checklist |
|---|---|---|
| Nguyễn Thành Đạt | Backend/API và tích hợp | [TD – 12 tác vụ](BTL2_Database_HK261/docs/team/01_nguyen_thanh_dat.md) |
| Nguyễn Minh Đạt | Lược đồ, ràng buộc và chỉ mục | [MD – 12 tác vụ](BTL2_Database_HK261/docs/team/02_nguyen_minh_dat.md) |
| Nguyễn Phúc Bảo Đạt | Dữ liệu mẫu và truy vấn | [BD – 12 tác vụ](BTL2_Database_HK261/docs/team/03_nguyen_phuc_bao_dat.md) |
| Nguyễn Hữu Tây | Thủ tục, hàm, trigger và giao dịch | [HT – 12 tác vụ](BTL2_Database_HK261/docs/team/04_nguyen_huu_tay.md) |
| Trần Tiến Thành | Frontend, báo cáo tổng hợp và demo | [TT – 12 tác vụ](BTL2_Database_HK261/docs/team/05_tran_tien_thanh.md) |

## Trạng thái hiện tại

Đã có kế hoạch, 60 tác vụ, checklist, cấu trúc thư mục và hợp đồng kỹ thuật. **SQL, backend và frontend hiện là khung công việc, chưa phải ứng dụng đã chạy.** Các tác vụ hiện thực đang TODO; chỉ đánh dấu hoàn thành sau khi làm và kiểm tra kết quả. Xem [trạng thái chi tiết](BTL2_Database_HK261/SCAFFOLD_STATUS.md).

## Công nghệ đã chốt

- MySQL Community Server **8.4.13**, InnoDB; giữ 23 bảng và tên cột nghiệp vụ BTL1.
- Backend: **Python 3.12, Flask 3.1.3, mysql-connector-python 26.7.0**; SQL có tham số/CALL.
- Frontend: **HTML/CSS/JavaScript modules**, Flask phục vụ UI và API cùng origin cổng 5000.
- Backend service sở hữu transaction; routine không tự COMMIT/ROLLBACK. Các quyết định này đã chốt để thành viên triển khai trực tiếp.

| Tài liệu | Mục đích |
|---|---|
| [Lược đồ vật lý](BTL2_Database_HK261/docs/design/schema_contract.md) | Tên/kiểu/khóa, cột sinh và chênh lệch so với BTL1 |
| [Hợp đồng API](BTL2_Database_HK261/docs/design/api_contract.md) | Endpoint, đầu vào/ra và quyền |
| [Thủ tục, hàm, trigger](BTL2_Database_HK261/docs/design/routines_catalog.md) | Chữ ký và hậu điều kiện SQL |
| [Mã lỗi](BTL2_Database_HK261/docs/design/error_codes.md) | Mã HTTP và SIGNAL thống nhất |
| [Giao dịch và chống lặp](BTL2_Database_HK261/docs/design/transactions.md) | Khóa, commit/rollback và retry |
| [Yêu cầu bài tập](BTL2_Database_HK261/docs/requirements/requirements.md) | Nguồn đề, rubric và phạm vi |
| [Bản thiết kế BTL1](BTL2_Database_HK261/docs/btl1_baseline/README.md) | Mô hình, quy tắc nghiệp vụ và nguồn draw.io dùng đối chiếu |

## Cấu trúc chính

```text
BTL2_Database_HK261/
├── PLAN.md, TASKS.json, CONTRIBUTING.md
├── docs/            # Yêu cầu, baseline BTL1, hợp đồng, checklist, báo cáo, demo
├── database/        # SQL: lược đồ, dữ liệu, truy vấn, thủ tục, hàm, trigger
├── apps/            # Backend và frontend
├── tests/           # Kiểm tra SQL, API và đầu cuối
├── infrastructure/ # Hướng dẫn môi trường
├── scripts/        # Cài mới, sao lưu và đóng gói
├── evidence/       # Minh chứng khi có kết quả thực chạy
└── deliverables/   # Báo cáo/gói bàn giao khi hoàn thiện
```

Cây thư mục có người phụ trách và danh mục bàn giao từng người nằm trong [PLAN.md](BTL2_Database_HK261/PLAN.md). Kho chứa đầu vào và tệp cần cho BTL2; sơ đồ dùng nguồn draw.io.

## Lấy dự án về máy

```bash
git clone https://github.com/Dat-nguyen195/BTL_Database.git
cd BTL_Database/BTL2_Database_HK261
```

Hiện chưa có lệnh chạy ứng dụng hoàn chỉnh. TD/MD/TT bổ sung lệnh đã kiểm tra vào README phần mình và [runbook](BTL2_Database_HK261/docs/demo/runbook.md) khi hiện thực. Cấu hình mẫu ở [.env.example](BTL2_Database_HK261/.env.example); mật khẩu và SECRET_KEY tạo trên từng máy, không đưa vào Git.

Kho công khai giữ các tệp phục vụ triển khai; PDF báo cáo và PDF đề gốc được thay bằng nội dung quy tắc cần thiết và liên kết nguồn. Không có bộ ảnh xuất trùng hoặc bản ZIP cũ.
