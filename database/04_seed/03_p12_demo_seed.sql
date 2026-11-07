-- BTL2 Quản lý quán Net – L09, Nhóm 09
-- Dữ liệu mẫu bổ sung phục vụ năm truy vấn, CRUD, trigger, thủ tục và hàm P1-2 (BD phụ trách)

-- 1. Thêm máy trạm ở các khu vực và trạng thái khác nhau
INSERT INTO `MAY_TRAM` (`MaMay`, `TenMay`, `TrangThaiMay`, `ViTriHang`, `ViTriCot`, `MaNhomMay`, `MaKhuVuc`)
VALUES
    ('M04', 'Máy 04', 'AVAILABLE', 2, 1, 'VIP', 'KV01'),
    ('M05', 'Máy 05', 'ONLINE', 2, 2, 'VIP', 'KV02'),
    ('M06', 'Máy 06', 'OFFLINE', 2, 3, 'VIP', 'KV02');

-- 2. Thêm dịch vụ ở nhóm khác nhau, khoảng giá khác nhau và mức tồn kho đa dạng
INSERT INTO `DICH_VU` (`MaDichVu`, `TenDichVu`, `GiaBanHienHanh`, `SoLuongTon`, `TrangThaiKinhDoanh`, `MaNhomDV`, `MaDonVi`, `MaMayIn`)
VALUES
    ('DV03', 'Cơm chiên trứng', 25000, 30, 'DangKinhDoanh', 'NDV01', 'DVT01', 'MI01'),
    ('DV04', 'Bò húc lon', 18000, 8, 'DangKinhDoanh', 'NDV02', 'DVT02', 'MI01'),
    ('DV05', 'Cà phê sữa', 15000, 0, 'DangKinhDoanh', 'NDV02', 'DVT02', 'MI01'),
    ('DV06', 'Trà chanh sả', 10000, 45, 'NgungKinhDoanh', 'NDV02', 'DVT02', 'MI01');

-- 3. Thêm tài khoản người chơi mẫu với số dư khác nhau
INSERT INTO `TAI_KHOAN` (`MaTaiKhoan`, `TenDangNhap`, `MatKhauBam`, `Ten`, `TrangThai`, `MaNhomND`)
VALUES
    ('TK09', 'player3', 'scrypt:32768:8:1$4Vo8NDFXxVQZeijE$b8550ee326f01ffe822f66bc82b81bc615a58956617aa52e027b230d2b0f2c90c7ea8fefabdf9542fc54ad66e276c4a7dfbda00712fa0c24147d680a9293faff', 'Demo player3', 'HoatDong', 'HoiVien'),
    ('TK10', 'player4', 'scrypt:32768:8:1$4Vo8NDFXxVQZeijE$b8550ee326f01ffe822f66bc82b81bc615a58956617aa52e027b230d2b0f2c90c7ea8fefabdf9542fc54ad66e276c4a7dfbda00712fa0c24147d680a9293faff', 'Demo player4', 'HoatDong', 'HoiVien');

INSERT INTO `NGUOI_CHOI` (`MaTaiKhoan`, `SoCCCD`, `SoDuVi`, `NgayDangKy`)
VALUES
    ('TK09', 'DEMO-TK09', 250000, '2026-10-01'),
    ('TK10', 'DEMO-TK10', 50000, '2026-10-15');

-- 4. Thêm ca trực và phân công trực (bao gồm ca nhân viên trực nhiều khu trong cùng ca để kiểm tra khử trùng)
INSERT INTO `CA_TRUC` (`MaCa`, `TenCa`, `ThoiDiemBatDau`, `ThoiDiemKetThuc`)
VALUES
    ('CA02', 'Ca chiều', '2026-10-26 12:00:00', '2026-10-26 17:00:00'),
    ('CA03', 'Ca tối', '2026-10-26 17:00:00', '2026-10-26 22:00:00');

-- TK03 đã trực CA01 tại KV01 ở reference seed; thêm KV02 cùng CA01 để test khử trùng:
INSERT INTO `PHAN_CONG_TRUC` (`MaNhanVien`, `MaCa`, `MaKhuVuc`, `GhiChuNhiemVu`)
VALUES
    ('TK03', 'CA01', 'KV02', 'Hỗ trợ tăng cường khu khác'),
    ('TK01', 'CA02', 'KV01', 'Quản lý giám sát ca chiều'),
    ('TK07', 'CA02', 'KV01', 'Pha chế ca chiều'),
    ('TK07', 'CA03', 'KV01', 'Pha chế ca tối');

