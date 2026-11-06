# Kiểm thử

Cài dependency từ `apps/backend/requirements-dev.lock`. Từ gốc dự án, với cấu hình MySQL demo trong `.env`:

```bash
apps/backend/.venv/bin/pip install -r apps/backend/requirements-dev.lock
set -a
. ./.env
set +a
export TD_TEST_DB_HOST="$DB_HOST" TD_TEST_DB_PORT="$DB_PORT"
export TD_TEST_DB_PASSWORD="$MYSQL_ROOT_PASSWORD"
TD_BROWSER_EVIDENCE_DIR=evidence/app apps/backend/.venv/bin/python -m pytest tests -q --junitxml=evidence/final_verification/all.xml
```

Với MySQL riêng, đặt thêm TD_TEST_DB_OWNER và TD_TEST_DB_PASSWORD theo tài khoản có quyền tạo/xóa database và user tạm. Không in thông tin bí mật khi chia sẻ log.

| Thư mục | Nội dung |
|---|---|
| `api/` | HTTP, auth/CSRF, đầu vào, quyền, chống lặp và retry |
| `integration/` | Giao dịch nguyên tử, quyền runtime, rollback, tranh chấp, deadlock/lock timeout và ca biên |
| `sql/` | 14 ca P1–2: seed, truy vấn, CRUD, trigger, procedure/function |
| `e2e/` | Ba luồng HTTP và một ca Chrome thực hiện ba luồng giao diện |

Fixture dùng MySQL thật; mỗi ca tạo database `quan_net_test_<random>` và user riêng rồi dọn đúng tài nguyên đó. Không reset database demo. Retry/commit có fault injection để đo hành vi; các ca khóa, rollback và lỗi 1213/1205 còn chạy trên MySQL thật.

Ca trình duyệt cần Playwright và Chrome/Chromium. Thiếu TD_TEST_DB_PORT hoặc trình duyệt sẽ được ghi SKIP, không coi là PASS. Kết quả chính thức cần không SKIP. Clock cố định riêng cho ca trình duyệt để đối chiếu tiền; các ca biên thời gian có kiểm tra riêng.

Kết quả mới nhất: `evidence/final_verification/all.xml` và `summary.json`. Minh chứng API/Chrome được ghi vào `evidence/app/` khi đặt TD_BROWSER_EVIDENCE_DIR.
