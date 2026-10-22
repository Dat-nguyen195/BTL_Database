# Frontend – TT

Đã chốt HTML5/CSS3/JavaScript ES modules, không framework/build/Node. Tạo index.html và các module trong src/pages, src/components, src/services. Flask phục vụ các tệp UI cùng origin http://127.0.0.1:5000; fetch /api/v1 bằng đường dẫn tương đối. Không mở index.html bằng file:// để demo.

Theo ui_scope.md/api_contract.md: login/session/CSRF, quyền trên menu và form, envelope/mã lỗi dùng chung, trạng thái tải/rỗng/lỗi. Nút chặn bấm lặp kết hợp giữ mã P/O/K/G và nap:{UUID} để retry; không tự tính số dư/giá cho nghiệp vụ thu. Không cần package.json/lockfile frontend; README phải có cách truy cập qua Flask sau khi tích hợp.

Checklist TT có 12 tác vụ. Trạng thái: mới có khung phân công/tài liệu, chưa có UI tích hợp chạy được hoặc kết quả kiểm tra được xác nhận.
