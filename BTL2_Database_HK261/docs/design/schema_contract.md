# Hợp đồng lược đồ vật lý đã chốt – MD

Áp dụng MySQL 8.4.13, database `quan_net_btl2`, InnoDB. Bản chụp BTL1 là nguồn tên/cột/khóa, giữ nguyên để đối chiếu. Các quyết định bên dưới chờ được hiện thực trong DDL, không xác nhận DB đã có.

## 1. Quy ước cố định

- Giữ 23 bảng và toàn bộ cột nghiệp vụ bên dưới, đúng chữ hoa/thường. Không dùng AUTO_INCREMENT thay mã VARCHAR hoặc đổi khóa tổ hợp. SQL luôn viết đúng tên IN HOA trên mọi hệ điều hành.
- Giữ kiểu/độ dài/NULL/PK/FK/UQ và chính sách DELETE của model.json. Mã PK/FK chuỗi và MaYeuCau dùng `CHARACTER SET ascii COLLATE ascii_bin` ở cả hai đầu FK; dữ liệu tiếng Việt dùng utf8mb4. Riêng TenDangNhap dùng `utf8mb4_0900_as_ci`, chuẩn hóa trim/NFC trước khi lưu/tra cứu.
- Mặc định DB `utf8mb4_0900_as_cs`. Bật chế độ SQL nghiêm ngặt, giữ CHECK đang được thực thi; không tắt FK/CHECK để nhập dữ liệu sai. Mỗi kết nối đặt múi giờ `+07:00`; DATETIME là giờ Việt Nam.
- Tiền DECIMAL(...,0), không âm trừ cột chênh lệch có dấu; lượng nguyên theo BTL1. API từ chối phần lẻ thay vì để DB tự làm tròn. Khóa/miền/thời gian dùng D-01 đến D-09 trong báo cáo BTL1.
- Mã đối tượng do ứng dụng sinh bằng số ngẫu nhiên mật mã, tối đa 20 ký tự, giữ nguyên khi gửi lại; mã đối tượng gốc của seed không đổi. Không dùng MAX(id)+1.

## 2. Từ điển bảng/cột kế thừa

`?` nghĩa là cột được phép NULL. Chi tiết ý nghĩa, UQ, FK và DELETE lấy từ [model.json](../btl1_baseline/model.json).

