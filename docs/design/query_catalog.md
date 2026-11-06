# Danh mục truy vấn – BD

Mục tiêu nhóm: tám truy vấn; đề không quy định con số tối thiểu. Mỗi Q-ID cần có tham số, SQL, seed, kết quả chuẩn và bằng chứng thực chạy.

| Mã | UC BTL1 | Nội dung | Ca cần đối chiếu |
|---|---|---|---|
| Q01 | UC-02 | Máy theo nhóm/khu/trạng thái | Không trả máy bảo trì thành máy có thể mở. |
| Q02 | UC-03 | Phiên đang chạy và tiền giờ/giữ chỗ | Có phiên qua ngày và giá 0. |
| Q03 | UC-05 | Số dư và lịch sử giao dịch ví | Chỉ tính giao dịch thành công; đúng chủ. |
| Q04 | UC-04 | Đơn và dòng món theo trạng thái/ngày | Tổng bằng tổng dòng với giá chụp. |
| Q05 | UC-08 | Doanh thu theo ngày/kênh | Không cộng nạp ví; trừ hoàn theo phạm vi hỗ trợ. |
| Q06 | UC-07 | Tồn khả dụng và hàng dưới ngưỡng | Không hiển thị tồn âm như dữ liệu hợp lệ. |
| Q07 | UC-06/07 | Đối soát nhập/xuất/đơn/kiểm kê | Hủy/tái phân loại theo quy tắc BTL1, không trừ hai lần. |
| Q08 | UC-08 | Lịch trực và phát hiện chồng giờ | Cùng nhân viên, khác ca chồng giờ; cho phép hai ca tiếp giáp. |

## Bộ 5 truy vấn đạt chuẩn Mẫu Báo Cáo P1-2 (Updated)

| Mã | Phụ trách | Bảng chính | Yêu cầu cú pháp | Use case / Mục đích |
|---|---|---|---|---|
| Q-P12-01 | MD | `MAY_TRAM` | SELECT, FROM, WHERE, ORDER BY | Thu ngân/quản lý tra cứu danh sách máy đang khả dụng hoặc đang chơi theo khu vực và nhóm máy. |
| Q-P12-02 | BD | `DICH_VU` | SELECT, FROM, WHERE, ORDER BY | Khách hàng lọc thực đơn món ăn/uống đang kinh doanh theo nhóm và khoảng giá mong muốn. |
| Q-P12-03 | BD | `DON_GOI_DICH_VU` | SELECT, FROM, WHERE, GROUP BY, ORDER BY, SUM/COUNT | Quản lý thống kê doanh số đơn hàng đã thanh toán theo ngày và kênh đặt món (Tại máy / Tại quầy). |
| Q-P12-04 | TT | `CA_TRUC`, `PHAN_CONG_TRUC`, `NHAN_VIEN` | SELECT, FROM, WHERE, GROUP BY, ORDER BY, COUNT/SUM | Quản lý chấm công, tính tổng số ca và số giờ trực của nhân viên, khử trùng ca khi trực nhiều khu. |
| Q-P12-05 | HT | `NGUOI_CHOI`, `GIAO_DICH_VI` | 2 cấp Nested Query, WHERE, AVG, ORDER BY | Phân tích tập hội viên có số dư ví cao hơn mức trung bình của nhóm khách hàng có phát sinh giao dịch ví. |

Chi tiết câu lệnh SQL dạng text được lưu tại [01_operations.sql](../../database/05_queries/01_operations.sql) và [02_reports.sql](../../database/05_queries/02_reports.sql). Toàn bộ 5 truy vấn đã được kiểm thử tự động đạt chuẩn tại [test_p12_database.py](../../tests/sql/test_p12_database.py).
