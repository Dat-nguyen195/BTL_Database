# TD-09 — Danh tính và quyền

Cập nhật sau sửa lỗi ngày 26/10/2026. Có ca login/logout/CSRF, Khoa/TamDung, thu hồi quyền sau login, tài khoản hai lớp con và truy cập chéo chủ đơn. Mỗi request đọc quyền DB, transaction ghi kiểm tra lại trên cùng kết nối; SECRET_KEY thiếu làm khởi động thất bại.

Nguồn kết quả và lệnh tái hiện: [TD_repair_verification.md](TD_repair_verification.md). JUnit giữ ca kiểm tra thực và kết quả; không dùng bằng chứng mock trước review để xác nhận tích hợp.
