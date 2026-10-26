# TD-12 — Ngân sách và worker

Cập nhật sau sửa lỗi ngày 26/10/2026. B=g=15.000 cho t_max=3.600 giây. Hội viên dùng SoDuVi, không dùng TienGiuCho làm ngân sách. Kiểm tra fee(t_max)<=B và fee(t_max+1)>B, SQL DIV khớp Python, worker trễ chốt đúng hạn, nạp muộn quyết toán trước, nạp/chi thay đổi hạn và 0 đồng không tạo giao dịch ví. Worker đọc lại DB, không phụ thuộc mốc RAM; actor SQL NULL. Mô phỏng ứng dụng, không khóa máy vật lý.

Nguồn kết quả và lệnh tái hiện: [TD_repair_verification.md](TD_repair_verification.md). JUnit giữ ca kiểm tra thực và kết quả; không dùng bằng chứng mock trước review để xác nhận tích hợp.