| Bảng | PK | Cột nghiệp vụ kế thừa |
|---|---|---|
| `NHOM_NGUOI_DUNG` | `MaNhomND` | `MaNhomND` VARCHAR(10), `TenNhomND` VARCHAR(60) |
| `TAI_KHOAN` | `MaTaiKhoan` | `MaTaiKhoan` VARCHAR(15), `TenDangNhap` VARCHAR(50), `MatKhauBam` VARCHAR(255), `Ho` VARCHAR(30) ?, `TenDem` VARCHAR(40) ?, `Ten` VARCHAR(30), `TrangThai` VARCHAR(20), `MaNhomND` VARCHAR(10) |
| `SO_DIEN_THOAI` | `MaTaiKhoan`, `SoDienThoai` | `MaTaiKhoan` VARCHAR(15), `SoDienThoai` VARCHAR(20) |
| `NGUOI_CHOI` | `MaTaiKhoan` | `MaTaiKhoan` VARCHAR(15), `SoCCCD` VARCHAR(20), `SoDuVi` DECIMAL(12,0), `NgayDangKy` DATE |
| `NHAN_VIEN` | `MaTaiKhoan` | `MaTaiKhoan` VARCHAR(15), `ChucVu` VARCHAR(30), `LuongCoBan` DECIMAL(12,0), `NgayVaoLam` DATE, `MaNguoiQuanLy` VARCHAR(15) ? |
| `DIA_CHI_NV` | `MaTaiKhoan`, `STTDiaChi` | `MaTaiKhoan` VARCHAR(15), `STTDiaChi` INT, `SoNha` VARCHAR(50) ?, `Duong` VARCHAR(100) ?, `PhuongXa` VARCHAR(100) ?, `TinhThanh` VARCHAR(100) |
| `KHU_VUC` | `MaKhuVuc` | `MaKhuVuc` VARCHAR(10), `TenKhuVuc` VARCHAR(60), `MoTaViTri` VARCHAR(255) ? |
| `NHOM_MAY` | `MaNhomMay` | `MaNhomMay` VARCHAR(10), `TenNhomMay` VARCHAR(60), `DonGiaGioMacDinh` DECIMAL(10,0), `MoTa` VARCHAR(255) ? |
| `BANG_GIA` | `MaNhomND`, `MaNhomMay` | `MaNhomND` VARCHAR(10), `MaNhomMay` VARCHAR(10), `DonGiaGio` DECIMAL(10,0) |
| `MAY_TRAM` | `MaMay` | `MaMay` VARCHAR(10), `TenMay` VARCHAR(50), `TrangThaiMay` VARCHAR(20), `ViTriHang` INT ?, `ViTriCot` INT ?, `MaNhomMay` VARCHAR(10), `MaKhuVuc` VARCHAR(10) |
| `PHIEN_SU_DUNG` | `MaPhien` | `MaPhien` VARCHAR(20), `HinhThucDangNhap` VARCHAR(20), `ThoiDiemBatDau` DATETIME, `ThoiDiemKetThuc` DATETIME ?, `DonGiaGioApDung` DECIMAL(10,0), `TienNapTruoc` DECIMAL(12,0), `TienGiuCho` DECIMAL(12,0), `TongTienTamTinh` DECIMAL(12,0), `TrangThaiPhien` VARCHAR(20), `MaMay` VARCHAR(10), `MaNguoiChoi` VARCHAR(15) ? |
| `BIEN_LAI_TIEN_MAY` | `MaBienLai` | `MaBienLai` VARCHAR(20), `MaPhien` VARCHAR(20), `ThoiDiemLap` DATETIME, `ThoiDiemThanhToan` DATETIME ?, `TongTienGio` DECIMAL(12,0), `HinhThucThanhToan` VARCHAR(20), `TienNhan` DECIMAL(12,0), `TienHoan` DECIMAL(12,0), `TrangThaiBienLai` VARCHAR(20), `MaNhanVienThu` VARCHAR(15) ? |
| `CA_TRUC` | `MaCa` | `MaCa` VARCHAR(15), `TenCa` VARCHAR(50), `ThoiDiemBatDau` DATETIME, `ThoiDiemKetThuc` DATETIME |
| `PHAN_CONG_TRUC` | `MaNhanVien`, `MaCa`, `MaKhuVuc` | `MaNhanVien` VARCHAR(15), `MaCa` VARCHAR(15), `MaKhuVuc` VARCHAR(10), `GhiChuNhiemVu` VARCHAR(255) ? |
| `NHOM_DICH_VU` | `MaNhomDV` | `MaNhomDV` VARCHAR(10), `TenNhomDV` VARCHAR(50) |
| `DON_VI_TINH` | `MaDonVi` | `MaDonVi` VARCHAR(10), `TenDonVi` VARCHAR(30) |
| `MAY_IN` | `MaMayIn` | `MaMayIn` VARCHAR(10), `TenMayIn` VARCHAR(50), `ViTriDat` VARCHAR(100) ? |
| `DICH_VU` | `MaDichVu` | `MaDichVu` VARCHAR(10), `TenDichVu` VARCHAR(100), `GiaBanHienHanh` DECIMAL(10,0), `SoLuongTon` INT, `TrangThaiKinhDoanh` VARCHAR(20), `MaNhomDV` VARCHAR(10), `MaDonVi` VARCHAR(10), `MaMayIn` VARCHAR(10) ? |
| `DON_GOI_DICH_VU` | `MaDonHang` | `MaDonHang` VARCHAR(20), `ThoiDiemDat` DATETIME, `KenhDat` VARCHAR(15), `MaPhien` VARCHAR(20) ?, `MaNhanVienXuLy` VARCHAR(15) ?, `TongTien` DECIMAL(12,0), `TrangThaiPhucVu` VARCHAR(20), `TrangThaiTruocHuy` VARCHAR(20) ?, `ThoiDiemHuy` DATETIME ?, `TrangThaiThanhToan` VARCHAR(20), `HinhThucThanhToan` VARCHAR(20) ?, `ThoiDiemThanhToan` DATETIME ?, `SoTienDaHoan` DECIMAL(12,0), `ThoiDiemHoanTien` DATETIME ? |
| `CHI_TIET_GOI_DICH_VU` | `MaDonHang`, `MaDichVu` | `MaDonHang` VARCHAR(20), `MaDichVu` VARCHAR(10), `SoLuong` INT, `DonGiaBan` DECIMAL(10,0), `ThanhTien` DECIMAL(12,0) |
| `PHIEU_KHO` | `MaPhieuKho` | `MaPhieuKho` VARCHAR(20), `LoaiPhieu` VARCHAR(20), `TrangThaiPhieu` VARCHAR(20), `ThoiDiemLap` DATETIME, `ThoiDiemGhiSo` DATETIME ?, `GhiChuLyDo` VARCHAR(255) ?, `MaNhanVienLap` VARCHAR(15), `MaDonHang` VARCHAR(20) ? |
| `CHI_TIET_PHIEU_KHO` | `MaPhieuKho`, `STTDong` | `MaPhieuKho` VARCHAR(20), `STTDong` INT, `MaDichVu` VARCHAR(10), `SoLuong` INT, `SoLuongSoSach` INT ?, `SoLuongThucTe` INT ?, `SoLuongChenhLech` INT, `DonGiaVon` DECIMAL(10,0) |
| `GIAO_DICH_VI` | `MaGiaoDich` | `MaGiaoDich` VARCHAR(20), `MaYeuCau` VARCHAR(100), `LoaiGiaoDich` VARCHAR(20), `SoTien` DECIMAL(12,0), `ThoiDiemGD` DATETIME, `TrangThaiGD` VARCHAR(20), `PhuongThucGD` VARCHAR(20), `MaNguoiChoi` VARCHAR(15), `MaNhanVienXuLy` VARCHAR(15) ?, `MaDonHang` VARCHAR(20) ?, `MaPhien` VARCHAR(20) ?, `MaGDGoc` VARCHAR(20) ? |

