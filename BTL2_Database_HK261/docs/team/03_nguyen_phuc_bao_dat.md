# Checklist – Nguyễn Phúc Bảo Đạt

- [ ] **BD-01 – Thiết kế bộ dữ liệu và danh mục tám truy vấn**
  - Làm tại: `docs/design/seed_scenarios.md`, `docs/design/query_catalog.md`.
  - Có ca bình thường, biên và lỗi cho các UC BTL1; nêu kết quả mong đợi, không lấy dữ liệu cá nhân thật.

- [ ] **BD-02 – Viết dữ liệu mẫu nhất quán và có thể nạp lại**
  - Làm tại: `database/04_seed/01_reference_data.sql`, `database/04_seed/02_demo_scenarios.sql`.
  - Đủ 23 bảng theo yêu cầu nghiệp vụ; thứ tự nạp đúng FK; có danh mục, hội viên, vãng lai, phiên, đơn, kho và ca.

- [ ] **BD-03 – Hiện thực Q01–Q04 cho máy, phiên, ví và đơn**
  - Làm tại: `database/05_queries/01_operations.sql`.
  - Mỗi truy vấn nêu UC, tham số, dữ liệu đầu vào, SQL và kết quả chuẩn để so sánh.

- [ ] **BD-04 – Hiện thực Q05–Q08 cho doanh thu, tồn và ca**
  - Làm tại: `database/05_queries/02_reports.sql`.
  - Tổng hợp đúng; nạp ví không bị cộng thành doanh thu; có truy vấn đối soát kho và ca chồng giờ.

- [ ] **BD-05 – Lưu kết quả chuẩn và các trường hợp không có dữ liệu**
  - Làm tại: `tests/sql/queries/`, `evidence/queries/`.
  - Kết quả được đối chiếu với tính tay/dữ liệu chuẩn; có NULL, khoảng ngày, nhóm rỗng và ca qua đêm.

- [ ] **BD-06 – Đối chiếu hiệu năng với MD và hoàn thiện dữ liệu demo**
  - Làm tại: `docs/design/index_catalog.md`, `evidence/queries/`.
  - Lưu kế hoạch thực thi trên DBMS thật trước/sau chỉ mục; dữ liệu đủ để thấy khác biệt, ghi rõ giới hạn phép đo.

- [ ] **BD-07 – Viết phần dữ liệu và đặc tả truy vấn**
  - Làm tại: `docs/report/sections/02_data_queries.md`.
  - Mỗi Q-ID liên kết được UC BTL1, SQL, kết quả và ảnh/log chạy thật.

- [ ] **BD-08 – Kiểm tra DDL cùng MD và bàn giao dữ liệu, truy vấn**
  - Làm tại: `database/04_seed/`, `database/05_queries/`, `tests/sql/queries/`.
  - Tự nạp lại seed và chạy tám truy vấn từ DB mới; so sánh với kết quả chuẩn, báo MD các khác biệt cấu trúc. Giải thích được phép nối, cách kiểm tra tổng và liên hệ với UC BTL1.

- [ ] **BD-09 – Bổ sung seed tài khoản và quyền dùng cho demo**
  - Làm tại: `database/04_seed/01_reference_data.sql`, `docs/design/seed_scenarios.md`, `tests/api/`.
  - Tạo dữ liệu giả cho người chơi, ThuNgan, PhaChe, KyThuat, QuanLy và tài khoản có cả hai lớp con; thêm Khoa/TamDung cho ca từ chối. MatKhauBam tạo bằng Werkzeug tương thích backend, không lưu mật khẩu thật; ghi tài khoản demo và cách tạo mật khẩu thử trong hướng dẫn. Nhóm VangLai là nhóm giá, không phải quyền.

- [ ] **BD-10 – Chuẩn bị dữ liệu chuẩn cho mã lỗi và chống lặp**
  - Làm tại: `docs/design/seed_scenarios.md`, `tests/sql/queries/`, `tests/sql/business_rules/`, `evidence/queries/`.
  - Tách bộ seed hợp lệ và dữ liệu thử lỗi; lập đầu vào/kết quả số dư-tồn trước/sau cho thiếu tiền, thiếu món, sai chủ, máy bận, replay và cùng khóa khác nội dung. Gắn expected error.code theo error_codes.md; dữ liệu lỗi không làm bộ cài chính bị lỗi.

- [ ] **BD-11 – Gắn tám truy vấn với bộ lọc API và kết quả JSON**
  - Làm tại: `docs/design/query_catalog.md`, `database/05_queries/`, `tests/sql/queries/`.
  - Cho mỗi Q-ID ghi endpoint trong api_contract.md, tham số có kiểu, quyền/phạm vi dữ liệu và trường kết quả. Khoảng ngày gồm đủ ngày cuối theo giờ Việt Nam; sắp xếp/phân trang ổn định; Q03 tính khả dụng tại giờ server, Q05 không cộng nạp ví hoặc thu công nợ chưa có, Q07 không trừ kho hai lần.

- [ ] **BD-12 – Chạy lại seed và truy vấn sau thay đổi cột sinh**
  - Làm tại: `database/04_seed/`, `database/05_queries/`, `tests/sql/queries/`, `evidence/queries/`.
  - Mọi INSERT dùng danh sách cột và bỏ generated; nạp lại trên DDL cuối, kiểm đếm 23 bảng. So sánh đủ tám truy vấn với kết quả chuẩn và dữ liệu kiểm thử mới; ghi số bản ghi/kết quả thực tế cùng phiên bản MySQL, cung cấp fixture ổn định cho TT demo.
