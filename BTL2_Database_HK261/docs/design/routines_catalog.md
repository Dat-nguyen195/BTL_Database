# Hợp đồng thủ tục, hàm và trigger – đã chốt

HT triển khai đúng tên/thứ tự tham số dưới đây trên MySQL 8.4.13. Mọi tham số thủ tục là IN. Backend service mở/commit/rollback transaction; các routine không tự mở/kết thúc transaction. pMaTacNhan do backend lấy từ phiên đăng nhập, pThoiDiem là giờ server lấy một lần cho thao tác; client không được chọn người thực hiện/giá/tổng/giờ chốt.

## 1. Sáu thủ tục chính

| Tên / tệp | Tham số theo đúng thứ tự | Hậu điều kiện |
|---|---|---|
| sp_mo_phien / 01_sessions.sql | pMaPhien VARCHAR(20), pMaMay VARCHAR(10), pMaNguoiChoi VARCHAR(15) NULL, pHinhThucDangNhap VARCHAR(20), pTienNapTruoc DECIMAL(12,0), pMaTacNhan VARCHAR(15), pThoiDiem DATETIME | Khóa ví/máy, kiểm tra quyền, AVAILABLE và phiên trùng; chụp giá từ BANG_GIA, thiếu giá riêng dùng NHOM_MAY.DonGiaGioMacDinh; vãng lai dùng nhóm VangLai. Tạo phiên và ONLINE nguyên tử. MienPhi chỉ QuanLy và mọi khoản 0. |
| sp_ket_thuc_phien / 01_sessions.sql | pMaPhien VARCHAR(20), pMaBienLai VARCHAR(20), pMaGiaoDich VARCHAR(20), pHinhThucThanhToan VARCHAR(20), pTienNhan DECIMAL(12,0), pMaTacNhan VARCHAR(15), pThoiDiem DATETIME | Tính phí/giữ chỗ dưới khóa, tạo đúng một biên lai, thu theo loại phiên, giải phóng máy/giữ chỗ. TruVi đúng chủ/đủ khả dụng và gio:{MaPhien}; 0 đồng không tạo GD ví. TraSau chưa thu dùng pHinhThucThanhToan='ChuaThu' như giá trị điều khiển, không lưu vào cột hình thức. |
| sp_nap_vi / 02_wallet_orders.sql | pMaGiaoDich VARCHAR(20), pMaYeuCau VARCHAR(100), pMaNguoiChoi VARCHAR(15), pSoTien DECIMAL(12,0), pPhuongThucGD VARCHAR(20), pMaTacNhan VARCHAR(15), pThoiDiem DATETIME | ThuNgan/QuanLy xác nhận; số tiền dương; TienMat/ChuyenKhoan. Khóa ví, kiểm tra replay, ghi NapTien/ThanhCong và cộng một lần. |
| sp_tiep_nhan_don / 02_wallet_orders.sql | pMaDonHang VARCHAR(20), pMaTacNhan VARCHAR(15), pThoiDiem DATETIME | ThuNgan/PhaChe/QuanLy, đơn MoiDat đủ dòng; khóa món tăng dần, kiểm tra tồn/tổng, trừ một lần và chuyển DaTiepNhan, gán MaNhanVienXuLy. |
| sp_thanh_toan_don / 02_wallet_orders.sql | pMaDonHang VARCHAR(20), pMaGiaoDich VARCHAR(20), pHinhThucThanhToan VARCHAR(20), pMaTacNhan VARCHAR(15), pThoiDiem DATETIME | Chỉ thu đơn đã tiếp nhận/chế biến/giao chưa thu. Người chơi chỉ tự trả TruVi của mình; tiền mặt/chuyển khoản do ThuNgan/QuanLy xác nhận. TaiQuay không TruVi. Thu đúng tổng, ghi dv:{MaDonHang} nếu trừ ví >0; không đổi tồn. |
| sp_ghi_so_phieu_kho / 03_inventory.sql | pMaPhieuKho VARCHAR(20), pMaTacNhan VARCHAR(15), pThoiDiem DATETIME | QuanLy duyệt phiếu Nhap đủ dòng; tính delta theo loại, khóa món, kiểm tra ảnh kiểm kê/tồn không âm, cập nhật kho và DaGhiSo nguyên tử. Bản demo cho NhapKho/XuatHuy/KiemKe; TaiPhanLoai chưa có API tạo vì phụ thuộc hủy. |

