# Quyết định kỹ thuật BTL2 – đã chốt để triển khai

Các lựa chọn dưới đây được chốt theo yêu cầu của người dùng, áp dụng cho toàn bộ BTL2. Các thành viên triển khai theo tài liệu này; kiểm tra chéo dùng để tìm lỗi cài đặt, không cần họp lại để chọn công nghệ hay hợp đồng. Đây là quyết định thiết kế, chưa phải kết quả chạy hệ thống.

| Mã | Nội dung | Quyết định áp dụng | Người triển khai |
|---|---|---|---|
| KT-01 | CSDL | **MySQL Community Server 8.4.13**, nhánh 8.4 LTS; database `quan_net_btl2`; InnoDB; cổng 3306. | MD |
| KT-02 | Dữ liệu và tên | Giữ đủ **23 bảng**, tên bảng IN HOA và tên cột/PK/FK/UQ/NULL nghiệp vụ đúng `../btl1_baseline/model.json`. Không đổi sang tên tiếng Anh hoặc thêm bảng nghiệp vụ. Các bổ sung vật lý được liệt kê trong schema_contract.md. | MD |
| KT-03 | Chuỗi/thời gian/tiền | UTF-8 `utf8mb4_0900_as_cs`; mã PK/FK dạng chuỗi và MaYeuCau dùng ASCII `ascii_bin`; TenDangNhap dùng `utf8mb4_0900_as_ci`. DB DATETIME lưu giờ Việt Nam, phiên kết nối `+07:00`; JSON thời gian ISO 8601 có `+07:00`. Tiền VND nguyên, giữ DECIMAL của BTL1, không FLOAT. | MD + BD + TD |
| KT-04 | Backend | **Python 3.12**, **Flask 3.1.3**, **mysql-connector-python 26.7.0**. Truy vấn SQL có tham số và CALL trực tiếp, không ORM. TD ghi phiên bản vá Python và khóa toàn bộ thư viện thực cài trong sản phẩm bàn giao. | TD |
| KT-05 | Frontend | **HTML5/CSS3/JavaScript ES modules**, `fetch`; không bước build. Flask phục vụ `apps/frontend/` và API cùng origin `http://127.0.0.1:5000`; các thư mục pages/components/services chứa module JS. | TT + TD |
| KT-06 | API | REST JSON dưới `/api/v1`; giữ tên trường nghiệp vụ theo BTL1; envelope thành công/lỗi, quyền và endpoint theo api_contract.md; mã lỗi theo error_codes.md. | TD + TT |
| KT-07 | SQL nghiệp vụ | Sáu thủ tục chính, hai hàm và ba nhóm trigger theo routines_catalog.md. Tạo đơn/phiếu nháp dùng SQL có tham số trong service transaction; không trừ tiền/tồn ở thao tác tạo nháp. | HT + TD |
| KT-08 | Giao dịch | **Backend service sở hữu transaction**: `autocommit=False`, `READ COMMITTED`, một kết nối/một thao tác ghi; BEGIN → CALL/SQL → kiểm tra kết quả → COMMIT; lỗi thì ROLLBACK. Thủ tục, hàm, trigger không tự START TRANSACTION/COMMIT/ROLLBACK. | TD + HT |
| KT-09 | Quyền và đăng nhập | Tài khoản seed có mật khẩu băm; Flask signed session cookie HttpOnly/SameSite=Lax, CSRF token cho thao tác ghi. Quyền suy từ NGUOI_CHOI, NHAN_VIEN.ChucVu và chủ tài nguyên; NHOM_NGUOI_DUNG chỉ là nhóm giá. | TD + BD + TT |
| KT-10 | Chống lặp và khóa | Khóa sự kiện `gio:{MaPhien}`, `dv:{MaDonHang}`, `nap:{UUID}`; kiểm tra cùng khóa khác nội dung. Mở phiên/tạo nháp dùng mã đối tượng ổn định. Thứ tự khóa, retry và kiểm tra hai kết nối theo transactions.md. | HT + TD + MD |
| KT-11 | Phạm vi ứng dụng | Ba luồng trong PLAN, có đăng nhập và người chơi/nhân viên/quản lý. Danh mục/tài khoản/ca được seed và đọc; không làm CRUD tổng quát. Hủy/hoàn, trả hàng, sửa lịch sử không có API/nút ghi trong bản demo này; quy tắc chưa hỗ trợ phải ghi rõ. | Cả năm |
| KT-12 | Cài đặt/demo | DB cài riêng; một tiến trình Flask phục vụ UI/API. Không bắt buộc Docker, Node hay dịch vụ cloud. Máy trạm trong demo là mô phỏng quyền sử dụng phiên; không tuyên bố đã điều khiển máy vật lý. Phiên trả trước phải được kiểm soát hạn dùng trên server theo BTL1. | MD + TD + TT |

## Tài liệu dùng để thực hiện

- [Hợp đồng lược đồ](schema_contract.md): tên, kiểu, cột sinh, khóa và chênh lệch vật lý.
- [Hợp đồng API](api_contract.md), [mã lỗi](error_codes.md), [thủ tục/hàm/trigger](routines_catalog.md), [giao dịch và chống lặp](transactions.md).
- [Kiến trúc](architecture.md), [phạm vi màn hình](ui_scope.md), [nhật ký thay đổi](change_log.md).

## Cơ sở lựa chọn

Giữ MySQL và mô hình BTL1 giúp cả nhóm tập trung vào SQL, ràng buộc và demo đúng rubric. Flask cùng giao diện JavaScript không build giảm phần cài đặt; SQL vẫn hiện rõ để giải thích khi hỏi đáp. Backend quản lý transaction giúp gộp tạo nháp nhiều dòng hoặc CALL với kiểm tra hậu điều kiện trong một lần commit.

Đã đối chiếu phiên bản/tính năng với nguồn chính thức: [MySQL 8.4.13](https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-13.html), [Python 3.12](https://www.python.org/downloads/), [Flask 3.1.3](https://flask.palletsprojects.com/en/stable/changes/), [Connector/Python 26.7.0](https://pypi.org/project/mysql-connector-python/26.7.0/), [transaction MySQL](https://dev.mysql.com/doc/refman/8.4/en/commit.html), [autocommit của connector](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-autocommit.html), [chỉ mục trên cột sinh](https://dev.mysql.com/doc/refman/8.4/en/create-table-secondary-indexes.html).

Tên/ngày bài nộp trên LMS là thông tin hành chính TT cần kiểm tra theo đề gốc; không còn quyết định công nghệ đang chờ nhóm chọn. Chỉ sửa hợp đồng nếu phát hiện mâu thuẫn với đề/BTL1 hoặc lỗi khả thi cụ thể, và ghi lại thay đổi cùng các tệp bị ảnh hưởng.
