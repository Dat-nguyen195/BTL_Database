# Checklist – Nguyễn Hữu Tây (2413095)

- [ ] **HT-01 – Ánh xạ quy tắc BTL1 vào hợp đồng SQL đã chốt**
  - Làm tại: `docs/design/routines_catalog.md`, `docs/design/rules_matrix.md`, `docs/design/error_codes.md`, `docs/design/transactions.md`.
  - Theo đúng sáu chữ ký thủ tục, hai hàm, ba nhóm trigger và mã SIGNAL đã ghi. Điền BR/D-ID, nơi thực thi và ca kiểm tra trong rules_matrix.md; backend giữ transaction, routine không tự commit và không chờ họp chọn lại hợp đồng.

- [ ] **HT-02 – Hiện thực hai hàm tiền giờ và số dư khả dụng**
  - Làm tại: `database/07_functions/01_billing.sql`.
  - Hiện thực fn_tien_gio(pBatDau,pKetThuc,pDonGiaGio) và fn_so_du_kha_dung(pMaNguoiChoi) đúng kiểu/giới hạn trong catalog. Kiểm tra 59 giây, qua ngày, giá 0, tràn số, giữ chỗ; fn_so_du_kha_dung chỉ đọc, caller làm mới giữ chỗ dưới khóa trước khi quyết định chi.

- [ ] **HT-03 – Hiện thực mở phiên và kết thúc/quyết toán**
  - Làm tại: `database/06_procedures/01_sessions.sql`.
  - Tối đa một phiên hoạt động/máy/hội viên; đóng phiên lập biên lai và thu một lần trong cùng giao dịch.

- [ ] **HT-04 – Hiện thực nạp ví, nhận đơn, thu đơn và ghi sổ kho**
  - Làm tại: `database/06_procedures/02_wallet_orders.sql`, `database/06_procedures/03_inventory.sql`.
  - Đúng chủ ví, đủ tiền/tồn, chụp giá; nhận đơn trừ kho một lần; thanh toán không trừ kho lần nữa.

- [ ] **HT-05 – Hiện thực nhóm trigger và kiểm tra bảo toàn lịch sử**
  - Làm tại: `database/08_triggers/01_history.sql`, `database/08_triggers/02_state_identity.sql`, `tests/sql/business_rules/`.
  - Chặn sửa/xóa chứng từ đã chốt và các thay đổi không hợp lệ theo phạm vi đã chốt; có ca từ chối thực chạy.

- [ ] **HT-06 – Kiểm tra rollback, gửi lặp và hai yêu cầu tranh chấp**
  - Làm tại: `tests/sql/business_rules/`, `evidence/routines/`.
  - Dùng hai kết nối cho ca tranh máy/tồn/ví; giữ thứ tự khóa; không dùng mô phỏng tuần tự để tuyên bố đã thử đồng thời.

- [ ] **HT-07 – Viết phần thủ tục/hàm/trigger và ma trận quy tắc**
  - Làm tại: `docs/report/sections/04_routines.md`, `docs/design/rules_matrix.md`.
  - Chỉ rõ BR/D-ID nào được thực thi ở đâu, bằng chứng và phần nào chưa hỗ trợ; giải thích được từng đối tượng SQL.

- [ ] **HT-08 – Kiểm tra luồng ghi backend cùng TD và bàn giao SQL nghiệp vụ**
  - Làm tại: `apps/backend/src/services/`, `database/06_procedures/`, `docs/design/rules_matrix.md`.
  - Cùng TD kiểm tra không có đường API bỏ qua ràng buộc/giao dịch; sửa lỗi SQL chặn demo. Giải thích tham số, khóa, rollback và một ca thành công/từ chối; ghi rõ các quy tắc BTL1 còn chưa hỗ trợ.

- [ ] **HT-09 – Triển khai chữ ký routine và SIGNAL theo hợp đồng**
  - Làm tại: `database/06_procedures/`, `database/07_functions/`, `database/08_triggers/`, `docs/design/error_codes.md`, `tests/sql/business_rules/`.
  - Giữ đúng tên/thứ tự/kiểu tham số trong catalog; mỗi routine trả một dòng MaDoiTuong/DaThucHienTruoc. SIGNAL SQLSTATE 45000 với MYSQL_ERRNO 60001–60015; caller nhận biết lỗi theo mã, không phân tích câu tiếng Việt. Tác nhân/giờ do backend cung cấp, kiểm tra quyền nghiệp vụ trong SQL.

- [ ] **HT-10 – Loại bỏ commit nội bộ và thống nhất khóa**
  - Làm tại: `database/06_procedures/`, `database/08_triggers/`, `tests/sql/business_rules/`, `docs/design/transactions.md`.
  - Routine chỉ làm nghiệp vụ trong transaction của caller; không START TRANSACTION/COMMIT/ROLLBACK, không nuốt lỗi. Tuân thứ tự ví → máy → phiên → đơn/phiếu → món tăng dần → ví nhật ký. Routine cập nhật tiền/tồn, trigger chỉ kiểm tra/từ chối; gây lỗi cuối thao tác để chứng minh caller rollback toàn bộ.

- [ ] **HT-11 – Bảo vệ chống thu/trừ lặp bằng khóa và trạng thái**
  - Làm tại: `database/06_procedures/`, `tests/sql/business_rules/`, `evidence/routines/`.
  - Dùng nap:{UUID}, gio:{MaPhien}, dv:{MaDonHang} và UNIQUE đã chốt; so sánh payload khi replay, cùng khóa khác nội dung phải SIGNAL 60009. Lần đóng/nhận/thu/ghi sổ đã làm không lặp tác dụng; phí 0 không tạo GD ví; tiền nhận vãng lai không thu lại. Kiểm tra race bằng hai kết nối, kể cả khóa khác nhưng cùng phiên/đơn.

- [ ] **HT-12 – Hoàn thiện giữ chỗ và quyết toán tại hạn ngân sách**
  - Làm tại: `database/06_procedures/01_sessions.sql`, `database/06_procedures/02_wallet_orders.sql`, `database/07_functions/01_billing.sql`, `tests/sql/business_rules/`, `docs/design/rules_matrix.md`.
  - Cùng service TD, tính lại phí/giữ chỗ dưới khóa trước chi ví; tách TraTruoc/TraSau/MienPhi, không vừa trừ theo nhịp vừa thu lúc đóng. Thử giá 0, 59 giây, qua ngày, đúng hạn/ngân sách và worker đóng muộn; giữ phí tại hạn dùng hợp lệ, biên lai/thu một lần. Ghi BR-04/05 chưa đạt nếu chưa có minh chứng.
