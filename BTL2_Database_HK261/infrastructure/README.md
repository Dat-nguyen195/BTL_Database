# Môi trường đã quyết định

| Thành phần | Cấu hình | Chủ phần |
|---|---|---|
| MySQL | Community Server 8.4.13, InnoDB, database quan_net_btl2, cổng 3306 | MD |
| Chuỗi/giờ | utf8mb4_0900_as_cs; mã ascii_bin; TenDangNhap utf8mb4_0900_as_ci; session +07:00 | MD |
| Backend | Python 3.12, Flask 3.1.3, Connector-Python 26.7.0; 127.0.0.1:5000 | TD |
| Frontend | HTML/CSS/JS modules, Flask phục vụ cùng origin; /api/v1 | TT + TD |
| Transaction | READ COMMITTED, autocommit=False cho ghi; backend service commit/rollback | TD + HT |

MD dùng tài khoản quan_net_owner cho cài đặt và routine SQL SECURITY DEFINER; runtime quan_net_app chỉ SELECT, INSERT bốn bảng nháp DON_GOI_DICH_VU/CHI_TIET_GOI_DICH_VU/PHIEU_KHO/CHI_TIET_PHIEU_KHO và EXECUTE routine cần thiết. Không cấp trực tiếp UPDATE ví/tồn hoặc DDL cho runtime. Mật khẩu nhập trên máy chạy, không ghi vào tệp bàn giao; .env.example chỉ là mẫu.

Không bắt buộc Docker hoặc dịch vụ cloud. Trước nghiệm thu, từng chủ phần bổ sung lệnh cài/khởi động đã thử, phiên bản thực cài, cấu hình thư viện, sao lưu/khôi phục và đường dẫn vào runbook.md. Bản hiện tại là hợp đồng môi trường, chưa phải môi trường đã cài/chạy.
