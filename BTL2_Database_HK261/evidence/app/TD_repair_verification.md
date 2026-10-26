# Kết quả sửa lỗi và nghiệm thu kỹ thuật phần TD — 26/10/2026

Đã sửa các phát hiện R01–R16 trong review trước. **78 ca kiểm thử riêng biệt đạt**, 0 failure/error/skip. Lượt đầy đủ: 77 ca/287,13 giây; sau chỉnh sửa cuối chạy thêm 8 ca/24,40 giây (7 ca chạy lại, 1 ca chụp dữ liệu thật mới). Không cộng lặp thành 85 ca. JUnit gốc giữ riêng; bản gộp theo classname/name chỉ phục vụ tra cứu.

## Tệp kiểm chứng

- [Lượt chính](TD_test_results.xml), [lượt bổ sung](TD_followup_results.xml), [78 ca riêng biệt](TD_verified_results.xml), [tổng hợp JSON](TD_verification_summary.json).
- [Request/response thực đã bỏ bí mật](TD_api_samples.json): tạo nạp 201, replay 200, khác nội dung 409, số tiền lẻ 422; ví tăng đúng 10.000đ một lần.
- [Chrome E2E](TD_browser_three_flows.json), [ảnh giao diện](TD_browser_three_flows.png): D1 có biên lai/giải phóng máy; D2 nạp lặp chỉ cộng một lần, tiếp nhận trừ kho, thu ví; D3 nhập kho/ghi sổ lặp, tồn cuối 68 và doanh thu dịch vụ 30.000đ, không cộng nạp ví.

## Môi trường và lệnh tái hiện

Python 3.12.3, Flask 3.1.3, Connector/Python 26.7.0 pure Python, Werkzeug 3.1.9; MySQL Docker 8.4.13. Browser version được lấy trực tiếp trong JSON E2E; Playwright 1.56.0, Chrome cài sẵn. Các DB/user test là tài nguyên ngẫu nhiên riêng, được xóa sau test. Backend dùng tài khoản hạn quyền, không UPDATE trực tiếp ví/tồn.

```bash
TD_TEST_DB_PORT=13306 TD_BROWSER_EVIDENCE_DIR=evidence/app \
  apps/backend/.venv/bin/python -m pytest tests/api tests/integration tests/e2e -q --junitxml=evidence/app/TD_test_results.xml
```

Xem tests/README.md để chuẩn bị MySQL riêng và dependency. Lượt test trình duyệt dùng clock cố định để kết quả tiền xác định, còn các ca hạn/worker có kiểm tra thời điểm riêng. Fault injection cho mất kết nối/commit thất bại và giới hạn retry được ghi rõ trong test; deadlock 1213, lock timeout 1205, rollback dòng thứ hai và tranh máy/tồn/ví còn được kiểm tra trên MySQL thật. Không còn MockCursor/MockConnection mô phỏng SQL.

## Đối chiếu review

| Review | Thay đổi đã thực hiện | Bằng chứng tiêu biểu |
|---|---|---|
| R01 | Bỏ DATE_FORMAT thời gian có %s; trả DATETIME và serialize ISO +07:00 | Bộ API/E2E chạy Connector thật |
| R02–R03 | Bắt buộc SECRET_KEY; quyền/trạng thái DB mỗi request và cùng transaction ghi | secret_required, account_revocation, role_revocation |
| R04 | Kiểm tra chủ tài nguyên trước replay | pay_replay_enforces_owner_and_method |
| R05 | Ngân sách hội viên dùng SoDuVi; TienGiuCho chỉ là phí đã phát sinh | wallet_uses_balance_not_accrued_holding, holding_prevents_spending |
| R06–R07 | Chốt tại hạn dưới khóa; chặn phiên quá hạn; nạp muộn quyết toán cũ trước | worker_closes_at_deadline, expired_session_cannot_create_order, late_topup |
| R08–R09 | So đầy đủ dữ liệu replay; phục hồi sau UNIQUE bằng giao dịch mới; dùng cờ routine | inventory_replay, topup_replay_checks_actor, two_identical_draft_requests |
| R10 | Integer đúng kiểu/miền, whitelist/JSON/object từng dòng | Các ca parametrized noninteger, invalid_order_line, malformed_json |
| R11 | Lỗi result-set/commit truyền về rollback, không trả thành công | result_read_error_propagates, commit_failure_never_returns_success |
| R12 | Clock Asia/Ho_Chi_Minh, DATETIME → ISO +07:00 | API thật và CanUseUntil/worker assertions |
| R13–R14 | Q07 cộng lượng bán độc lập, Q08 khác MaCa và giao khoảng | q07_counts_sales, shifts_deduplicate_same_shift_and_include_overnight |
| R15 | Tách quyền tạo/đọc/tiếp nhận cho PhaChe | barista_can_read_but_cannot_create_counter_order |
| R16 | Thay fixture giả bằng MySQL/Chrome, sửa báo cáo và minh chứng | JUnit, JSON, ảnh trình duyệt trong thư mục này |

SQL dùng charset/collation ASCII cho tham số mã và helper khóa SQL SECURITY DEFINER để runtime không cần UPDATE. Có kiểm tra 1213/1205 thật và quyền UPDATE bị MySQL từ chối.

## Phạm vi và giới hạn

Giao diện là bản demo tích hợp cho phần TD, không xác nhận phần frontend cuối của TT. Bộ SQL hỗ trợ cài mới không tự xác nhận mọi tác vụ MD/BD/HT hoặc toàn bộ BR BTL1 đã nghiệm thu. Chưa có API hủy/hoàn/thu công nợ trả sau/CRUD quản trị. Q07 phân nhóm bán theo ngày đặt do baseline không có thời điểm tiếp nhận; không khẳng định mốc xuất kho chính xác khi đặt và nhận khác ngày. Mô phỏng phiên, chưa điều khiển máy vật lý; một worker/process demo. Review chéo thực tế với thành viên HT chưa được giả nhận là đã diễn ra.

Các tệp minh chứng TD trước review đã được cập nhật trỏ tới kết quả thực này; không giữ nguyên các tuyên bố PASS chỉ dựa vào mock.
