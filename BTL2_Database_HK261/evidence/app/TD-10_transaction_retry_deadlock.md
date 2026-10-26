# TD-10 — Transaction, retry và tranh chấp

Cập nhật sau sửa lỗi ngày 26/10/2026. Có fault injection đếm tối đa ba lần, lỗi nghiệp vụ không retry, commit lỗi không trả thành công; ngoài ra ép deadlock 1213/timeout 1205 thật và tranh máy/món cuối/ví bằng hai kết nối. Ràng buộc, khóa và rollback được kiểm tra trên MySQL thật.

Nguồn kết quả và lệnh tái hiện: [TD_repair_verification.md](TD_repair_verification.md). JUnit giữ ca kiểm tra thực và kết quả; không dùng bằng chứng mock trước review để xác nhận tích hợp.
