# Phạm vi giao diện đã chốt – TT

HTML/CSS/JavaScript ES modules, không framework/build; Flask phục vụ cùng origin cổng 5000. index.html là điểm vào; src/pages là màn hình, components là phần dùng lại, services là fetch/API/session. Không tính giá/số dư để quyết định thu ở client.

| Màn hình | API chính | Quyền / việc cần làm |
|---|---|---|
| Đăng nhập | /auth/csrf, /auth/login, /auth/me, /auth/logout | Lưu CSRF mới sau login; không lưu mật khẩu/giả vai trò trong localStorage. |
| Máy và phiên | /workstations, /sessions, /sessions/:id/close | Người chơi thấy/thao tác phiên mình; ThuNgan/QuanLy xử lý khách; quyền miễn phí chỉ QuanLy. Hiển thị phí/CanUseUntil từ server. |
| Ví hội viên | /wallets/:id, /wallets/:id/transactions, /wallet/topups | Người chơi xem ví mình; ThuNgan/QuanLy nạp. Hiển thị số dư, giữ chỗ, khả dụng tách biệt. |
| Đơn dịch vụ | /services, /orders, /orders/:id/accept, /orders/:id/pay | Tạo nháp chụp giá server; PhaChe/ThuNgan/QuanLy tiếp nhận; thanh toán theo quyền trong API contract. |
| Phiếu kho | /inventory-documents, /inventory-documents/:id/post | ThuNgan/QuanLy tạo; QuanLy ghi sổ. Kiểm kê lỗi ảnh chụp phải yêu cầu đếm lại, không tự sửa số. |
| Báo cáo | Bốn /reports/... | Q05/Q07/Q08 QuanLy; Q06 ThuNgan/QuanLy; bộ lọc/phân trang. |

Mỗi trang có trạng thái tải/rỗng/lỗi và kết quả sau ghi; hiển thị error.code thành thông báo rõ, giữ input khi lỗi. Với 401 trở về login; 403 báo thiếu quyền; 409 giải thích lý do và cho tải lại; 503 cho thử lại cùng mã/khóa, không tạo một giao dịch nạp mới. Nút bận ngăn bấm lặp nhưng không thay cơ chế chống lặp server.

Các nút hủy/hoàn, đổi trạng thái chế biến/giao, sửa/xóa nháp và CRUD tài khoản/danh mục/ca nằm ngoài UI ghi của demo. Không hiển thị nút chưa có API/SQL bảo vệ. Danh mục/tài khoản/ca dùng seed; tài khoản có cả lớp con vẫn hiển thị quyền phù hợp. TT đối chiếu từng trang với API contract và minh chứng ba luồng trong docs/demo/scenarios.md.