## 3. Bổ sung vật lý được chốt

Không thêm bảng nghiệp vụ. Thêm năm cột sinh STORED để dùng UNIQUE có điều kiện theo trạng thái; các cột này không nhận từ API/seed và không đổi cột nghiệp vụ gốc.

| Bảng | Cột sinh / kiểu | Biểu thức | UNIQUE |
|---|---|---|---|
| PHIEN_SU_DUNG | MaMayDangHoatDong VARCHAR(10) ASCII | CASE WHEN TrangThaiPhien='DangHoatDong' THEN MaMay ELSE NULL END | uq_phien_may_active |
| PHIEN_SU_DUNG | MaNguoiChoiDangHoatDong VARCHAR(15) ASCII | CASE WHEN TrangThaiPhien='DangHoatDong' THEN MaNguoiChoi ELSE NULL END | uq_phien_nguoi_active |
| GIAO_DICH_VI | MaPhienThuThanhCong VARCHAR(20) ASCII | CASE WHEN LoaiGiaoDich='TruTienMay' AND TrangThaiGD='ThanhCong' THEN MaPhien ELSE NULL END | uq_vi_thu_phien |
| GIAO_DICH_VI | MaDonHangThuThanhCong VARCHAR(20) ASCII | CASE WHEN LoaiGiaoDich='TruTienDichVu' AND TrangThaiGD='ThanhCong' THEN MaDonHang ELSE NULL END | uq_vi_thu_don |
| GIAO_DICH_VI | MaGDGocHoanThanhCong VARCHAR(20) ASCII | CASE WHEN LoaiGiaoDich='HoanTien' AND TrangThaiGD='ThanhCong' THEN MaGDGoc ELSE NULL END | uq_vi_hoan_goc |

Các cột sinh ASCII dùng `ascii_bin` như cột gốc. UNIQUE vẫn cho phép nhiều NULL nên không chặn các phiên đã đóng hoặc giao dịch chưa thành công. Giữ UQ sẵn có `GIAO_DICH_VI.MaYeuCau` và `BIEN_LAI_TIEN_MAY.MaPhien`.

`CHI_TIET_GOI_DICH_VU.ThanhTien` giữ tên và DECIMAL(12,0), chuyển thành `GENERATED ALWAYS AS (SoLuong * DonGiaBan) STORED`; không INSERT/UPDATE trực tiếp cột này. TongTien ở đầu đơn được tính lại từ tổng dòng trong cùng transaction; trigger đối chiếu khi tiếp nhận. Các kiểu/khóa nghiệp vụ khác không đổi.

Chỉ mục tra cứu khởi điểm: `DON_GOI_DICH_VU(ThoiDiemDat)`, `BIEN_LAI_TIEN_MAY(ThoiDiemThanhToan)`, `GIAO_DICH_VI(MaNguoiChoi,ThoiDiemGD)`, `CA_TRUC(ThoiDiemBatDau,ThoiDiemKetThuc)`. MD bỏ chỉ mục trùng PK/UQ/FK; BD đo EXPLAIN trước/sau trên dữ liệu thực và ghi kết quả, không khẳng định mọi chỉ mục đều tăng tốc.

## 4. Cách đưa vào dự án

- MD tạo DDL ban đầu gồm các cột sinh ở tệp schema tương ứng; các UNIQUE bổ sung ở `database/03_indexes/01_indexes.sql`.
- BD dùng danh sách cột tường minh khi seed và bỏ các cột GENERATED; không INSERT VALUES theo toàn bộ thứ tự cột.
- Ghi chênh lệch CH-01/CH-02 trong change_log.md. Với DB mới, không chạy thêm ALTER lặp lại cột đã có. Migration dành cho DB đã cài bản trước, phải có kiểm tra trạng thái.
- HT dùng FK/CHECK/UQ kết hợp khóa và thủ tục/trigger cho quy tắc liên bảng. UQ không tự bảo đảm máy ONLINE, đủ tiền, đúng chủ ví hoặc chuyên biệt hóa toàn phần.
- MD kiểm tra information_schema đối chiếu đủ 23 bảng, cột gốc, kiểu và PK/FK/UQ/NULL; giải thích rõ năm cột sinh thêm và ThanhTien dẫn xuất trong báo cáo.
