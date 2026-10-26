# API – TD

Auth/CSRF, quyền hiện tại và chủ tài nguyên, JSON/whitelist/integer, API đọc/ghi, replay và hạn dùng. Fixture dùng MySQL thật. Các test transaction fault injection chỉ kiểm tra rollback/retry/commit và không được coi là bằng chứng khóa DB; tests/integration kiểm chứng phần đó bằng hai kết nối thật. Hướng dẫn tại tests/README.md.
