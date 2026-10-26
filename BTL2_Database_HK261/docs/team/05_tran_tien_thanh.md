# Checklist – Trần Tiến Thành (2413181)

- [ ] **TT-01 – Ánh xạ màn hình theo phạm vi và API đã chốt**
  - Làm tại: `docs/design/ui_scope.md`, `docs/demo/scenarios.md`.
  - Dùng HTML/CSS/JavaScript modules không build; lập màn hình theo ui_scope.md và API contract, đủ quyền người chơi/nhân viên/QuanLy và ba luồng demo. Không thêm nút hủy/hoàn/CRUD ngoài phạm vi hoặc chờ chọn framework.

- [ ] **TT-02 – Dựng frontend HTML/CSS/JavaScript cùng origin Flask**
  - Làm tại: `apps/frontend/`.
  - Tạo index.html, CSS và module trong pages/components/services; fetch địa chỉ tương đối /api/v1, Flask phục vụ cùng origin cổng 5000. Không cần Node/package.json/build; README chỉ cách dùng qua Flask và các trạng thái tải/rỗng/lỗi.

- [ ] **TT-03 – Làm màn hình đọc máy, phiên, đơn và báo cáo**
  - Làm tại: `apps/frontend/src/pages/`, `apps/frontend/src/services/`.
  - Hiển thị dữ liệu DB qua API, có rỗng/lỗi/đang tải; tham số lọc nhất quán với Q-ID.

- [ ] **TT-04 – Làm form mở/đóng phiên, nạp ví, đơn và phiếu kho**
  - Làm tại: `apps/frontend/src/components/`.
  - Chặn bấm lặp ở UI, hiển thị lỗi nghiệp vụ từ server; không tự tính số dư/giá để quyết định thanh toán.

- [ ] **TT-05 – Chạy ba luồng demo đầu cuối với TD**
  - Làm tại: `tests/e2e/`, `evidence/app/`.
  - Ảnh/log thể hiện thay đổi trong DB thật; có tình huống thành công và một tình huống bị từ chối.

- [ ] **TT-06 – Viết phần frontend và tổng hợp báo cáo từ cả năm người**
  - Làm tại: `docs/report/outline.md`, `docs/report/sections/05_frontend_integration.md`.
  - Tự viết 05_frontend_integration.md về màn hình, luồng UI → API → DB và bằng chứng tích hợp. Hợp nhất năm phần theo outline, đối chiếu rubric và đánh dấu nội dung còn thiếu bằng chứng; không viết thay phần kỹ thuật của người khác.

- [ ] **TT-07 – Chốt PDF, hướng dẫn chạy và diễn tập hỏi đáp**
  - Làm tại: `docs/report/`, `docs/demo/scenarios.md`, `docs/demo/runbook.md`, `docs/demo/questions.md`, `deliverables/`.
  - Xuất báo cáo PDF có mục lục, hình/bảng và liên kết nguồn đúng; sơ đồ có nguồn draw.io và ảnh xuất. Ghi đủ phiên bản, cấu hình mẫu, thứ tự SQL, lệnh chạy và ba kịch bản để máy khác làm lại. Cùng cả nhóm diễn tập giải thích phần mình và ca lỗi.

- [ ] **TT-08 – Đóng gói và kiểm tra bản bàn giao**
  - Làm tại: `deliverables/`, `scripts/`, `README.md`, `docs/demo/runbook.md`.
  - Tạo ZIP gồm SQL, mã nguồn, tệp khai báo/khóa phiên bản thư viện, cấu hình mẫu, báo cáo, nguồn sơ đồ và hướng dẫn. Bỏ thư viện đã cài, tệp tạm, mật khẩu thật; không lồng các ZIP cũ. Giải nén ra vị trí mới và kiểm tra cài/chạy theo hướng dẫn trước bàn giao.

- [ ] **TT-09 – Làm màn hình đăng nhập và hiển thị đúng quyền**
  - Làm tại: `apps/frontend/src/pages/`, `apps/frontend/src/services/`, `apps/frontend/src/components/`, `tests/e2e/`.
  - Gọi /auth/csrf trước login, dùng token mới sau login và /auth/me để dựng menu. Kiểm tra người chơi/ThuNgan/PhaChe/KyThuat/QuanLy/tài khoản hai lớp con; 401 về login, 403 báo thiếu quyền. Ẩn nút không đủ quyền nhưng vẫn dựa kiểm tra quyền backend.

- [ ] **TT-10 – Tạo lớp fetch dùng chung theo API v1**
  - Làm tại: `apps/frontend/src/services/`, `apps/frontend/src/components/`, `tests/e2e/`.
  - Dùng URL tương đối /api/v1, cookie cùng origin và X-CSRF-Token cho ghi. Đọc envelope ok/data/meta/error/requestId, render thông báo theo error.code; hỗ trợ loading/rỗng/lỗi/phân trang. Không thay response DB lỗi bằng dữ liệu giả hoặc tự diễn giải chuỗi lỗi SQL.

- [ ] **TT-11 – Giữ mã thao tác và dữ liệu form khi gửi lại**
  - Làm tại: `apps/frontend/src/pages/`, `apps/frontend/src/components/`, `apps/frontend/src/services/`, `tests/e2e/`.
  - Dùng crypto tạo mã P/O/K/G + 19 hex và nap:{UUID} một lần mỗi thao tác; giữ cùng mã/nội dung khi mất response hoặc 503, không tự nạp lại với UUID mới. Cùng mã khác nội dung xử lý 409, thao tác mới dùng mã mới; hiển thị replayed và ngăn bấm lặp. Form không gửi giá/tổng/số dư/nhân viên/giờ do server quản lý.

- [ ] **TT-12 – Bổ sung tổng duyệt theo hợp đồng và giới hạn demo**
  - Làm tại: `docs/demo/scenarios.md`, `docs/demo/runbook.md`, `docs/demo/questions.md`, `tests/e2e/`, `evidence/app/`.
  - Thử ba luồng với từng vai, ca 401/403/409/503, replay, phiếu kiểm kê lỗi và phiên hết hạn server. Giải thích mô phỏng máy trạm, danh mục/ca dùng seed, chưa có UI hủy/hoàn/thu công nợ; không để nút ngoài phạm vi. Cùng TD ghi phiên bản thực cài/lệnh chạy và ảnh trước-sau cho máy khác làm lại.
