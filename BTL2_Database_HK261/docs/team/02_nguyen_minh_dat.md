# Checklist – Nguyễn Minh Đạt (2410694)

- [ ] **MD-01 – Áp dụng MySQL và hợp đồng lược đồ kế thừa BTL1**
  - Làm tại: `docs/design/schema_contract.md`, `docs/design/btl1_to_btl2.md`, `docs/design/decisions.md`.
  - Dùng MySQL Community Server 8.4.13/InnoDB, database quan_net_btl2. Giữ đúng 23 bảng và tên/kiểu/khóa cột nghiệp vụ trong baseline; chỉ thêm các thay đổi vật lý đã liệt kê trong schema_contract.md, không chờ nhóm chọn lại DBMS.

- [ ] **MD-02 – Viết DDL cho đủ 23 bảng**
  - Làm tại: `database/00_bootstrap/00_create_database.sql`, `database/01_schema/01_identity.sql`, `database/01_schema/02_workstations.sql`, `database/01_schema/03_services.sql`, `database/01_schema/04_inventory.sql`, `database/01_schema/05_staff_wallet.sql`.
  - Tạo được các bảng từ DB rỗng theo thứ tự đã ghi; đối chiếu đủ cột, kiểu tiền/ngày giờ và khóa chính.

- [ ] **MD-03 – Bổ sung FK, UNIQUE, NOT NULL, CHECK và chính sách xóa**
  - Làm tại: `database/02_constraints/01_constraints.sql`, `tests/sql/schema/`.
  - Có ca hợp lệ và ca bị từ chối; giải thích khóa tổ hợp và quy tắc phải thực thi bằng thủ tục/trigger.

- [ ] **MD-04 – Thiết kế chỉ mục phục vụ truy vấn và chống trùng phiên**
  - Làm tại: `database/03_indexes/01_indexes.sql`, `docs/design/index_catalog.md`.
  - Tạo năm UNIQUE trên cột sinh và giữ UQ MaYeuCau/MaPhien biên lai; dùng bốn chỉ mục tra cứu khởi điểm trong schema_contract.md, bỏ chỉ mục trùng PK/UQ/FK. Cùng BD đo EXPLAIN trước/sau và gắn mỗi chỉ mục với Q-ID/quy tắc.

- [ ] **MD-05 – Hoàn tất bảng đối chiếu BTL1 sang cấu trúc cài đặt**
  - Làm tại: `docs/design/btl1_to_btl2.md`, `docs/design/change_log.md`, `database/migrations/`.
  - Mỗi bảng và UC đều có vị trí hiện thực; mọi khác biệt với BTL1 được ghi và được người review kiểm tra.

- [ ] **MD-06 – Cài mới và kiểm tra khôi phục dữ liệu**
  - Làm tại: `scripts/`, `database/README.md`, `infrastructure/README.md`, `.env.example`, `evidence/database/`.
  - Một thành viên khác dùng hướng dẫn để dựng lại DB, nạp dữ liệu và đối chiếu số bản ghi; kiểm tra backup/restore.

- [ ] **MD-07 – Viết phần DDL/ràng buộc/chỉ mục của báo cáo**
  - Làm tại: `docs/report/sections/01_schema.md`, `evidence/database/`.
  - Có phiên bản DBMS thật, lệnh cài, kết quả kiểm tra khóa và giải thích lựa chọn chỉ mục.

- [ ] **MD-08 – Kiểm tra seed/truy vấn cùng BD, sửa lỗi và bàn giao CSDL**
  - Làm tại: `database/01_schema/`, `database/04_seed/`, `database/05_queries/`, `docs/design/btl1_to_btl2.md`.
  - Cùng BD dựng DB rỗng, nạp seed và chạy đủ tám truy vấn; xử lý FK lỗi, bản ghi mồ côi và thay đổi lược đồ chưa ghi nhận. Giải thích được ánh xạ từ BTL1, một ca chấp nhận và một ca bị từ chối.

- [ ] **MD-09 – Cố định charset, mã định danh, kiểu tiền và múi giờ**
  - Làm tại: `database/00_bootstrap/00_create_database.sql`, `database/01_schema/`, `docs/design/schema_contract.md`, `infrastructure/README.md`.
  - Tạo DB utf8mb4_0900_as_cs; PK/FK chuỗi và MaYeuCau dùng ascii_bin cùng kiểu hai đầu; TenDangNhap dùng utf8mb4_0900_as_ci. Giữ DECIMAL VND nguyên và DATETIME đầy đủ ngày, +07:00, SQL mode nghiêm ngặt. Kiểm tra tên bảng IN HOA và không thay VARCHAR bằng mã tự tăng.

- [ ] **MD-10 – Tạo cột sinh và UNIQUE bảo vệ phiên, ví**
  - Làm tại: `database/01_schema/02_workstations.sql`, `database/01_schema/03_services.sql`, `database/01_schema/05_staff_wallet.sql`, `database/03_indexes/01_indexes.sql`, `tests/sql/schema/`.
  - Thêm đúng năm cột sinh/UNIQUE trong schema_contract.md; chuyển ThanhTien thành generated STORED. Kiểm tra nhiều phiên đóng được phép, một active/máy/hội viên; nhiều giao dịch chưa thành công được phép nhưng chỉ một thu/phiên/đơn hoặc hoàn/gốc. Seed không ghi cột generated.

- [ ] **MD-11 – Tách tài khoản cài đặt và tài khoản chạy ứng dụng**
  - Làm tại: `database/00_bootstrap/`, `infrastructure/README.md`, `.env.example`, `tests/sql/schema/`.
  - Dùng quan_net_owner cho cài đặt và DEFINER routine, quan_net_app cho runtime. Runtime chỉ SELECT, INSERT bốn bảng nháp đầu/dòng đơn/phiếu và EXECUTE routine cần thiết; không trực tiếp UPDATE ví/tồn hay CREATE/ALTER/DROP. Kiểm tra CALL vẫn hoạt động với SQL SECURITY DEFINER, DML trái quyền bị từ chối; không đưa mật khẩu thật vào repo.

- [ ] **MD-12 – Kiểm tra bộ cài theo hợp đồng và ghi chênh lệch vật lý**
  - Làm tại: `docs/design/schema_contract.md`, `docs/design/change_log.md`, `database/migrations/`, `tests/sql/schema/`, `evidence/database/`.
  - Từ DB mới, đối chiếu information_schema đủ 23 bảng/cột gốc/PK/FK/UQ/NULL và năm cột sinh; lưu SELECT VERSION(), charset/time_zone/isolation thực tế. Kiểm tra cài lại/backup/restore, không ALTER lặp cột trên bản mới; ghi CH-01/CH-02 đã làm tới đâu, không đánh dấu đã chạy khi chưa kiểm chứng.