Routine trả đúng một result set một dòng: `MaDoiTuong VARCHAR(20)`, `DaThucHienTruoc TINYINT` (0/1). TD đọc hết result set rồi truy vấn DTO cần trả trên cùng kết nối; lỗi SIGNAL theo error_codes.md. pMaBienLai/pMaGiaoDich do TD sinh ngẫu nhiên tối đa 20 ký tự; nếu replay thì trả đối tượng đã có. Với HTTP pMaTacNhan không NULL; worker kết thúc phiên tự động có ngữ cảnh hệ thống riêng, MaNhanVienThu NULL, không nhận danh tính này từ request.

`ChuaThu` chỉ là giá trị điều khiển cho kết thúc trả sau: BIEN_LAI lưu TrangThaiBienLai=ChuaThanhToan, HinhThucThanhToan=TienMat (phương thức dự kiến), thời điểm thanh toán NULL, nhận/hoàn 0. Không ghi doanh thu. Chưa có API thu công nợ về sau trong demo; ghi giới hạn này. Tiền nhận vãng lai trả trước được lấy từ TienNapTruoc đã lưu, tiền hoàn tính ở lúc đóng; không nhận lại tiền hai lần. Với hội viên TruVi, pTienNhan=0. Khoản 0 giữ chứng từ 0 đồng, không vi phạm GD ví SoTien>0.

## 2. Hai hàm

| Hàm | Tham số | Kết quả / giới hạn |
|---|---|---|
| fn_tien_gio | pBatDau DATETIME, pKetThuc DATETIME, pDonGiaGio DECIMAL(10,0) | DECIMAL(12,0) = FLOOR(TIMESTAMPDIFF(SECOND,pBatDau,pKetThuc)*pDonGiaGio/3600); thời gian đầy đủ ngày, kết thúc >= bắt đầu, giá >=0, kiểm tra tràn. Không dùng FLOAT. |
| fn_so_du_kha_dung | pMaNguoiChoi VARCHAR(15) | DECIMAL(12,0) = SoDuVi - SUM(TienGiuCho của phiên TraTruoc đang hoạt động). READS SQL DATA, không ghi/commit; caller phải làm mới giữ chỗ theo giờ server dưới khóa trước khi dùng để quyết định chi. |

fn_tien_gio khai báo DETERMINISTIC/NO SQL; fn_so_du_kha_dung không khai báo DETERMINISTIC vì đọc dữ liệu thay đổi. fn_so_du_kha_dung một mình không thay cơ chế khóa/kiểm soát hạn dùng trong transactions.md.

## 3. Ba nhóm trigger

| Nhóm / tệp | Việc phải làm | Giới hạn |
|---|---|---|
| Lịch sử / 01_history.sql | BEFORE UPDATE/DELETE trên biên lai đã thu, ví đã kết thúc, phiếu đã ghi sổ; bảo vệ đầu/dòng đơn sau tiếp nhận, dòng phiếu sau ghi sổ. | Cho phép đúng các trường trạng thái chuyển hợp lệ theo nghiệp vụ; không chặn toàn bộ UPDATE khiến routine không hoạt động. Không cập nhật lại bảng đang kích hoạt trigger. |
| Trạng thái/liên bảng / 02_state_identity.sql | Kiểm tra chuỗi trạng thái, tổng/giá chụp, đúng chủ ví/phiên, ảnh kiểm kê và điều kiện chưa bao phủ bởi CHECK/UQ tại điểm chuyển. | Không gán cùng tác dụng trừ ví/trừ tồn cho cả trigger lẫn routine: **routine sở hữu cập nhật ví/tồn**, trigger kiểm tra/từ chối. |
| Danh tính/chuyên biệt hóa / 02_state_identity.sql | Chặn xóa lớp con cuối khi cha còn tồn tại; kiểm tra tham chiếu/quản lý theo phạm vi seed/luồng hỗ trợ. | MySQL không có CHECK hoãn đến COMMIT để bảo đảm tạo cha đã có con. Tạo tài khoản chỉ qua seed giao dịch cha+ít nhất một con và hậu kiểm trước commit; ứng dụng không có API tạo/xóa hồ sơ. Không tuyên bố FK/trigger đã tự bảo đảm toàn phần ở mọi thao tác SQL tùy ý. |

Một nhóm có thể cần nhiều CREATE TRIGGER. HT ghi đủ BR/D-ID, nơi thực thi, ca kiểm tra và giới hạn trong rules_matrix.md. Các thao tác quản lý chu trình nhân viên, ca/hủy/hoàn ngoài API vẫn cần dữ liệu hợp lệ và đánh giá rõ, không tự đánh dấu đã hỗ trợ.
