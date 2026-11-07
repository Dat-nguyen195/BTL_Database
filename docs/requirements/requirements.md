# Yêu cầu BTL2 và phạm vi áp dụng

Nguồn: [THCSL_HK261_L09](https://drive.google.com/drive/u/9/folders/1v_9W2CMeLXQi4SlCZRHUT_k7J5sAouoQ), tệp **Bài tập lớn CSDL L09 (1).pdf**, trang 1–2. Nội dung đã được đọc trực tiếp bằng tài khoản trường ngày 22/10/2026. Bản PDF có sẵn trong BTL1 được kế thừa tại `de_bai_goc.pdf` (bản local, không đưa vào kho công khai) và đối chiếu với bản trong thư mục lớp.

## Nội dung trong đề bài

- Nhóm có 5 người. BTL2 chiếm 15% học phần, chia 5% tạo bảng/dữ liệu/SQL, 5% thủ tục/hàm/trigger và 5% demo ứng dụng.
- Đợt SQL (tuần 47): tạo bảng, dữ liệu mẫu và chỉ mục (3 điểm); đặc tả truy vấn gắn chức năng **đã mô tả trong BTL1** (5 điểm); demo, hỏi đáp, trình bày kết quả (2 điểm).
- Phần thủ tục/hàm: đặc tả gắn chức năng BTL1 (8 điểm); demo SQL, hỏi đáp và kết quả (2 điểm). Tên nhóm yêu cầu chung có cả trigger; kế hoạch vì vậy có chỗ hiện thực và kiểm chứng trigger.
- Đợt ứng dụng (tuần 49): kiến trúc, hạ tầng và luồng thực thi (2 điểm); demo hệ thống kết nối CSDL (6 điểm); hỏi đáp và kết quả (2 điểm).
- Hình thức: nộp LMS, in báo cáo, trình bày tại lớp và hỏi đáp. Đề ghi hạn hết thứ Hai tuần 47 và tuần 49; phải đối chiếu ngày cụ thể trên LMS.

## Phạm vi áp dụng

- **BTL2 nối tiếp BTL1 của nhóm Quản lý quán Net**, lấy 23 bảng, UC và ràng buộc làm đầu vào.
- Các mục tiêu 8 truy vấn, 6 thủ tục, 2 hàm, 3 nhóm trigger và ba luồng demo là cách nhóm chia việc; không gán thành số lượng tối thiểu giảng viên yêu cầu.
- Đề chưa chỉ định framework ứng dụng trong phần đã đọc. Nhóm đã chọn MySQL Community Server 8.4.13, Python/Flask và HTML/CSS/JavaScript theo docs/design/architecture.md; đây là quyết định của nhóm, không phải framework/phiên bản giảng viên bắt buộc.
- Cùng đề bài dùng nhãn BTL02-1 ở cả hai đợt. Chưa tự suy ra tên bài nộp; TT kiểm tra LMS khi chuẩn bị báo cáo.
- `Lab 4.pdf` cùng thư mục là tài liệu Đại số quan hệ (3 trang), không được coi là rubric số lượng SQL riêng cho BTL2.

## Ma trận bàn giao

| Nhóm yêu cầu | Chủ phần | Sản phẩm chính | Bằng chứng |
|---|---|---|---|
| Bảng, ràng buộc, chỉ mục | MD | `database/01_schema`, `02_constraints`, `03_indexes` | `evidence/dbms` |
| Dữ liệu và SQL theo chức năng BTL1 | BD | `database/04_seed`, `05_queries`, query catalog | `evidence/queries` |
| Thủ tục, hàm, trigger | HT, TD phối hợp gọi API | `database/06_procedures`, `07_functions`, `08_triggers` | `evidence/dbms` |
| Ứng dụng kết nối DB | TD + TT | `apps/backend`, `apps/frontend`, API contract | `evidence/app` |
| Kiến trúc, báo cáo, demo, hỏi đáp | Mỗi người viết phần mình; TT tổng hợp | `docs/report`, `docs/demo` | PDF, nguồn LaTeX và kết quả kiểm thử |

## Tư liệu gốc

Mẫu báo cáo của lớp: [report_template.docx](report_template.docx). Các PDF đề gốc và BTL1 được tham chiếu qua Drive như bản công khai trước đây.

- Thư mục yêu cầu của lớp: https://drive.google.com/drive/u/9/folders/1v_9W2CMeLXQi4SlCZRHUT_k7J5sAouoQ
- Tệp chính: **Bài tập lớn CSDL L09 (1).pdf**, ba trang; rubric BTL2 ở trang 1–2.
- Đã đọc toàn văn ba trang trên trình xem Drive ngày 22/10/2026. Truy cập nguồn cần tài khoản có quyền của lớp.
- Bản sao `de_bai_goc.pdf` lấy từ tệp gốc đã có trong BTL1 của người dùng; nội dung được đối chiếu với trình xem Drive.
- BTL1 dùng để kế thừa: bản chụp trong `../btl1_baseline/`.
- Thông tin chốt thêm trên LMS (hạn, tên bài nộp, số lượng bổ sung): cần đối chiếu thông báo của lớp trước khi nộp.
