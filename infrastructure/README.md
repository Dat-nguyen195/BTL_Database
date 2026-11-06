# Môi trường backend và MySQL

MySQL 8.4.13/InnoDB; Python 3.12.3, Flask 3.1.3, Connector/Python 26.7.0 pure Python. API/UI cùng origin localhost:5000. Backend tạo clock Asia/Ho_Chi_Minh; kết nối DB +07:00, READ COMMITTED, autocommit=False.

Chạy demo từ gốc:

```bash
apps/backend/.venv/bin/python scripts/start_backend_demo.py
```

Script dùng compose.backend.yaml, MySQL chỉ bind 127.0.0.1:13307, volume riêng `quan_net_backend_mysql`. `.env` riêng được sinh ngẫu nhiên nếu chưa có; không ghi đè credential hoặc xóa dữ liệu đang có. SECRET_KEY bắt buộc. Quản trị tạo routine với definer quan_net_owner chỉ có quyền DB; quan_net_app chỉ SELECT/EXECUTE/INSERT bốn bảng nháp, không UPDATE ví/tồn. Không cần bật log_bin_trust_function_creators.

`Ctrl+C` dừng backend/worker. `docker compose --env-file .env -f infrastructure/compose.backend.yaml stop` dừng MySQL, giữ dữ liệu. Không dùng `down -v` nếu cần giữ volume. Để chạy lại chỉ cần lệnh demo trên. Kiểm tra đọc môi trường bằng `scripts/check_backend.py`.

Test dùng MySQL riêng trên port do TD_TEST_DB_PORT chỉ định, không dùng DB ứng dụng. Có thể tạo instance tạm:

```bash
docker run --detach --name quan-net-btl2-test -p 127.0.0.1:13306:3306 -e MYSQL_ALLOW_EMPTY_PASSWORD=yes mysql:8.4.13
TD_TEST_DB_PORT=13306 apps/backend/.venv/bin/python -m pytest tests/api tests/integration tests/e2e -q
```

Instance test này chỉ dùng local tạm; test tạo/xóa DB/user mang mã ngẫu nhiên. Dọn đúng instance test bằng `docker rm -f quan-net-btl2-test` sau khi xong. Demo và test dùng hai port/volume độc lập.
