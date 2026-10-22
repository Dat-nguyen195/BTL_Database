# Nhật ký quyết định và thay đổi thiết kế

Mốc gốc: docs/btl1_baseline/model.json (23 bảng), giữ nguyên checksum. Các dòng dưới đã được người dùng cho phép chốt để triển khai; **chưa có DDL/migration đã chạy được xác nhận**.

| Mã | Phạm vi | Quyết định | Lý do | Nơi thực hiện | Trạng thái |
|---|---|---|---|---|---|
| CH-01 | Lược đồ vật lý | Giữ tên/kiểu/khóa/NULL nghiệp vụ; MySQL 8.4.13, charset/collation, SQL nghiêm ngặt, +07:00 theo schema_contract.md. | Kế thừa BTL1, thống nhất môi trường và so khớp mã/đăng nhập. | database/00_bootstrap, 01_schema, 02_constraints | Đã chốt, chờ hiện thực/kiểm tra |
| CH-02 | PHIEN_SU_DUNG, GIAO_DICH_VI, CHI_TIET_GOI_DICH_VU | Năm cột sinh và UNIQUE có điều kiện; ThanhTien thành generated STORED; không thêm bảng nghiệp vụ. | Chặn phiên/thu/hoàn trùng và dẫn xuất thành tiền. | database/01_schema, 03_indexes; schema_contract.md | Đã chốt, chờ hiện thực/kiểm tra |
| KT-04–10 | Ứng dụng/API/giao dịch | Flask + JS cùng origin, API v1, auth/CSRF, backend service sở hữu transaction, khóa và mã lỗi thống nhất. | Cho các thành viên triển khai trực tiếp, tránh hợp đồng khác nhau. | apps, docs/design, tests | Đã chốt, chờ hiện thực/kiểm tra |

MD đưa các lựa chọn vật lý vào DDL mới. Nếu nâng DB đã cài bản trước, tạo migration có điều kiện tương ứng trong database/migrations; không chạy ALTER thêm trùng cột trên DB tạo bằng DDL mới. Mỗi thay đổi phát sinh phải cập nhật hợp đồng, seed, SQL nghiệp vụ, API, kiểm tra và báo cáo bị ảnh hưởng; ghi lý do cụ thể thay vì mở lại quyết định công nghệ chung.
