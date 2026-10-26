# Kiểm thử backend TD

Cài dependency: `apps/backend/.venv/bin/pip install -r apps/backend/requirements-dev.lock`.

```bash
TD_TEST_DB_PORT=13306 TD_BROWSER_EVIDENCE_DIR=evidence/app   apps/backend/.venv/bin/python -m pytest tests/api tests/integration tests/e2e -q --junitxml=evidence/app/TD_test_results.xml
```

- tests/api: hợp đồng HTTP, auth, validation và trường hợp nghiệp vụ; phần cần DB dùng MySQL thật. Retry/commit/result-set có fault injection để đếm chính xác hành vi, không giả là lỗi mạng thật.
- tests/integration: hồi quy R01–R16, transaction nguyên tử, runtime hạn quyền và hai kết nối tranh chấp. Có ca ép deadlock 1213 và lock timeout 1205 trên MySQL thật.
- tests/e2e/test_e2e_scenarios.py: ba luồng HTTP qua Flask test client tới MySQL thật.
- tests/e2e/test_browser_flows.py: ba luồng qua UI, HTTP server và Chrome thật tới MySQL. Clock cố định trong riêng ca browser để so số tiền xác định; ca worker/phí biên có kiểm tra riêng.

Fixture không mock SQL/CALL. Mỗi test DB tạo database `quan_net_test_<random>` và user hạn quyền riêng, dọn chúng sau test; không reset dữ liệu ứng dụng. Không đặt TD_TEST_DB_PORT thì các ca cần DB SKIP rõ ràng. Browser cần Chrome/Chromium và Playwright; thiếu chúng ghi SKIP, không ghi PASS. Minh chứng chính thức phải chạy đủ không SKIP.

Connector 26.7.0 phát DeprecationWarning cho stored_results(); API này vẫn hoạt động trong phiên bản đã khóa. Khi nâng Connector, kiểm tra API result-set mới trước khi đổi adapter.
