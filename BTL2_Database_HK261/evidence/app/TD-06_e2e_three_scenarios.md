# TD-06 — Ba luồng tích hợp thật

Cập nhật sau sửa lỗi ngày 26/10/2026. test_e2e_scenarios.py chạy HTTP test client/MySQL. test_browser_flows.py chạy Chrome/UI/HTTP/MySQL thật, đối chiếu biên lai, tồn 50→48→68, ví 100.000+100.000−30.000=170.000 và doanh thu dịch vụ 30.000. Ảnh/JSON browser là đầu ra test, không phải mô tả kỳ vọng tự gán.

Nguồn kết quả và lệnh tái hiện: [TD_repair_verification.md](TD_repair_verification.md). JUnit giữ ca kiểm tra thực và kết quả; không dùng bằng chứng mock trước review để xác nhận tích hợp.
