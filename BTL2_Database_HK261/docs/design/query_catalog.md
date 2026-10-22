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
