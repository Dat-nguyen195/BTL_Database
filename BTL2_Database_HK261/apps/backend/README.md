# Backend – TD

Đã chốt Python 3.12, Flask 3.1.3, mysql-connector-python 26.7.0, SQL tham số/CALL trực tiếp; không ORM. Flask phục vụ frontend và /api/v1 cùng cổng 5000. Cấu hình theo .env.example, dùng quan_net_app, không dùng tài khoản cài đặt.

TD cần tạo entrypoint cùng requirements.in/requirements.lock và hướng dẫn lệnh cài/chạy sau khi thực hiện; ghi phiên bản vá Python thực dùng. routes xử lý HTTP/auth/CSRF, services sở hữu transaction và hạn dùng, repositories truy cập SQL không commit. Backend đọc cấu hình từ biến môi trường; việc đọc .env nếu thêm phải được mô tả và khóa thư viện đi kèm.

Hợp đồng: docs/design/decisions.md, api_contract.md, error_codes.md, routines_catalog.md, transactions.md (tính từ gốc dự án). Checklist TD có 12 tác vụ, gồm auth, retry/chống lặp và kiểm soát phiên trả trước.

Trạng thái: mới có khung phân công/tài liệu; chưa có entrypoint/API chạy được hoặc kết quả kiểm tra được xác nhận.
