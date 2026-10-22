# Chuyển tiếp BTL1 → BTL2

**Nguyên tắc:** hiện thực hệ thống Quản lý quán Net đã phân tích, giữ mốc 23 bảng. Bảng dưới chỉ phân nơi đặt DDL, chưa xác nhận DDL đã có.

| Bảng BTL1 | Khóa chính kế thừa | Tệp DDL dự kiến |
|---|---|---|
| `NHOM_NGUOI_DUNG` | `MaNhomND` | `database/01_schema/01_identity.sql` |
| `TAI_KHOAN` | `MaTaiKhoan` | `database/01_schema/01_identity.sql` |
| `SO_DIEN_THOAI` | `MaTaiKhoan, SoDienThoai` | `database/01_schema/01_identity.sql` |
| `NGUOI_CHOI` | `MaTaiKhoan` | `database/01_schema/01_identity.sql` |
| `NHAN_VIEN` | `MaTaiKhoan` | `database/01_schema/01_identity.sql` |
| `DIA_CHI_NV` | `MaTaiKhoan, STTDiaChi` | `database/01_schema/01_identity.sql` |
| `KHU_VUC` | `MaKhuVuc` | `database/01_schema/02_workstations.sql` |
| `NHOM_MAY` | `MaNhomMay` | `database/01_schema/02_workstations.sql` |
| `BANG_GIA` | `MaNhomND, MaNhomMay` | `database/01_schema/02_workstations.sql` |
| `MAY_TRAM` | `MaMay` | `database/01_schema/02_workstations.sql` |
| `PHIEN_SU_DUNG` | `MaPhien` | `database/01_schema/02_workstations.sql` |
| `BIEN_LAI_TIEN_MAY` | `MaBienLai` | `database/01_schema/02_workstations.sql` |
| `NHOM_DICH_VU` | `MaNhomDV` | `database/01_schema/03_services.sql` |
| `DON_VI_TINH` | `MaDonVi` | `database/01_schema/03_services.sql` |
| `MAY_IN` | `MaMayIn` | `database/01_schema/03_services.sql` |
| `DICH_VU` | `MaDichVu` | `database/01_schema/03_services.sql` |
| `DON_GOI_DICH_VU` | `MaDonHang` | `database/01_schema/03_services.sql` |
| `CHI_TIET_GOI_DICH_VU` | `MaDonHang, MaDichVu` | `database/01_schema/03_services.sql` |
| `PHIEU_KHO` | `MaPhieuKho` | `database/01_schema/04_inventory.sql` |
| `CHI_TIET_PHIEU_KHO` | `MaPhieuKho, STTDong` | `database/01_schema/04_inventory.sql` |
| `CA_TRUC` | `MaCa` | `database/01_schema/05_staff_wallet.sql` |
| `PHAN_CONG_TRUC` | `MaNhanVien, MaCa, MaKhuVuc` | `database/01_schema/05_staff_wallet.sql` |
| `GIAO_DICH_VI` | `MaGiaoDich` | `database/01_schema/05_staff_wallet.sql` |

## Chức năng kế thừa

| UC BTL1 | Nội dung | Nơi triển khai chính |
|---|---|---|
| UC-01 | Tài khoản/đăng nhập/quyền | Nhóm bảng danh tính; backend; UI theo vai trò |
| UC-02/03 | Mở, tính giờ, đóng và quyết toán phiên | Thủ tục phiên, hàm tiền giờ/số dư; API và UI |
| UC-04 | Đơn, tiếp nhận, phục vụ | Thủ tục đơn; UI đơn; Q04 |
| UC-05 | Nạp, thu và hoàn ví | Giao dịch ví; thủ tục; quy tắc chống lặp; Q03 |
| UC-06 | Hủy đơn và đối soát tồn | Ma trận quy tắc; triển khai trước khi bật chức năng hủy/hoàn |
| UC-07 | Phiếu kho, ghi sổ, kiểm kê | Thủ tục kho; Q06/Q07; UI nhân viên |
| UC-08 | Ca và báo cáo | Q05/Q08; UI quản lý |

## Các điểm không được làm mất khi cài đặt

- Chuyên biệt hóa toàn phần/chồng lấp của tài khoản; thực thể yếu và khóa tổ hợp; đa trị đã tách bảng.
- Tiền VND nguyên, giá chụp lịch sử, DATETIME đầy đủ ngày để tính phiên/ca qua đêm.
- Một phiên đang hoạt động mỗi máy/hội viên; đúng chủ ví, đủ số dư sau giữ chỗ.
- Chống gửi lặp bằng mã nghiệp vụ; nhận đơn trừ kho một lần; quyết toán/ghi sổ nguyên tử.
- Lịch sử chứng từ đã chốt bất biến; nạp ví không được cộng lại thành doanh thu tiêu dùng.
- Ràng buộc liên bảng không tự được bảo đảm chỉ bởi FK/CHECK; phải chỉ rõ tầng thực thi.

Đã chốt MySQL 8.4.13 và các chênh lệch vật lý trong [schema_contract.md](schema_contract.md), [change_log.md](change_log.md). MD triển khai các thay đổi đó, giữ nguyên 23 bảng và cột nghiệp vụ gốc. Không dùng kết quả prototype SQLite/Python của BTL1 để tuyên bố MySQL đã kiểm thử thành công.