-- 5. Thêm phiên sử dụng và biên lai tiền máy đã thanh toán
INSERT INTO `PHIEN_SU_DUNG` (`MaPhien`, `MaMay`, `MaNguoiChoi`, `ThoiDiemBatDau`, `ThoiDiemKetThuc`, `DonGiaGioApDung`, `HinhThucDangNhap`, `TienNapTruoc`, `TienGiuCho`, `TongTienTamTinh`, `TrangThaiPhien`)
VALUES
    ('PH_P12_01', 'M02', 'TK02', '2026-10-20 08:00:00', '2026-10-20 09:00:00', 15000, 'TraTruoc', 0, 0, 15000, 'DaKetThuc');

INSERT INTO `BIEN_LAI_TIEN_MAY` (`MaBienLai`, `MaPhien`, `ThoiDiemLap`, `TongTienGio`, `TienNhan`, `TienHoan`, `HinhThucThanhToan`, `TrangThaiBienLai`, `ThoiDiemThanhToan`, `MaNhanVienThu`)
VALUES
    ('BL_P12_01', 'PH_P12_01', '2026-10-20 09:00:00', 15000, 15000, 0, 'TruVi', 'DaThanhToan', '2026-10-20 09:00:00', 'TK03');

-- 6. Thêm đơn hàng và chi tiết gọi dịch vụ
-- Khởi tạo đơn ở trạng thái MoiDat để chi tiết cập nhật TongTien qua trigger
INSERT INTO `DON_GOI_DICH_VU` (`MaDonHang`, `ThoiDiemDat`, `KenhDat`, `MaPhien`, `TongTien`, `TrangThaiPhucVu`, `TrangThaiThanhToan`, `SoTienDaHoan`, `MaNhanVienXuLy`)
VALUES
    ('DH_P12_01', '2026-10-20 11:00:00', 'TaiQuay', NULL, 0, 'MoiDat', 'ChuaThanhToan', 0, 'TK03'),
    ('DH_P12_02', '2026-10-21 15:00:00', 'TaiQuay', NULL, 0, 'MoiDat', 'ChuaThanhToan', 0, 'TK03');

-- Chi tiết đơn hàng (trigger tr_chi_tiet_goi_dich_vu_after_insert tự cộng dồn TongTien)
INSERT INTO `CHI_TIET_GOI_DICH_VU` (`MaDonHang`, `MaDichVu`, `SoLuong`, `DonGiaBan`)
VALUES
    ('DH_P12_01', 'DV01', 1, 15000),
    ('DH_P12_01', 'DV02', 1, 12000),
    ('DH_P12_01', 'DV03', 1, 25000),
    ('DH_P12_02', 'DV03', 2, 25000);

-- Chốt trạng thái tiếp nhận và thanh toán cho các đơn demo hoàn tất
UPDATE `DON_GOI_DICH_VU`
SET `TrangThaiPhucVu` = 'DaTiepNhan',
    `TrangThaiThanhToan` = 'DaThanhToan',
    `HinhThucThanhToan` = 'TienMat',
    `ThoiDiemThanhToan` = `ThoiDiemDat`
WHERE `MaDonHang` IN ('DH_P12_01', 'DH_P12_02');

-- 7. Thêm giao dịch ví thành công
INSERT INTO `GIAO_DICH_VI` (`MaGiaoDich`, `MaYeuCau`, `LoaiGiaoDich`, `SoTien`, `ThoiDiemGD`, `TrangThaiGD`, `PhuongThucGD`, `MaNguoiChoi`, `MaNhanVienXuLy`, `MaDonHang`, `MaPhien`, `MaGDGoc`)
VALUES
    ('GD_P12_01', 'YC_P12_01', 'NapTien', 50000, '2026-10-20 07:30:00', 'ThanhCong', 'TienMat', 'TK02', 'TK03', NULL, NULL, NULL),
    ('GD_P12_02', 'YC_P12_02', 'TruTienMay', 15000, '2026-10-20 09:00:00', 'ThanhCong', 'NoiBo', 'TK02', 'TK03', NULL, 'PH_P12_01', NULL),
    ('GD_P12_03', 'YC_P12_03', 'NapTien', 200000, '2026-10-21 14:00:00', 'ThanhCong', 'ChuyenKhoan', 'TK09', 'TK03', NULL, NULL, NULL);
