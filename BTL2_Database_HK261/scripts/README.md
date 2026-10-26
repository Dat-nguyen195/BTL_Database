# Công cụ backend

- start_backend_demo.py: sinh cấu hình local nếu chưa có, dựng MySQL Docker, cài DB mới với quyền runtime tối thiểu và chạy Flask/worker. Chạy bằng Python trong apps/backend/.venv.
- bootstrap_backend.py: cài schema/routine/seed vào database mới, từ chối ghi đè database cũ; có API initialize/create_runtime_user dùng trong test. Không chứa mật khẩu thật.
- check_backend.py: kiểm tra phiên bản, 23 bảng, 8 procedure, múi giờ/isolation và danh tính runtime bằng truy vấn đọc.

Hướng dẫn lệnh đầy đủ ở apps/backend/README.md. Backup/restore và đóng gói tổng nhóm vẫn cần được thành viên phụ trách bổ sung.
