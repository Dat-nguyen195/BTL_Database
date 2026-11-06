# Giao diện demo

HTML/CSS/JavaScript được Flask phục vụ cùng API tại `http://127.0.0.1:5000`. Không cần Node hoặc bước build.

- `index.html`: cấu trúc và kiểu hiển thị.
- `src/main.js`: màn hình đăng nhập, máy/phiên, ví/đơn, kho và báo cáo.
- `src/services/api.js`: fetch, CSRF và xử lý phản hồi API.

Mã thao tác được giữ khi gửi lại; nút yêu cầu mới sinh ngữ cảnh mới. Quyền, tiền, giá và tồn được xác định tại server. Thông tin động được chèn bằng textContent.

Cách chạy tại `apps/backend/README.md`; kiểm chứng trình duyệt tại `tests/e2e/test_browser_flows.py` và `evidence/app/`.
