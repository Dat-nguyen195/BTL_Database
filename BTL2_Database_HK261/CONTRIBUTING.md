# Cách phối hợp

- Giữ tên bảng/cột theo baseline; MD quản lý mọi thay đổi lược đồ và migration.
- Mã tác vụ dùng TD/MD/BD/HT/TT; ghi mã trong phần mô tả thay đổi. Nếu nhóm dùng Git, có thể dùng nhánh `feature/TD-03-mo-ta` và chỉ hợp nhất sau review.
- Mỗi người làm phần mình, tự viết phần báo cáo và lưu bằng chứng. Người review kiểm tra cách chạy và kết quả, không chỉ xem ảnh.
- Chỉ tick checklist khi thỏa acceptance, có bằng chứng và review; đồng thời cập nhật trạng thái TASKS.json.
- Không đưa mật khẩu thật hoặc dữ liệu cá nhân thật vào mã nguồn/seed/báo cáo; cấu hình qua .env của máy chạy.
- Chưa có ứng dụng/bộ test chạy hoàn chỉnh tại thời điểm tạo scaffold. Không coi các khung SQL/README là sản phẩm đã hoàn thành.

- Các lựa chọn kỹ thuật đã chốt trong docs/design/decisions.md; triển khai trực tiếp theo schema/API/routine/error/transaction contract. Kiểm tra chéo không phải yêu cầu họp lại để chọn công nghệ.
- Backend service sở hữu transaction; không commit trong repository/routine. Giữ mã đối tượng/khóa nghiệp vụ khi retry, chỉ dùng Q-ID/tham số đã whitelist.
