# Kiến trúc đã chốt

Trình duyệt → HTML/CSS/JavaScript modules → `fetch('/api/v1/...')` → Flask routes → services (quyền, transaction) → repositories/Connector-Python → MySQL 8.4.13. Flask đồng thời phục vụ frontend từ apps/frontend, chỉ có một origin cổng 5000; DB ở 3306. Không có frontend dev server riêng hay bước build.

| Thành phần | Nơi đặt | Chủ phần | Trách nhiệm |
|---|---|---|---|
| UI | apps/frontend/index.html, src/pages, src/components, src/services | TT | Màn hình, fetch, CSRF, hiển thị lỗi/quyền; giữ mã thao tác khi retry. |
| Routes | apps/backend/src/routes | TD | Parse/whitelist JSON, đăng nhập, HTTP/DTO và mã lỗi; không chứa luật trừ tiền/tồn. |
| Services | apps/backend/src/services | TD | Một transaction/một thao tác, gọi routine hoặc SQL tạo nháp, commit/rollback, retry, hạn dùng server. |
| Repositories | apps/backend/src/repositories | TD | SQL tham số và CALL, lấy hết result set; không tự commit. |
| CSDL | database/00–08 | MD + BD + HT | DDL/dữ liệu/Q-ID, hàm/thủ tục/trigger, khóa/ràng buộc và lịch sử. |
| Worker phiên trả trước | apps/backend/src/services | TD, HT hỗ trợ | Dùng cùng service/khóa, kết thúc tại hạn dùng đã cấp; không thu phí hai lần. Một worker cho môi trường demo. |

Luồng đọc: xác thực/quyền → SQL tham số/Q-ID → DTO JSON, kết thúc kết nối; tính tiền hiển thị theo server, không tự ghi số dư. Luồng ghi: xác thực/CSRF → service lấy một kết nối → READ COMMITTED → khóa/CALL hoặc đầu+dòng nháp → đọc kết quả → commit → response. Lỗi rollback toàn bộ rồi trả mã thống nhất.

Thư viện trực tiếp cố định: Flask 3.1.3, mysql-connector-python 26.7.0, Python 3.12. Entry point, dependency lock và lệnh chạy đã có trong apps/backend/README.md; môi trường test tách riêng DB/user theo tests/README.md. MD ghi cách cài đúng server; TT tạo UI không cần Node. Sơ đồ kiến trúc báo cáo dùng nguồn draw.io và bản xuất PNG/SVG trong docs/design, không vẽ bằng TeX.

Hợp đồng chi tiết ở decisions.md, schema_contract.md, api_contract.md, routines_catalog.md, error_codes.md và transactions.md. Backend, SQL hỗ trợ và UI demo đã được kiểm chứng; kết quả sau sửa ở evidence/app/TD_repair_verification.md. Việc này không tự xác nhận nghiệm thu phần toàn nhóm.

Sơ đồ đã có: [nguồn draw.io](backend_architecture.drawio), [bản SVG](backend_architecture.svg). Tổng routine cài cho backend gồm 6 procedure chính + 2 helper và 2 function chính + 2 helper; chi tiết ở routines_catalog.md.
