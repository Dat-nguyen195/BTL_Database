-- Standalone installer for quan_net_btl2. Open and execute this entire file in MySQL Workbench.
-- Use a new or empty database; existing tables will cause installation errors.
-- Source files are embedded below in dependency order; SOURCE commands are not required.
SET NAMES utf8mb4;
SET time_zone = '+07:00';
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- BEGIN 00_bootstrap/00_create_database.sql
CREATE DATABASE IF NOT EXISTS quan_net_btl2 CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs;
-- END 00_bootstrap/00_create_database.sql

USE `quan_net_btl2`;

-- BEGIN 01_schema/01_identity.sql
-- MySQL 8.4.13; baseline 23 tables. Added to unblock backend integration.

CREATE TABLE `NHOM_NGUOI_DUNG` (
  `MaNhomND` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `TenNhomND` VARCHAR(60) NOT NULL,
  PRIMARY KEY (`MaNhomND`),
  CONSTRAINT `uq_nhom_nguoi_dung_0` UNIQUE (`TenNhomND`)
) ENGINE=InnoDB;

CREATE TABLE `TAI_KHOAN` (
  `MaTaiKhoan` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `TenDangNhap` VARCHAR(50) COLLATE utf8mb4_0900_as_ci NOT NULL,
  `MatKhauBam` VARCHAR(255) NOT NULL,
  `Ho` VARCHAR(30) NULL,
  `TenDem` VARCHAR(40) NULL,
  `Ten` VARCHAR(30) NOT NULL,
  `TrangThai` VARCHAR(20) NOT NULL,
  `MaNhomND` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  PRIMARY KEY (`MaTaiKhoan`),
  CONSTRAINT `uq_tai_khoan_0` UNIQUE (`TenDangNhap`),
  CONSTRAINT `ck_tai_khoan_0` CHECK (TrangThai IN ('HoatDong','Khoa','TamDung'))
) ENGINE=InnoDB;

CREATE TABLE `SO_DIEN_THOAI` (
  `MaTaiKhoan` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `SoDienThoai` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`MaTaiKhoan`,`SoDienThoai`)
) ENGINE=InnoDB;

CREATE TABLE `NGUOI_CHOI` (
  `MaTaiKhoan` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `SoCCCD` VARCHAR(20) NOT NULL,
  `SoDuVi` DECIMAL(12,0) NOT NULL,
  `NgayDangKy` DATE NOT NULL,
  PRIMARY KEY (`MaTaiKhoan`),
  CONSTRAINT `uq_nguoi_choi_0` UNIQUE (`SoCCCD`),
  CONSTRAINT `ck_nguoi_choi_0` CHECK (SoDuVi>=0)
) ENGINE=InnoDB;

CREATE TABLE `NHAN_VIEN` (
  `MaTaiKhoan` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `ChucVu` VARCHAR(30) NOT NULL,
  `LuongCoBan` DECIMAL(12,0) NOT NULL,
  `NgayVaoLam` DATE NOT NULL,
  `MaNguoiQuanLy` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NULL,
  PRIMARY KEY (`MaTaiKhoan`),
  CONSTRAINT `ck_nhan_vien_0` CHECK (ChucVu IN ('QuanLy','ThuNgan','PhaChe','KyThuat')),
  CONSTRAINT `ck_nhan_vien_1` CHECK (LuongCoBan>=0)
) ENGINE=InnoDB;

CREATE TABLE `DIA_CHI_NV` (
  `MaTaiKhoan` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `STTDiaChi` INT NOT NULL,
  `SoNha` VARCHAR(50) NULL,
  `Duong` VARCHAR(100) NULL,
  `PhuongXa` VARCHAR(100) NULL,
  `TinhThanh` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`MaTaiKhoan`,`STTDiaChi`),
  CONSTRAINT `ck_dia_chi_nv_0` CHECK (STTDiaChi>0)
) ENGINE=InnoDB;
-- END 01_schema/01_identity.sql

-- BEGIN 01_schema/02_workstations.sql
-- MySQL 8.4.13; baseline 23 tables. Added to unblock backend integration.

CREATE TABLE `KHU_VUC` (
  `MaKhuVuc` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `TenKhuVuc` VARCHAR(60) NOT NULL,
  `MoTaViTri` VARCHAR(255) NULL,
  PRIMARY KEY (`MaKhuVuc`),
  CONSTRAINT `uq_khu_vuc_0` UNIQUE (`TenKhuVuc`)
) ENGINE=InnoDB;

CREATE TABLE `NHOM_MAY` (
  `MaNhomMay` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `TenNhomMay` VARCHAR(60) NOT NULL,
  `DonGiaGioMacDinh` DECIMAL(10,0) NOT NULL,
  `MoTa` VARCHAR(255) NULL,
  PRIMARY KEY (`MaNhomMay`),
  CONSTRAINT `uq_nhom_may_0` UNIQUE (`TenNhomMay`),
  CONSTRAINT `ck_nhom_may_0` CHECK (DonGiaGioMacDinh>=0)
) ENGINE=InnoDB;

CREATE TABLE `BANG_GIA` (
  `MaNhomND` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaNhomMay` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `DonGiaGio` DECIMAL(10,0) NOT NULL,
  PRIMARY KEY (`MaNhomND`,`MaNhomMay`),
  CONSTRAINT `ck_bang_gia_0` CHECK (DonGiaGio>=0)
) ENGINE=InnoDB;

CREATE TABLE `MAY_TRAM` (
  `MaMay` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `TenMay` VARCHAR(50) NOT NULL,
  `TrangThaiMay` VARCHAR(20) NOT NULL,
  `ViTriHang` INT NULL,
  `ViTriCot` INT NULL,
  `MaNhomMay` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaKhuVuc` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  PRIMARY KEY (`MaMay`),
  CONSTRAINT `uq_may_tram_0` UNIQUE (`TenMay`),
  CONSTRAINT `ck_may_tram_0` CHECK (TrangThaiMay IN ('AVAILABLE','ONLINE','MAINTENANCE','OFFLINE'))
) ENGINE=InnoDB;

CREATE TABLE `PHIEN_SU_DUNG` (
  `MaPhien` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `HinhThucDangNhap` VARCHAR(20) NOT NULL,
  `ThoiDiemBatDau` DATETIME NOT NULL,
  `ThoiDiemKetThuc` DATETIME NULL,
  `DonGiaGioApDung` DECIMAL(10,0) NOT NULL,
  `TienNapTruoc` DECIMAL(12,0) NOT NULL,
  `TienGiuCho` DECIMAL(12,0) NOT NULL,
  `TongTienTamTinh` DECIMAL(12,0) NOT NULL,
  `TrangThaiPhien` VARCHAR(20) NOT NULL,
  `MaMay` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaNguoiChoi` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NULL,
  `MaMayDangHoatDong` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin GENERATED ALWAYS AS (CASE WHEN TrangThaiPhien='DangHoatDong' THEN MaMay ELSE NULL END) STORED,
  `MaNguoiChoiDangHoatDong` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin GENERATED ALWAYS AS (CASE WHEN TrangThaiPhien='DangHoatDong' THEN MaNguoiChoi ELSE NULL END) STORED,
  PRIMARY KEY (`MaPhien`),
  CONSTRAINT `ck_phien_su_dung_0` CHECK (HinhThucDangNhap IN ('TraTruoc','TraSau','MienPhi')),
  CONSTRAINT `ck_phien_su_dung_1` CHECK (TrangThaiPhien IN ('DangHoatDong','DaKetThuc','DaHuy')),
  CONSTRAINT `ck_phien_su_dung_2` CHECK (DonGiaGioApDung>=0 AND TienNapTruoc>=0 AND TienGiuCho>=0 AND TongTienTamTinh>=0),
  CONSTRAINT `ck_phien_su_dung_3` CHECK (ThoiDiemKetThuc IS NULL OR ThoiDiemKetThuc>=ThoiDiemBatDau),
  CONSTRAINT `ck_phien_su_dung_4` CHECK ((TrangThaiPhien='DangHoatDong')=(ThoiDiemKetThuc IS NULL)),
  CONSTRAINT `ck_phien_su_dung_5` CHECK ((MaNguoiChoi IS NULL AND HinhThucDangNhap='TraTruoc') OR TienNapTruoc=0)
) ENGINE=InnoDB;

CREATE TABLE `BIEN_LAI_TIEN_MAY` (
  `MaBienLai` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaPhien` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `ThoiDiemLap` DATETIME NOT NULL,
  `ThoiDiemThanhToan` DATETIME NULL,
  `TongTienGio` DECIMAL(12,0) NOT NULL,
  `HinhThucThanhToan` VARCHAR(20) NOT NULL,
  `TienNhan` DECIMAL(12,0) NOT NULL,
  `TienHoan` DECIMAL(12,0) NOT NULL,
  `TrangThaiBienLai` VARCHAR(20) NOT NULL,
  `MaNhanVienThu` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NULL,
  PRIMARY KEY (`MaBienLai`),
  CONSTRAINT `uq_bien_lai_tien_may_0` UNIQUE (`MaPhien`),
  CONSTRAINT `ck_bien_lai_tien_may_0` CHECK (HinhThucThanhToan IN ('TienMat','ChuyenKhoan','TruVi','MienPhi')),
  CONSTRAINT `ck_bien_lai_tien_may_1` CHECK (TrangThaiBienLai IN ('ChuaThanhToan','DaThanhToan')),
  CONSTRAINT `ck_bien_lai_tien_may_2` CHECK (TongTienGio>=0 AND TienNhan>=0 AND TienHoan>=0)
) ENGINE=InnoDB;
-- END 01_schema/02_workstations.sql

-- BEGIN 01_schema/03_services.sql
-- MySQL 8.4.13; baseline 23 tables. Added to unblock backend integration.

CREATE TABLE `NHOM_DICH_VU` (
  `MaNhomDV` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `TenNhomDV` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`MaNhomDV`),
  CONSTRAINT `uq_nhom_dich_vu_0` UNIQUE (`TenNhomDV`)
) ENGINE=InnoDB;

CREATE TABLE `DON_VI_TINH` (
  `MaDonVi` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `TenDonVi` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`MaDonVi`),
  CONSTRAINT `uq_don_vi_tinh_0` UNIQUE (`TenDonVi`)
) ENGINE=InnoDB;

CREATE TABLE `MAY_IN` (
  `MaMayIn` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `TenMayIn` VARCHAR(50) NOT NULL,
  `ViTriDat` VARCHAR(100) NULL,
  PRIMARY KEY (`MaMayIn`),
  CONSTRAINT `uq_may_in_0` UNIQUE (`TenMayIn`)
) ENGINE=InnoDB;

CREATE TABLE `DICH_VU` (
  `MaDichVu` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `TenDichVu` VARCHAR(100) NOT NULL,
  `GiaBanHienHanh` DECIMAL(10,0) NOT NULL,
  `SoLuongTon` INT NOT NULL,
  `TrangThaiKinhDoanh` VARCHAR(20) NOT NULL,
  `MaNhomDV` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaDonVi` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaMayIn` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NULL,
  PRIMARY KEY (`MaDichVu`),
  CONSTRAINT `ck_dich_vu_0` CHECK (GiaBanHienHanh>=0 AND SoLuongTon>=0),
  CONSTRAINT `ck_dich_vu_1` CHECK (TrangThaiKinhDoanh IN ('DangKinhDoanh','NgungKinhDoanh'))
) ENGINE=InnoDB;

CREATE TABLE `DON_GOI_DICH_VU` (
  `MaDonHang` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `ThoiDiemDat` DATETIME NOT NULL,
  `KenhDat` VARCHAR(15) NOT NULL,
  `MaPhien` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NULL,
  `MaNhanVienXuLy` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NULL,
  `TongTien` DECIMAL(12,0) NOT NULL,
  `TrangThaiPhucVu` VARCHAR(20) NOT NULL,
  `TrangThaiTruocHuy` VARCHAR(20) NULL,
  `ThoiDiemHuy` DATETIME NULL,
  `TrangThaiThanhToan` VARCHAR(20) NOT NULL,
  `HinhThucThanhToan` VARCHAR(20) NULL,
  `ThoiDiemThanhToan` DATETIME NULL,
  `SoTienDaHoan` DECIMAL(12,0) NOT NULL DEFAULT 0,
  `ThoiDiemHoanTien` DATETIME NULL,
  PRIMARY KEY (`MaDonHang`),
  CONSTRAINT `ck_don_goi_dich_vu_0` CHECK (KenhDat IN ('TaiMay','TaiQuay')),
  CONSTRAINT `ck_don_goi_dich_vu_1` CHECK ((KenhDat='TaiMay' AND MaPhien IS NOT NULL) OR (KenhDat='TaiQuay' AND MaPhien IS NULL)),
  CONSTRAINT `ck_don_goi_dich_vu_2` CHECK (TrangThaiPhucVu IN ('MoiDat','DaTiepNhan','DangCheBien','DaGiao','DaHuy')),
  CONSTRAINT `ck_don_goi_dich_vu_3` CHECK (TrangThaiThanhToan IN ('ChuaThanhToan','DaThanhToan','DaHoanTien')),
  CONSTRAINT `ck_don_goi_dich_vu_4` CHECK (TongTien>=0 AND SoTienDaHoan>=0)
) ENGINE=InnoDB;

CREATE TABLE `CHI_TIET_GOI_DICH_VU` (
  `MaDonHang` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaDichVu` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `SoLuong` INT NOT NULL,
  `DonGiaBan` DECIMAL(10,0) NOT NULL,
  `ThanhTien` DECIMAL(12,0) GENERATED ALWAYS AS (SoLuong*DonGiaBan) STORED,
  PRIMARY KEY (`MaDonHang`,`MaDichVu`),
  CONSTRAINT `ck_chi_tiet_goi_dich_vu_0` CHECK (SoLuong>0 AND DonGiaBan>=0)
) ENGINE=InnoDB;
-- END 01_schema/03_services.sql

-- BEGIN 01_schema/04_inventory.sql
-- MySQL 8.4.13; baseline 23 tables. Added to unblock backend integration.

CREATE TABLE `PHIEU_KHO` (
  `MaPhieuKho` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `LoaiPhieu` VARCHAR(20) NOT NULL,
  `TrangThaiPhieu` VARCHAR(20) NOT NULL,
  `ThoiDiemLap` DATETIME NOT NULL,
  `ThoiDiemGhiSo` DATETIME NULL,
  `GhiChuLyDo` VARCHAR(255) NULL,
  `MaNhanVienLap` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaDonHang` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NULL,
  PRIMARY KEY (`MaPhieuKho`),
  CONSTRAINT `uq_phieu_kho_0` UNIQUE (`MaDonHang`),
  CONSTRAINT `ck_phieu_kho_0` CHECK (LoaiPhieu IN ('NhapKho','XuatHuy','KiemKe','TaiPhanLoai')),
  CONSTRAINT `ck_phieu_kho_1` CHECK (TrangThaiPhieu IN ('Nhap','DaGhiSo','DaHuy')),
  CONSTRAINT `ck_phieu_kho_2` CHECK ((TrangThaiPhieu='DaGhiSo')=(ThoiDiemGhiSo IS NOT NULL))
) ENGINE=InnoDB;

CREATE TABLE `CHI_TIET_PHIEU_KHO` (
  `MaPhieuKho` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `STTDong` INT NOT NULL,
  `MaDichVu` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `SoLuong` INT NOT NULL,
  `SoLuongSoSach` INT NULL,
  `SoLuongThucTe` INT NULL,
  `SoLuongChenhLech` INT NOT NULL,
  `DonGiaVon` DECIMAL(10,0) NOT NULL,
  PRIMARY KEY (`MaPhieuKho`,`STTDong`),
  CONSTRAINT `uq_chi_tiet_phieu_kho_0` UNIQUE (`MaPhieuKho`,`MaDichVu`),
  CONSTRAINT `ck_chi_tiet_phieu_kho_0` CHECK (STTDong>0 AND SoLuong>=0 AND DonGiaVon>=0),
  CONSTRAINT `ck_chi_tiet_phieu_kho_1` CHECK (SoLuongSoSach IS NULL OR SoLuongSoSach>=0),
  CONSTRAINT `ck_chi_tiet_phieu_kho_2` CHECK (SoLuongThucTe IS NULL OR SoLuongThucTe>=0)
) ENGINE=InnoDB;
-- END 01_schema/04_inventory.sql

-- BEGIN 01_schema/05_staff_wallet.sql
-- MySQL 8.4.13; baseline 23 tables. Added to unblock backend integration.

CREATE TABLE `CA_TRUC` (
  `MaCa` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `TenCa` VARCHAR(50) NOT NULL,
  `ThoiDiemBatDau` DATETIME NOT NULL,
  `ThoiDiemKetThuc` DATETIME NOT NULL,
  PRIMARY KEY (`MaCa`),
  CONSTRAINT `uq_ca_truc_0` UNIQUE (`TenCa`,`ThoiDiemBatDau`),
  CONSTRAINT `ck_ca_truc_0` CHECK (ThoiDiemKetThuc>ThoiDiemBatDau)
) ENGINE=InnoDB;

CREATE TABLE `PHAN_CONG_TRUC` (
  `MaNhanVien` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaCa` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaKhuVuc` VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `GhiChuNhiemVu` VARCHAR(255) NULL,
  PRIMARY KEY (`MaNhanVien`,`MaCa`,`MaKhuVuc`)
) ENGINE=InnoDB;

CREATE TABLE `GIAO_DICH_VI` (
  `MaGiaoDich` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaYeuCau` VARCHAR(100) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `LoaiGiaoDich` VARCHAR(20) NOT NULL,
  `SoTien` DECIMAL(12,0) NOT NULL,
  `ThoiDiemGD` DATETIME NOT NULL,
  `TrangThaiGD` VARCHAR(20) NOT NULL,
  `PhuongThucGD` VARCHAR(20) NOT NULL,
  `MaNguoiChoi` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `MaNhanVienXuLy` VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin NULL,
  `MaDonHang` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NULL,
  `MaPhien` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NULL,
  `MaGDGoc` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin NULL,
  `MaPhienThuThanhCong` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin GENERATED ALWAYS AS (CASE WHEN LoaiGiaoDich='TruTienMay' AND TrangThaiGD='ThanhCong' THEN MaPhien ELSE NULL END) STORED,
  `MaDonHangThuThanhCong` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin GENERATED ALWAYS AS (CASE WHEN LoaiGiaoDich='TruTienDichVu' AND TrangThaiGD='ThanhCong' THEN MaDonHang ELSE NULL END) STORED,
  `MaGDGocHoanThanhCong` VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin GENERATED ALWAYS AS (CASE WHEN LoaiGiaoDich='HoanTien' AND TrangThaiGD='ThanhCong' THEN MaGDGoc ELSE NULL END) STORED,
  PRIMARY KEY (`MaGiaoDich`),
  CONSTRAINT `uq_giao_dich_vi_0` UNIQUE (`MaYeuCau`),
  CONSTRAINT `ck_giao_dich_vi_0` CHECK (LoaiGiaoDich IN ('NapTien','TruTienMay','TruTienDichVu','HoanTien')),
  CONSTRAINT `ck_giao_dich_vi_1` CHECK (TrangThaiGD IN ('ChoXuLy','ThanhCong','ThatBai')),
  CONSTRAINT `ck_giao_dich_vi_2` CHECK (PhuongThucGD IN ('TienMat','ChuyenKhoan','NoiBo')),
  CONSTRAINT `ck_giao_dich_vi_3` CHECK (SoTien>0)
) ENGINE=InnoDB;
-- END 01_schema/05_staff_wallet.sql

-- BEGIN 02_constraints/01_constraints.sql
-- Baseline foreign keys; install after all tables.
ALTER TABLE `TAI_KHOAN` ADD CONSTRAINT `fk_tai_khoan_0` FOREIGN KEY (`MaNhomND`) REFERENCES `NHOM_NGUOI_DUNG` (`MaNhomND`) ON DELETE RESTRICT;
ALTER TABLE `SO_DIEN_THOAI` ADD CONSTRAINT `fk_so_dien_thoai_0` FOREIGN KEY (`MaTaiKhoan`) REFERENCES `TAI_KHOAN` (`MaTaiKhoan`) ON DELETE CASCADE;
ALTER TABLE `NGUOI_CHOI` ADD CONSTRAINT `fk_nguoi_choi_0` FOREIGN KEY (`MaTaiKhoan`) REFERENCES `TAI_KHOAN` (`MaTaiKhoan`) ON DELETE CASCADE;
ALTER TABLE `NHAN_VIEN` ADD CONSTRAINT `fk_nhan_vien_0` FOREIGN KEY (`MaTaiKhoan`) REFERENCES `TAI_KHOAN` (`MaTaiKhoan`) ON DELETE CASCADE;
ALTER TABLE `NHAN_VIEN` ADD CONSTRAINT `fk_nhan_vien_1` FOREIGN KEY (`MaNguoiQuanLy`) REFERENCES `NHAN_VIEN` (`MaTaiKhoan`) ON DELETE SET NULL;
ALTER TABLE `DIA_CHI_NV` ADD CONSTRAINT `fk_dia_chi_nv_0` FOREIGN KEY (`MaTaiKhoan`) REFERENCES `NHAN_VIEN` (`MaTaiKhoan`) ON DELETE CASCADE;
ALTER TABLE `BANG_GIA` ADD CONSTRAINT `fk_bang_gia_0` FOREIGN KEY (`MaNhomND`) REFERENCES `NHOM_NGUOI_DUNG` (`MaNhomND`) ON DELETE CASCADE;
ALTER TABLE `BANG_GIA` ADD CONSTRAINT `fk_bang_gia_1` FOREIGN KEY (`MaNhomMay`) REFERENCES `NHOM_MAY` (`MaNhomMay`) ON DELETE CASCADE;
ALTER TABLE `MAY_TRAM` ADD CONSTRAINT `fk_may_tram_0` FOREIGN KEY (`MaNhomMay`) REFERENCES `NHOM_MAY` (`MaNhomMay`) ON DELETE RESTRICT;
ALTER TABLE `MAY_TRAM` ADD CONSTRAINT `fk_may_tram_1` FOREIGN KEY (`MaKhuVuc`) REFERENCES `KHU_VUC` (`MaKhuVuc`) ON DELETE RESTRICT;
ALTER TABLE `PHIEN_SU_DUNG` ADD CONSTRAINT `fk_phien_su_dung_0` FOREIGN KEY (`MaMay`) REFERENCES `MAY_TRAM` (`MaMay`) ON DELETE RESTRICT;
ALTER TABLE `PHIEN_SU_DUNG` ADD CONSTRAINT `fk_phien_su_dung_1` FOREIGN KEY (`MaNguoiChoi`) REFERENCES `NGUOI_CHOI` (`MaTaiKhoan`) ON DELETE RESTRICT;
ALTER TABLE `BIEN_LAI_TIEN_MAY` ADD CONSTRAINT `fk_bien_lai_tien_may_0` FOREIGN KEY (`MaPhien`) REFERENCES `PHIEN_SU_DUNG` (`MaPhien`) ON DELETE RESTRICT;
ALTER TABLE `BIEN_LAI_TIEN_MAY` ADD CONSTRAINT `fk_bien_lai_tien_may_1` FOREIGN KEY (`MaNhanVienThu`) REFERENCES `NHAN_VIEN` (`MaTaiKhoan`) ON DELETE RESTRICT;
ALTER TABLE `PHAN_CONG_TRUC` ADD CONSTRAINT `fk_phan_cong_truc_0` FOREIGN KEY (`MaNhanVien`) REFERENCES `NHAN_VIEN` (`MaTaiKhoan`) ON DELETE RESTRICT;
ALTER TABLE `PHAN_CONG_TRUC` ADD CONSTRAINT `fk_phan_cong_truc_1` FOREIGN KEY (`MaCa`) REFERENCES `CA_TRUC` (`MaCa`) ON DELETE RESTRICT;
ALTER TABLE `PHAN_CONG_TRUC` ADD CONSTRAINT `fk_phan_cong_truc_2` FOREIGN KEY (`MaKhuVuc`) REFERENCES `KHU_VUC` (`MaKhuVuc`) ON DELETE RESTRICT;
ALTER TABLE `DICH_VU` ADD CONSTRAINT `fk_dich_vu_0` FOREIGN KEY (`MaNhomDV`) REFERENCES `NHOM_DICH_VU` (`MaNhomDV`) ON DELETE RESTRICT;
ALTER TABLE `DICH_VU` ADD CONSTRAINT `fk_dich_vu_1` FOREIGN KEY (`MaDonVi`) REFERENCES `DON_VI_TINH` (`MaDonVi`) ON DELETE RESTRICT;
ALTER TABLE `DICH_VU` ADD CONSTRAINT `fk_dich_vu_2` FOREIGN KEY (`MaMayIn`) REFERENCES `MAY_IN` (`MaMayIn`) ON DELETE SET NULL;
ALTER TABLE `DON_GOI_DICH_VU` ADD CONSTRAINT `fk_don_goi_dich_vu_0` FOREIGN KEY (`MaPhien`) REFERENCES `PHIEN_SU_DUNG` (`MaPhien`) ON DELETE RESTRICT;
ALTER TABLE `DON_GOI_DICH_VU` ADD CONSTRAINT `fk_don_goi_dich_vu_1` FOREIGN KEY (`MaNhanVienXuLy`) REFERENCES `NHAN_VIEN` (`MaTaiKhoan`) ON DELETE RESTRICT;
ALTER TABLE `CHI_TIET_GOI_DICH_VU` ADD CONSTRAINT `fk_chi_tiet_goi_dich_vu_0` FOREIGN KEY (`MaDonHang`) REFERENCES `DON_GOI_DICH_VU` (`MaDonHang`) ON DELETE CASCADE;
ALTER TABLE `CHI_TIET_GOI_DICH_VU` ADD CONSTRAINT `fk_chi_tiet_goi_dich_vu_1` FOREIGN KEY (`MaDichVu`) REFERENCES `DICH_VU` (`MaDichVu`) ON DELETE RESTRICT;
ALTER TABLE `PHIEU_KHO` ADD CONSTRAINT `fk_phieu_kho_0` FOREIGN KEY (`MaNhanVienLap`) REFERENCES `NHAN_VIEN` (`MaTaiKhoan`) ON DELETE RESTRICT;
ALTER TABLE `PHIEU_KHO` ADD CONSTRAINT `fk_phieu_kho_1` FOREIGN KEY (`MaDonHang`) REFERENCES `DON_GOI_DICH_VU` (`MaDonHang`) ON DELETE RESTRICT;
ALTER TABLE `CHI_TIET_PHIEU_KHO` ADD CONSTRAINT `fk_chi_tiet_phieu_kho_0` FOREIGN KEY (`MaPhieuKho`) REFERENCES `PHIEU_KHO` (`MaPhieuKho`) ON DELETE CASCADE;
ALTER TABLE `CHI_TIET_PHIEU_KHO` ADD CONSTRAINT `fk_chi_tiet_phieu_kho_1` FOREIGN KEY (`MaDichVu`) REFERENCES `DICH_VU` (`MaDichVu`) ON DELETE RESTRICT;
ALTER TABLE `GIAO_DICH_VI` ADD CONSTRAINT `fk_giao_dich_vi_0` FOREIGN KEY (`MaNguoiChoi`) REFERENCES `NGUOI_CHOI` (`MaTaiKhoan`) ON DELETE RESTRICT;
ALTER TABLE `GIAO_DICH_VI` ADD CONSTRAINT `fk_giao_dich_vi_1` FOREIGN KEY (`MaNhanVienXuLy`) REFERENCES `NHAN_VIEN` (`MaTaiKhoan`) ON DELETE RESTRICT;
ALTER TABLE `GIAO_DICH_VI` ADD CONSTRAINT `fk_giao_dich_vi_2` FOREIGN KEY (`MaDonHang`) REFERENCES `DON_GOI_DICH_VU` (`MaDonHang`) ON DELETE RESTRICT;
ALTER TABLE `GIAO_DICH_VI` ADD CONSTRAINT `fk_giao_dich_vi_3` FOREIGN KEY (`MaPhien`) REFERENCES `PHIEN_SU_DUNG` (`MaPhien`) ON DELETE RESTRICT;
ALTER TABLE `GIAO_DICH_VI` ADD CONSTRAINT `fk_giao_dich_vi_4` FOREIGN KEY (`MaGDGoc`) REFERENCES `GIAO_DICH_VI` (`MaGiaoDich`) ON DELETE RESTRICT;
-- END 02_constraints/01_constraints.sql

-- BEGIN 03_indexes/01_indexes.sql
CREATE UNIQUE INDEX uq_phien_may_active ON PHIEN_SU_DUNG(MaMayDangHoatDong);
CREATE UNIQUE INDEX uq_phien_nguoi_active ON PHIEN_SU_DUNG(MaNguoiChoiDangHoatDong);
CREATE UNIQUE INDEX uq_vi_thu_phien ON GIAO_DICH_VI(MaPhienThuThanhCong);
CREATE UNIQUE INDEX uq_vi_thu_don ON GIAO_DICH_VI(MaDonHangThuThanhCong);
CREATE UNIQUE INDEX uq_vi_hoan_goc ON GIAO_DICH_VI(MaGDGocHoanThanhCong);
CREATE INDEX ix_don_thoi_diem ON DON_GOI_DICH_VU(ThoiDiemDat);
CREATE INDEX ix_bien_lai_thanh_toan ON BIEN_LAI_TIEN_MAY(ThoiDiemThanhToan);
CREATE INDEX ix_vi_nguoi_thoi_diem ON GIAO_DICH_VI(MaNguoiChoi,ThoiDiemGD);
CREATE INDEX ix_ca_khoang ON CA_TRUC(ThoiDiemBatDau,ThoiDiemKetThuc);
CREATE INDEX ix_dich_vu_filter ON DICH_VU(MaNhomDV, TrangThaiKinhDoanh, GiaBanHienHanh, MaDichVu);
-- END 03_indexes/01_indexes.sql

-- BEGIN 07_functions/01_billing.sql
-- MySQL 8.4.13. No routine commits; caller owns the transaction.
DELIMITER $$
CREATE FUNCTION fn_tien_gio(pBatDau DATETIME,pKetThuc DATETIME,pDonGiaGio DECIMAL(10,0)) RETURNS DECIMAL(12,0)
DETERMINISTIC NO SQL
BEGIN
  DECLARE result DECIMAL(30,0);
  IF pBatDau IS NULL OR pKetThuc IS NULL OR pKetThuc<pBatDau OR pDonGiaGio<0 THEN
    SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT';
  END IF;
  SET result=(TIMESTAMPDIFF(SECOND,pBatDau,pKetThuc)*pDonGiaGio) DIV 3600;
  IF result>999999999999 THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT'; END IF;
  RETURN result;
END$$
CREATE FUNCTION fn_so_du_kha_dung(pMaNguoiChoi VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin) RETURNS DECIMAL(12,0)
READS SQL DATA
BEGIN
  RETURN (SELECT SoDuVi-COALESCE((SELECT SUM(TienGiuCho) FROM PHIEN_SU_DUNG WHERE MaNguoiChoi=pMaNguoiChoi AND TrangThaiPhien='DangHoatDong' AND HinhThucDangNhap='TraTruoc'),0) FROM NGUOI_CHOI WHERE MaTaiKhoan=pMaNguoiChoi);
END$$
-- Internal helpers; not additional application business actions.
CREATE FUNCTION fn_co_quyen(pActor VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,pRoles VARCHAR(100) CHARACTER SET ascii COLLATE ascii_bin) RETURNS BOOLEAN
READS SQL DATA
RETURN EXISTS(SELECT 1 FROM TAI_KHOAN tk JOIN NHAN_VIEN nv ON nv.MaTaiKhoan=tk.MaTaiKhoan WHERE tk.MaTaiKhoan=pActor AND tk.TrangThai='HoatDong' AND FIND_IN_SET(nv.ChucVu,pRoles)>0)$$
CREATE FUNCTION fn_han_phien(pStart DATETIME,pBudget DECIMAL(12,0),pRate DECIMAL(10,0)) RETURNS DATETIME
DETERMINISTIC NO SQL
RETURN IF(pRate>0,TIMESTAMPADD(SECOND,LEAST(((3600*(pBudget+1)-1) DIV pRate),TIMESTAMPDIFF(SECOND,pStart,'9999-12-31 23:59:59')),pStart),NULL)$$
DELIMITER ;
-- END 07_functions/01_billing.sql

-- BEGIN 07_functions/02_functions_p12.sql
-- BTL2 Quản lý quán Net – L09, Nhóm 10
-- Hai hàm có điều kiện, vòng lặp và đọc bảng (HT & TD phụ trách)
-- Đáp ứng yêu cầu mục 2.4 của Mẫu Báo Cáo P1-2

DELIMITER $$

DROP FUNCTION IF EXISTS `fn_tong_chi_vi_rong`$$
CREATE FUNCTION `fn_tong_chi_vi_rong`(
    pMaNguoiChoi VARCHAR(15),
    pBatDau DATETIME,
    pKetThuc DATETIME
) RETURNS DECIMAL(18,0)
READS SQL DATA
BEGIN
    DECLARE vDone INT DEFAULT 0;
    DECLARE vLoaiGD VARCHAR(20);
    DECLARE vSoTien DECIMAL(12,0);
    DECLARE vTongChi DECIMAL(18,0) DEFAULT 0;

    -- Khai báo CURSOR đọc giao dịch ví thành công trong khoảng thời gian [pBatDau, pKetThuc)
    DECLARE cur_gd CURSOR FOR
        SELECT `LoaiGiaoDich`, `SoTien`
        FROM `GIAO_DICH_VI`
        WHERE `MaNguoiChoi` = pMaNguoiChoi
          AND `TrangThaiGD` = 'ThanhCong'
          AND `ThoiDiemGD` >= pBatDau
          AND `ThoiDiemGD` < pKetThuc;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET vDone = 1;

    -- 1. Phân biệt đối tượng không tồn tại (trả về NULL)
    IF NOT EXISTS (SELECT 1 FROM `NGUOI_CHOI` WHERE `MaTaiKhoan` = pMaNguoiChoi) THEN
        RETURN NULL;
    END IF;

    -- 2. Kiểm tra khoảng thời gian hợp lệ
    IF pBatDau IS NULL OR pKetThuc IS NULL OR pBatDau >= pKetThuc THEN
        RETURN NULL;
    END IF;

    -- 3. Mở CURSOR và duyệt qua các giao dịch
    OPEN cur_gd;

    read_loop: LOOP
        FETCH cur_gd INTO vLoaiGD, vSoTien;
        IF vDone = 1 THEN
            LEAVE read_loop;
        END IF;

        -- Điều kiện xử lý loại giao dịch:
        -- Cộng phí dịch vụ và tiền máy qua ví, trừ các khoản hoàn tiền, bỏ qua nạp tiền
        IF vLoaiGD IN ('TruTienMay', 'TruTienDichVu') THEN
            SET vTongChi = vTongChi + vSoTien;
        ELSEIF vLoaiGD = 'HoanTien' THEN
            SET vTongChi = vTongChi - vSoTien;
        END IF;
    END LOOP;

    CLOSE cur_gd;

    RETURN vTongChi;
END$$

DROP FUNCTION IF EXISTS `fn_tong_tien_don`$$
CREATE FUNCTION `fn_tong_tien_don`(
    pMaDonHang VARCHAR(20)
) RETURNS DECIMAL(18,0)
READS SQL DATA
BEGIN
    DECLARE vDone INT DEFAULT 0;
    DECLARE vSoLuong INT;
    DECLARE vDonGiaBan DECIMAL(12,0);
    DECLARE vTongTien DECIMAL(18,0) DEFAULT 0;

    -- Khai báo CURSOR duyệt các dòng chi tiết của đơn hàng
    DECLARE cur_ct CURSOR FOR
        SELECT `SoLuong`, `DonGiaBan`
        FROM `CHI_TIET_GOI_DICH_VU`
        WHERE `MaDonHang` = pMaDonHang;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET vDone = 1;

    -- 1. Kiểm tra tồn tại đơn hàng (trả NULL nếu không tồn tại)
    IF NOT EXISTS (SELECT 1 FROM `DON_GOI_DICH_VU` WHERE `MaDonHang` = pMaDonHang) THEN
        RETURN NULL;
    END IF;

    -- 2. Mở CURSOR và cộng dồn qua từng dòng
    OPEN cur_ct;

    read_loop: LOOP
        FETCH cur_ct INTO vSoLuong, vDonGiaBan;
        IF vDone = 1 THEN
            LEAVE read_loop;
        END IF;

        IF vSoLuong > 0 AND vDonGiaBan >= 0 THEN
            SET vTongTien = vTongTien + (vSoLuong * vDonGiaBan);
        END IF;
    END LOOP;

    CLOSE cur_ct;

    RETURN vTongTien;
END$$

DELIMITER ;
-- END 07_functions/02_functions_p12.sql

-- BEGIN 06_procedures/01_sessions.sql
-- Six main procedure contracts; helper locks below produce no result sets.
DELIMITER $$
CREATE PROCEDURE sp_khoa_dong(IN pBang VARCHAR(30) CHARACTER SET ascii COLLATE ascii_bin,IN pMa VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin)
SQL SECURITY DEFINER
BEGIN
  CASE pBang
    WHEN 'NGUOI_CHOI' THEN SELECT * FROM NGUOI_CHOI WHERE MaTaiKhoan=pMa FOR UPDATE;
    WHEN 'MAY_TRAM' THEN SELECT * FROM MAY_TRAM WHERE MaMay=pMa FOR UPDATE;
    WHEN 'PHIEN_SU_DUNG' THEN SELECT * FROM PHIEN_SU_DUNG WHERE MaPhien=pMa FOR UPDATE;
    WHEN 'DON_GOI_DICH_VU' THEN SELECT * FROM DON_GOI_DICH_VU WHERE MaDonHang=pMa FOR UPDATE;
    WHEN 'PHIEU_KHO' THEN SELECT * FROM PHIEU_KHO WHERE MaPhieuKho=pMa FOR UPDATE;
    WHEN 'DICH_VU' THEN SELECT * FROM DICH_VU WHERE MaDichVu=pMa FOR UPDATE;
    ELSE SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT';
  END CASE;
END$$
CREATE PROCEDURE sp_khoa_phien(IN pId VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin)
SQL SECURITY DEFINER
BEGIN
  DECLARE ownerId VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin; DECLARE machineId VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin; DECLARE dummy VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin;
  IF NOT EXISTS(SELECT 1 FROM PHIEN_SU_DUNG WHERE MaPhien=pId) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60002,MESSAGE_TEXT='NOT_FOUND'; END IF;
  SELECT MaNguoiChoi,MaMay INTO ownerId,machineId FROM PHIEN_SU_DUNG WHERE MaPhien=pId;
  IF ownerId IS NOT NULL THEN SELECT MaTaiKhoan INTO dummy FROM NGUOI_CHOI WHERE MaTaiKhoan=ownerId FOR UPDATE; END IF;
  SELECT MaMay INTO dummy FROM MAY_TRAM WHERE MaMay=machineId FOR UPDATE;
  SELECT MaPhien INTO dummy FROM PHIEN_SU_DUNG WHERE MaPhien=pId FOR UPDATE;
END$$
CREATE PROCEDURE sp_mo_phien(IN pMaPhien VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaMay VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin,IN pMaNguoiChoi VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pHinhThucDangNhap VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pTienNapTruoc DECIMAL(12,0),IN pMaTacNhan VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pThoiDiem DATETIME)
SQL SECURITY DEFINER
proc: BEGIN
  DECLARE balance DECIMAL(12,0) DEFAULT 0; DECLARE price DECIMAL(10,0); DECLARE groupId VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin; DECLARE machineGroup VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin; DECLARE state VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE existingId VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin;
  IF NOT EXISTS(SELECT 1 FROM TAI_KHOAN WHERE MaTaiKhoan=pMaTacNhan AND TrangThai='HoatDong') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60013,MESSAGE_TEXT='ACCOUNT_INACTIVE'; END IF;
  IF NOT fn_co_quyen(pMaTacNhan,'ThuNgan,QuanLy') AND NOT (pMaTacNhan=pMaNguoiChoi AND pHinhThucDangNhap='TraTruoc' AND EXISTS(SELECT 1 FROM NGUOI_CHOI WHERE MaTaiKhoan=pMaTacNhan)) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  IF pHinhThucDangNhap='MienPhi' AND NOT fn_co_quyen(pMaTacNhan,'QuanLy') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  IF pHinhThucDangNhap NOT IN ('TraTruoc','TraSau','MienPhi') OR pTienNapTruoc<0 OR ((pMaNguoiChoi IS NOT NULL OR pHinhThucDangNhap<>'TraTruoc') AND pTienNapTruoc<>0) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT'; END IF;
  IF pMaNguoiChoi IS NOT NULL THEN
    IF NOT EXISTS(SELECT 1 FROM NGUOI_CHOI WHERE MaTaiKhoan=pMaNguoiChoi) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60002,MESSAGE_TEXT='NOT_FOUND'; END IF;
    SELECT SoDuVi INTO balance FROM NGUOI_CHOI WHERE MaTaiKhoan=pMaNguoiChoi FOR UPDATE;
    SELECT MaNhomND INTO groupId FROM TAI_KHOAN WHERE MaTaiKhoan=pMaNguoiChoi AND TrangThai='HoatDong';
    IF groupId IS NULL THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60013,MESSAGE_TEXT='ACCOUNT_INACTIVE'; END IF;
  ELSE SET groupId='VangLai'; END IF;
  IF NOT EXISTS(SELECT 1 FROM MAY_TRAM WHERE MaMay=pMaMay) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60002,MESSAGE_TEXT='NOT_FOUND'; END IF;
  SELECT TrangThaiMay,MaNhomMay INTO state,machineGroup FROM MAY_TRAM WHERE MaMay=pMaMay FOR UPDATE;
  IF EXISTS(SELECT 1 FROM PHIEN_SU_DUNG WHERE MaPhien=pMaPhien) THEN
    IF NOT EXISTS(SELECT 1 FROM PHIEN_SU_DUNG WHERE MaPhien=pMaPhien AND MaMay=pMaMay AND MaNguoiChoi<=>pMaNguoiChoi AND HinhThucDangNhap=pHinhThucDangNhap AND TienNapTruoc=pTienNapTruoc) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60009,MESSAGE_TEXT='IDEMPOTENCY_CONFLICT'; END IF;
    SELECT pMaPhien AS MaDoiTuong,1 AS DaThucHienTruoc; LEAVE proc;
  END IF;
  IF EXISTS(SELECT 1 FROM PHIEN_SU_DUNG WHERE TrangThaiPhien='DangHoatDong' AND (MaMay=pMaMay OR MaNguoiChoi=pMaNguoiChoi)) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60005,MESSAGE_TEXT='ACTIVE_SESSION_EXISTS'; END IF;
  IF state<>'AVAILABLE' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60004,MESSAGE_TEXT='MACHINE_UNAVAILABLE'; END IF;
  SELECT COALESCE((SELECT DonGiaGio FROM BANG_GIA WHERE MaNhomND=groupId AND MaNhomMay=machineGroup),DonGiaGioMacDinh) INTO price FROM NHOM_MAY WHERE MaNhomMay=machineGroup;
  IF pHinhThucDangNhap='MienPhi' THEN SET price=0; END IF;
  IF pHinhThucDangNhap='TraTruoc' AND price>0 AND IF(pMaNguoiChoi IS NULL,pTienNapTruoc,balance)<=0 THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60006,MESSAGE_TEXT='INSUFFICIENT_FUNDS'; END IF;
  INSERT INTO PHIEN_SU_DUNG(MaPhien,HinhThucDangNhap,ThoiDiemBatDau,DonGiaGioApDung,TienNapTruoc,TienGiuCho,TongTienTamTinh,TrangThaiPhien,MaMay,MaNguoiChoi) VALUES(pMaPhien,pHinhThucDangNhap,pThoiDiem,price,pTienNapTruoc,0,0,'DangHoatDong',pMaMay,pMaNguoiChoi);
  UPDATE MAY_TRAM SET TrangThaiMay='ONLINE' WHERE MaMay=pMaMay;
  SELECT pMaPhien AS MaDoiTuong,0 AS DaThucHienTruoc;
END$$
CREATE PROCEDURE sp_ket_thuc_phien(IN pMaPhien VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaBienLai VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaGiaoDich VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pHinhThucThanhToan VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pTienNhan DECIMAL(12,0),IN pMaTacNhan VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pThoiDiem DATETIME)
SQL SECURITY DEFINER
proc: BEGIN
  DECLARE ownerId VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin; DECLARE machineId VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin; DECLARE state VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE kind VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE started DATETIME; DECLARE expiry DATETIME; DECLARE price DECIMAL(10,0); DECLARE budget DECIMAL(12,0); DECLARE fee DECIMAL(12,0); DECLARE balance DECIMAL(12,0) DEFAULT 0; DECLARE received DECIMAL(12,0); DECLARE returned DECIMAL(12,0) DEFAULT 0; DECLARE collector VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin; DECLARE method VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE paid VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin DEFAULT 'DaThanhToan';
  CALL sp_khoa_phien(pMaPhien);
  SELECT MaNguoiChoi,MaMay,TrangThaiPhien,HinhThucDangNhap,ThoiDiemBatDau,DonGiaGioApDung,TienNapTruoc INTO ownerId,machineId,state,kind,started,price,budget FROM PHIEN_SU_DUNG WHERE MaPhien=pMaPhien;
  IF ownerId IS NOT NULL THEN SELECT SoDuVi INTO balance FROM NGUOI_CHOI WHERE MaTaiKhoan=ownerId; END IF;
  IF pMaTacNhan IS NOT NULL AND NOT fn_co_quyen(pMaTacNhan,'ThuNgan,QuanLy') AND NOT (pMaTacNhan=ownerId AND pHinhThucThanhToan='TruVi' AND EXISTS(SELECT 1 FROM TAI_KHOAN WHERE MaTaiKhoan=pMaTacNhan AND TrangThai='HoatDong')) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  SET method=IF(pHinhThucThanhToan='ChuaThu','TienMat',pHinhThucThanhToan);
  SET received=pTienNhan;
  IF state='DaKetThuc' THEN
    IF NOT EXISTS(SELECT 1 FROM BIEN_LAI_TIEN_MAY WHERE MaPhien=pMaPhien AND HinhThucThanhToan=method AND TienNhan=pTienNhan AND (TrangThaiBienLai='ChuaThanhToan')=(pHinhThucThanhToan='ChuaThu')) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60009,MESSAGE_TEXT='IDEMPOTENCY_CONFLICT'; END IF;
    SELECT pMaPhien AS MaDoiTuong,1 AS DaThucHienTruoc; LEAVE proc;
  END IF;
  IF state<>'DangHoatDong' OR pThoiDiem<started THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  SET expiry=IF(kind='TraTruoc',fn_han_phien(started,IF(ownerId IS NULL,budget,balance),price),NULL);
  IF pMaTacNhan IS NULL AND (expiry IS NULL OR pThoiDiem<>expiry OR NOW()<expiry) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  IF expiry IS NOT NULL AND pThoiDiem>expiry THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60014,MESSAGE_TEXT='PREPAID_EXPIRED'; END IF;
  SET fee=fn_tien_gio(started,pThoiDiem,price);
  IF kind='MienPhi' THEN
    IF method<>'MienPhi' OR received<>0 THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  ELSEIF ownerId IS NULL AND kind='TraTruoc' THEN
    IF method<>'TienMat' OR received<>budget OR fee>budget THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
    SET returned=budget-fee;
  ELSEIF pHinhThucThanhToan='ChuaThu' THEN
    IF kind<>'TraSau' OR received<>0 THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
    SET paid='ChuaThanhToan';
  ELSEIF method='TruVi' THEN
    IF ownerId IS NULL OR received<>0 THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60012,MESSAGE_TEXT='INVALID_WALLET_OWNER'; END IF;
    IF balance<fee THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60006,MESSAGE_TEXT='INSUFFICIENT_FUNDS'; END IF;
    UPDATE NGUOI_CHOI SET SoDuVi=SoDuVi-fee WHERE MaTaiKhoan=ownerId;
    IF fee>0 THEN INSERT INTO GIAO_DICH_VI(MaGiaoDich,MaYeuCau,LoaiGiaoDich,SoTien,ThoiDiemGD,TrangThaiGD,PhuongThucGD,MaNguoiChoi,MaPhien) VALUES(pMaGiaoDich,CONCAT('gio:',pMaPhien),'TruTienMay',fee,pThoiDiem,'ThanhCong','NoiBo',ownerId,pMaPhien); END IF;
  ELSEIF method IN ('TienMat','ChuyenKhoan') THEN
    IF NOT fn_co_quyen(pMaTacNhan,'ThuNgan,QuanLy') OR received<fee THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
    SET returned=received-fee;
  ELSE SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  SET collector=IF(fn_co_quyen(pMaTacNhan,'ThuNgan,QuanLy'),pMaTacNhan,NULL);
  INSERT INTO BIEN_LAI_TIEN_MAY(MaBienLai,MaPhien,ThoiDiemLap,ThoiDiemThanhToan,TongTienGio,HinhThucThanhToan,TienNhan,TienHoan,TrangThaiBienLai,MaNhanVienThu) VALUES(pMaBienLai,pMaPhien,pThoiDiem,IF(paid='DaThanhToan',pThoiDiem,NULL),fee,method,received,returned,paid,collector);
  UPDATE PHIEN_SU_DUNG SET TrangThaiPhien='DaKetThuc',ThoiDiemKetThuc=pThoiDiem,TongTienTamTinh=fee,TienGiuCho=0 WHERE MaPhien=pMaPhien;
  UPDATE MAY_TRAM SET TrangThaiMay='AVAILABLE' WHERE MaMay=machineId;
  SELECT pMaPhien AS MaDoiTuong,0 AS DaThucHienTruoc;
END$$
DELIMITER ;
-- END 06_procedures/01_sessions.sql

-- BEGIN 06_procedures/02_wallet_orders.sql
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_nap_vi$$
CREATE PROCEDURE sp_nap_vi(IN pMaGiaoDich VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaYeuCau VARCHAR(100) CHARACTER SET ascii COLLATE ascii_bin,IN pMaNguoiChoi VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pSoTien DECIMAL(12,0),IN pPhuongThucGD VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaTacNhan VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pThoiDiem DATETIME)
SQL SECURITY DEFINER
proc: BEGIN
  DECLARE balance DECIMAL(12,0);
  IF NOT fn_co_quyen(pMaTacNhan,'ThuNgan,QuanLy') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  IF pSoTien<=0 OR pPhuongThucGD NOT IN ('TienMat','ChuyenKhoan') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT'; END IF;
  IF NOT EXISTS(SELECT 1 FROM NGUOI_CHOI WHERE MaTaiKhoan=pMaNguoiChoi) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60002,MESSAGE_TEXT='NOT_FOUND'; END IF;
  SELECT SoDuVi INTO balance FROM NGUOI_CHOI WHERE MaTaiKhoan=pMaNguoiChoi FOR UPDATE;
  IF EXISTS(SELECT 1 FROM GIAO_DICH_VI WHERE MaYeuCau=pMaYeuCau) THEN
    IF NOT EXISTS(SELECT 1 FROM GIAO_DICH_VI WHERE MaYeuCau=pMaYeuCau AND MaGiaoDich=pMaGiaoDich AND MaNguoiChoi=pMaNguoiChoi AND SoTien=pSoTien AND PhuongThucGD=pPhuongThucGD AND MaNhanVienXuLy=pMaTacNhan AND LoaiGiaoDich='NapTien' AND TrangThaiGD='ThanhCong') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60009,MESSAGE_TEXT='IDEMPOTENCY_CONFLICT'; END IF;
    SELECT pMaGiaoDich AS MaDoiTuong,1 AS DaThucHienTruoc; LEAVE proc;
  END IF;
  IF balance+pSoTien>999999999999 THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT'; END IF;
  INSERT INTO GIAO_DICH_VI(MaGiaoDich,MaYeuCau,LoaiGiaoDich,SoTien,ThoiDiemGD,TrangThaiGD,PhuongThucGD,MaNguoiChoi,MaNhanVienXuLy) VALUES(pMaGiaoDich,pMaYeuCau,'NapTien',pSoTien,pThoiDiem,'ThanhCong',pPhuongThucGD,pMaNguoiChoi,pMaTacNhan);
  UPDATE NGUOI_CHOI SET SoDuVi=SoDuVi+pSoTien WHERE MaTaiKhoan=pMaNguoiChoi;
  SELECT pMaGiaoDich AS MaDoiTuong,0 AS DaThucHienTruoc;
END$$
DROP PROCEDURE IF EXISTS sp_tiep_nhan_don$$
CREATE PROCEDURE sp_tiep_nhan_don(IN pMaDonHang VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaTacNhan VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pThoiDiem DATETIME)
SQL SECURITY DEFINER
proc: BEGIN
  DECLARE sessionId VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE state VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE ownerId VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin; DECLARE kind VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE started DATETIME; DECLARE price DECIMAL(10,0); DECLARE budget DECIMAL(12,0); DECLARE total DECIMAL(12,0); DECLARE amount DECIMAL(30,0) DEFAULT 0; DECLARE done BOOLEAN DEFAULT FALSE; DECLARE serviceId VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin; DECLARE qty INT; DECLARE stock INT; DECLARE capturedPrice DECIMAL(10,0); DECLARE countLines INT DEFAULT 0;
  DECLARE items CURSOR FOR SELECT dv.MaDichVu,ct.SoLuong,dv.SoLuongTon,ct.DonGiaBan FROM CHI_TIET_GOI_DICH_VU ct JOIN DICH_VU dv ON dv.MaDichVu=ct.MaDichVu WHERE ct.MaDonHang=pMaDonHang ORDER BY dv.MaDichVu FOR UPDATE;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done=TRUE;
  IF NOT fn_co_quyen(pMaTacNhan,'ThuNgan,PhaChe,QuanLy') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  IF NOT EXISTS(SELECT 1 FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60002,MESSAGE_TEXT='NOT_FOUND'; END IF;
  SELECT MaPhien INTO sessionId FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang;
  IF sessionId IS NOT NULL THEN CALL sp_khoa_phien(sessionId); END IF;
  SELECT TrangThaiPhucVu,TongTien INTO state,total FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang FOR UPDATE;
  IF state IN ('DaTiepNhan','DangCheBien','DaGiao') THEN SELECT pMaDonHang AS MaDoiTuong,1 AS DaThucHienTruoc; LEAVE proc; END IF;
  IF state<>'MoiDat' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  IF sessionId IS NOT NULL THEN
    SELECT TrangThaiPhien,MaNguoiChoi,HinhThucDangNhap,ThoiDiemBatDau,DonGiaGioApDung,TienNapTruoc INTO state,ownerId,kind,started,price,budget FROM PHIEN_SU_DUNG WHERE MaPhien=sessionId;
    IF state<>'DangHoatDong' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
    IF ownerId IS NOT NULL THEN SELECT SoDuVi INTO budget FROM NGUOI_CHOI WHERE MaTaiKhoan=ownerId; END IF;
    IF kind='TraTruoc' AND price>0 AND pThoiDiem>=fn_han_phien(started,budget,price) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60014,MESSAGE_TEXT='PREPAID_EXPIRED'; END IF;
  END IF;
  OPEN items;
  item_loop: LOOP
    FETCH items INTO serviceId,qty,stock,capturedPrice;
    IF done THEN LEAVE item_loop; END IF;
    IF stock<qty THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60007,MESSAGE_TEXT='INSUFFICIENT_STOCK'; END IF;
    SET amount=amount+qty*capturedPrice; SET countLines=countLines+1;
    UPDATE DICH_VU SET SoLuongTon=SoLuongTon-qty WHERE MaDichVu=serviceId;
  END LOOP;
  CLOSE items;
  IF countLines=0 OR amount<>total THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  UPDATE DON_GOI_DICH_VU SET TrangThaiPhucVu='DaTiepNhan',MaNhanVienXuLy=pMaTacNhan WHERE MaDonHang=pMaDonHang;
  SELECT pMaDonHang AS MaDoiTuong,0 AS DaThucHienTruoc;
END$$
DROP PROCEDURE IF EXISTS sp_thanh_toan_don$$
CREATE PROCEDURE sp_thanh_toan_don(IN pMaDonHang VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaGiaoDich VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pHinhThucThanhToan VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaTacNhan VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pThoiDiem DATETIME)
SQL SECURITY DEFINER
proc: BEGIN
  DECLARE sessionId VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE ownerId VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin; DECLARE state VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE serviceState VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE sessionState VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE oldMethod VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE kind VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE started DATETIME; DECLARE rate DECIMAL(10,0); DECLARE total DECIMAL(12,0); DECLARE balance DECIMAL(12,0); DECLARE holding DECIMAL(12,0) DEFAULT 0;
  DECLARE activeSessionId VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE activeKind VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE activeStarted DATETIME; DECLARE activeRate DECIMAL(10,0);
  IF pHinhThucThanhToan NOT IN ('TienMat','ChuyenKhoan','TruVi') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT'; END IF;
  IF NOT EXISTS(SELECT 1 FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60002,MESSAGE_TEXT='NOT_FOUND'; END IF;
  SELECT MaPhien INTO sessionId FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang;
  IF sessionId IS NOT NULL THEN
    CALL sp_khoa_phien(sessionId);
    SELECT MaNguoiChoi,HinhThucDangNhap,ThoiDiemBatDau,DonGiaGioApDung,TrangThaiPhien INTO ownerId,kind,started,rate,sessionState FROM PHIEN_SU_DUNG WHERE MaPhien=sessionId;
  END IF;
  SELECT TrangThaiThanhToan,TrangThaiPhucVu,HinhThucThanhToan,TongTien INTO state,serviceState,oldMethod,total FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang FOR UPDATE;
  IF NOT fn_co_quyen(pMaTacNhan,'ThuNgan,QuanLy') AND NOT (pMaTacNhan=ownerId AND pHinhThucThanhToan='TruVi' AND EXISTS(SELECT 1 FROM TAI_KHOAN WHERE MaTaiKhoan=pMaTacNhan AND TrangThai='HoatDong')) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  IF state='DaThanhToan' THEN
    IF oldMethod<>pHinhThucThanhToan THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60009,MESSAGE_TEXT='IDEMPOTENCY_CONFLICT'; END IF;
    SELECT pMaDonHang AS MaDoiTuong,1 AS DaThucHienTruoc; LEAVE proc;
  END IF;
  IF state<>'ChuaThanhToan' OR serviceState NOT IN ('DaTiepNhan','DangCheBien','DaGiao') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  IF pHinhThucThanhToan='TruVi' THEN
    IF ownerId IS NULL THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60012,MESSAGE_TEXT='INVALID_WALLET_OWNER'; END IF;
    SELECT SoDuVi INTO balance FROM NGUOI_CHOI WHERE MaTaiKhoan=ownerId FOR UPDATE;
    SET activeSessionId = NULL;
    SELECT MaPhien, HinhThucDangNhap, ThoiDiemBatDau, DonGiaGioApDung INTO activeSessionId, activeKind, activeStarted, activeRate FROM PHIEN_SU_DUNG WHERE MaNguoiChoi=ownerId AND TrangThaiPhien='DangHoatDong' LIMIT 1 FOR UPDATE;
    IF activeSessionId IS NOT NULL AND activeKind='TraTruoc' THEN
      IF activeRate>0 AND pThoiDiem>=fn_han_phien(activeStarted,balance,activeRate) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60014,MESSAGE_TEXT='PREPAID_EXPIRED'; END IF;
      SET holding=fn_tien_gio(activeStarted,pThoiDiem,activeRate);
      UPDATE PHIEN_SU_DUNG SET TienGiuCho=holding,TongTienTamTinh=holding WHERE MaPhien=activeSessionId;
    END IF;
    IF balance-holding<total THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60006,MESSAGE_TEXT='INSUFFICIENT_FUNDS'; END IF;
    UPDATE NGUOI_CHOI SET SoDuVi=SoDuVi-total WHERE MaTaiKhoan=ownerId;
    IF total>0 THEN INSERT INTO GIAO_DICH_VI(MaGiaoDich,MaYeuCau,LoaiGiaoDich,SoTien,ThoiDiemGD,TrangThaiGD,PhuongThucGD,MaNguoiChoi,MaDonHang,MaPhien) VALUES(pMaGiaoDich,CONCAT('dv:',pMaDonHang),'TruTienDichVu',total,pThoiDiem,'ThanhCong','NoiBo',ownerId,pMaDonHang,sessionId); END IF;
  END IF;
  UPDATE DON_GOI_DICH_VU SET TrangThaiThanhToan='DaThanhToan',HinhThucThanhToan=pHinhThucThanhToan,ThoiDiemThanhToan=pThoiDiem WHERE MaDonHang=pMaDonHang;
  SELECT pMaDonHang AS MaDoiTuong,0 AS DaThucHienTruoc;
END$$
DELIMITER ;
-- END 06_procedures/02_wallet_orders.sql

-- BEGIN 06_procedures/03_inventory.sql
DELIMITER $$
CREATE PROCEDURE sp_ghi_so_phieu_kho(IN pMaPhieuKho VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaTacNhan VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pThoiDiem DATETIME)
SQL SECURITY DEFINER
proc: BEGIN
  DECLARE state VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE kind VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE done BOOLEAN DEFAULT FALSE; DECLARE serviceId VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin; DECLARE qty INT; DECLARE book INT; DECLARE actual INT; DECLARE delta INT; DECLARE stock INT; DECLARE countLines INT DEFAULT 0;
  DECLARE items CURSOR FOR SELECT dv.MaDichVu,ct.SoLuong,ct.SoLuongSoSach,ct.SoLuongThucTe,ct.SoLuongChenhLech,dv.SoLuongTon FROM CHI_TIET_PHIEU_KHO ct JOIN DICH_VU dv ON dv.MaDichVu=ct.MaDichVu WHERE ct.MaPhieuKho=pMaPhieuKho ORDER BY dv.MaDichVu FOR UPDATE;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done=TRUE;
  IF NOT fn_co_quyen(pMaTacNhan,'QuanLy') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  IF NOT EXISTS(SELECT 1 FROM PHIEU_KHO WHERE MaPhieuKho=pMaPhieuKho) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60002,MESSAGE_TEXT='NOT_FOUND'; END IF;
  SELECT TrangThaiPhieu,LoaiPhieu INTO state,kind FROM PHIEU_KHO WHERE MaPhieuKho=pMaPhieuKho FOR UPDATE;
  IF state='DaGhiSo' THEN SELECT pMaPhieuKho AS MaDoiTuong,1 AS DaThucHienTruoc; LEAVE proc; END IF;
  IF state<>'Nhap' OR kind NOT IN ('NhapKho','XuatHuy','KiemKe') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  OPEN items;
  item_loop: LOOP
    FETCH items INTO serviceId,qty,book,actual,delta,stock;
    IF done THEN LEAVE item_loop; END IF;
    IF kind='KiemKe' AND (book IS NULL OR actual IS NULL OR stock<>book) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60010,MESSAGE_TEXT='INVENTORY_SNAPSHOT_STALE'; END IF;
    IF (kind='NhapKho' AND (qty<=0 OR delta<>qty)) OR (kind='XuatHuy' AND (qty<=0 OR delta<>-qty)) OR (kind='KiemKe' AND (qty<>0 OR delta<>actual-book)) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT'; END IF;
    IF stock+delta<0 THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60007,MESSAGE_TEXT='INSUFFICIENT_STOCK'; END IF;
    IF stock+delta>2147483647 THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT'; END IF;
    UPDATE DICH_VU SET SoLuongTon=SoLuongTon+delta WHERE MaDichVu=serviceId;
    SET countLines=countLines+1;
  END LOOP;
  CLOSE items;
  IF countLines=0 THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  UPDATE PHIEU_KHO SET TrangThaiPhieu='DaGhiSo',ThoiDiemGhiSo=pThoiDiem WHERE MaPhieuKho=pMaPhieuKho;
  SELECT pMaPhieuKho AS MaDoiTuong,0 AS DaThucHienTruoc;
END$$
DELIMITER ;
-- END 06_procedures/03_inventory.sql

-- BEGIN 06_procedures/04_khu_vuc_crud.sql
-- BTL2 Quản lý quán Net – L09, Nhóm 10
-- Ba thủ tục INSERT / UPDATE / DELETE trên bảng KHU_VUC (MD phụ trách)
-- Đáp ứng yêu cầu mục 2.1 của Mẫu Báo Cáo P1-2

DELIMITER $$

DROP PROCEDURE IF EXISTS `sp_khu_vuc_insert`$$
CREATE PROCEDURE `sp_khu_vuc_insert`(
    IN pMaKhuVuc VARCHAR(50),
    IN pTenKhuVuc VARCHAR(100),
    IN pMoTaViTri VARCHAR(255)
)
proc_label: BEGIN
    DECLARE vMa VARCHAR(10);
    DECLARE vTen VARCHAR(60);

    -- 1. Kiểm tra tham số đầu vào
    IF pMaKhuVuc IS NULL OR TRIM(pMaKhuVuc) = '' OR CHAR_LENGTH(TRIM(pMaKhuVuc)) > 10 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: MaKhuVuc khong hop le';
    END IF;

    IF pTenKhuVuc IS NULL OR TRIM(pTenKhuVuc) = '' OR CHAR_LENGTH(TRIM(pTenKhuVuc)) > 60 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: TenKhuVuc khong hop le';
    END IF;

    SET vMa = TRIM(pMaKhuVuc);
    SET vTen = TRIM(pTenKhuVuc);

    -- 2. Kiểm tra trùng lặp khóa chính
    IF EXISTS (SELECT 1 FROM `KHU_VUC` WHERE `MaKhuVuc` = vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60009, MESSAGE_TEXT = 'IDEMPOTENCY_CONFLICT: MaKhuVuc da ton tai';
    END IF;

    -- 3. Kiểm tra trùng lặp tên khu vực (UNIQUE)
    IF EXISTS (SELECT 1 FROM `KHU_VUC` WHERE `TenKhuVuc` = vTen) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: TenKhuVuc da ton tai';
    END IF;

    -- 4. Thực hiện thêm mới
    INSERT INTO `KHU_VUC` (`MaKhuVuc`, `TenKhuVuc`, `MoTaViTri`)
    VALUES (vMa, vTen, pMoTaViTri);

    -- 5. Trả kết quả thực thi
    SELECT vMa AS `MaKhuVuc`, 'INSERT' AS `ThaoTac`, ROW_COUNT() AS `SoDongTacDong`;
END$$

DROP PROCEDURE IF EXISTS `sp_khu_vuc_update`$$
CREATE PROCEDURE `sp_khu_vuc_update`(
    IN pMaKhuVuc VARCHAR(50),
    IN pTenKhuVucMoi VARCHAR(100),
    IN pMoTaViTriMoi VARCHAR(255)
)
proc_label: BEGIN
    DECLARE vMa VARCHAR(10);
    DECLARE vTen VARCHAR(60);

    -- 1. Kiểm tra tham số đầu vào
    IF pMaKhuVuc IS NULL OR TRIM(pMaKhuVuc) = '' OR CHAR_LENGTH(TRIM(pMaKhuVuc)) > 10 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: MaKhuVuc khong hop le';
    END IF;

    IF pTenKhuVucMoi IS NULL OR TRIM(pTenKhuVucMoi) = '' OR CHAR_LENGTH(TRIM(pTenKhuVucMoi)) > 60 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: TenKhuVuc khong hop le';
    END IF;

    SET vMa = TRIM(pMaKhuVuc);
    SET vTen = TRIM(pTenKhuVucMoi);

    -- 2. Kiểm tra tồn tại
    IF NOT EXISTS (SELECT 1 FROM `KHU_VUC` WHERE `MaKhuVuc` = vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60002, MESSAGE_TEXT = 'NOT_FOUND: Khu vuc khong ton tai';
    END IF;

    -- 3. Kiểm tra trùng lặp tên với khu vực khác
    IF EXISTS (SELECT 1 FROM `KHU_VUC` WHERE `TenKhuVuc` = vTen AND `MaKhuVuc` <> vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: TenKhuVuc da ton tai o khu vuc khac';
    END IF;

    -- 4. Cập nhật dữ liệu (không sửa mã khu vực)
    UPDATE `KHU_VUC`
    SET `TenKhuVuc` = vTen,
        `MoTaViTri` = pMoTaViTriMoi
    WHERE `MaKhuVuc` = vMa;

    -- 5. Trả kết quả thực thi
    SELECT vMa AS `MaKhuVuc`, 'UPDATE' AS `ThaoTac`, ROW_COUNT() AS `SoDongTacDong`;
END$$

DROP PROCEDURE IF EXISTS `sp_khu_vuc_delete`$$
CREATE PROCEDURE `sp_khu_vuc_delete`(
    IN pMaKhuVuc VARCHAR(50)
)
proc_label: BEGIN
    DECLARE vMa VARCHAR(10);

    -- 1. Kiểm tra tham số đầu vào
    IF pMaKhuVuc IS NULL OR TRIM(pMaKhuVuc) = '' OR CHAR_LENGTH(TRIM(pMaKhuVuc)) > 10 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: MaKhuVuc khong hop le';
    END IF;

    SET vMa = TRIM(pMaKhuVuc);

    -- 2. Kiểm tra tồn tại
    IF NOT EXISTS (SELECT 1 FROM `KHU_VUC` WHERE `MaKhuVuc` = vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60002, MESSAGE_TEXT = 'NOT_FOUND: Khu vuc khong ton tai';
    END IF;

    -- 3. Kiểm tra khóa ngoại tham chiếu từ MAY_TRAM
    IF EXISTS (SELECT 1 FROM `MAY_TRAM` WHERE `MaKhuVuc` = vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60015, MESSAGE_TEXT = 'DEPENDENCY_CONFLICT: Con may tram thuoc khu vuc nay';
    END IF;

    -- 4. Kiểm tra khóa ngoại tham chiếu từ PHAN_CONG_TRUC
    IF EXISTS (SELECT 1 FROM `PHAN_CONG_TRUC` WHERE `MaKhuVuc` = vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60015, MESSAGE_TEXT = 'DEPENDENCY_CONFLICT: Con phan cong truc thuoc khu vuc nay';
    END IF;

    -- 5. Thực hiện xóa
    DELETE FROM `KHU_VUC` WHERE `MaKhuVuc` = vMa;

    -- 6. Trả kết quả thực thi
    SELECT vMa AS `MaKhuVuc`, 'DELETE' AS `ThaoTac`, ROW_COUNT() AS `SoDongTacDong`;
END$$

DELIMITER ;
-- END 06_procedures/04_khu_vuc_crud.sql

-- BEGIN 06_procedures/05_reports_p12.sql
-- BTL2 Quản lý quán Net – L09, Nhóm 10
-- Hai thủ tục có điều kiện, vòng lặp và trả dữ liệu (TT & BD phụ trách)
-- Đáp ứng yêu cầu mục 2.3 của Mẫu Báo Cáo P1-2

DELIMITER $$

DROP PROCEDURE IF EXISTS `sp_bao_cao_doanh_thu_ngay`$$
CREATE PROCEDURE `sp_bao_cao_doanh_thu_ngay`(
    IN pNgayBatDau DATE,
    IN pNgayKetThuc DATE
)
proc_label: BEGIN
    DECLARE vNgayHienTai DATE;
    DECLARE vThuMay DECIMAL(12,0);
    DECLARE vThuDichVu DECIMAL(12,0);
    DECLARE vHoanDichVu DECIMAL(12,0);
    DECLARE vDanhSach JSON;
    DECLARE vItem JSON;

    -- 1. Kiểm tra tham số đầu vào
    IF pNgayBatDau IS NULL OR pNgayKetThuc IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: Ngay bat dau va ngay ket thuc khong duoc de trong';
    END IF;

    IF pNgayBatDau > pNgayKetThuc THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: Ngay bat dau phai nho hon hoac bang ngay ket thuc';
    END IF;

    IF DATEDIFF(pNgayKetThuc, pNgayBatDau) > 31 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: Khoang thoi gian bao cao khong vuot qua 31 ngay';
    END IF;

    -- 2. Khởi tạo mảng JSON và biến chạy ngày
    SET vDanhSach = JSON_ARRAY();
    SET vNgayHienTai = pNgayBatDau;

    -- 3. Vòng lặp WHILE duyệt qua từng ngày trong khoảng xét
    WHILE vNgayHienTai <= pNgayKetThuc DO
        -- Thu tiền máy từ các biên lai đã thanh toán trong ngày
        SELECT COALESCE(SUM(`TongTienGio`), 0)
        INTO vThuMay
        FROM `BIEN_LAI_TIEN_MAY`
        WHERE `TrangThaiBienLai` = 'DaThanhToan'
          AND DATE(`ThoiDiemThanhToan`) = vNgayHienTai;

        -- Thu tiền dịch vụ phát sinh theo thời điểm thanh toán
        SELECT COALESCE(SUM(`TongTien`), 0)
        INTO vThuDichVu
        FROM `DON_GOI_DICH_VU`
        WHERE `TrangThaiThanhToan` IN ('DaThanhToan', 'DaHoanTien')
          AND DATE(`ThoiDiemThanhToan`) = vNgayHienTai;

        -- Tiền hoàn dịch vụ phát sinh theo thời điểm hoàn tiền thực tế
        SELECT COALESCE(SUM(`SoTienDaHoan`), 0)
        INTO vHoanDichVu
        FROM `DON_GOI_DICH_VU`
        WHERE `SoTienDaHoan` > 0
          AND `ThoiDiemHoanTien` IS NOT NULL
          AND DATE(`ThoiDiemHoanTien`) = vNgayHienTai;

        -- Đóng gói kết quả ngày thành đối tượng JSON
        SET vItem = JSON_OBJECT(
            'Ngay', DATE_FORMAT(vNgayHienTai, '%Y-%m-%d'),
            'ThuTienMay', CAST(vThuMay AS SIGNED),
            'ThuDichVu', CAST(vThuDichVu AS SIGNED),
            'HoanDichVu', CAST(vHoanDichVu AS SIGNED),
            'DoanhThuRong', CAST((vThuMay + vThuDichVu - vHoanDichVu) AS SIGNED)
        );

        SET vDanhSach = JSON_ARRAY_APPEND(vDanhSach, '$', vItem);

        -- Chuyển sang ngày tiếp theo
        SET vNgayHienTai = DATE_ADD(vNgayHienTai, INTERVAL 1 DAY);
    END WHILE;

    -- 4. Trả một dòng JSON chứa danh sách kết quả từng ngày
    SELECT vDanhSach AS `BaoCaoDoanhThuNgay`;
END$$

DROP PROCEDURE IF EXISTS `sp_bao_cao_ton_dich_vu`$$
CREATE PROCEDURE `sp_bao_cao_ton_dich_vu`(
    IN pMaNhomDV VARCHAR(10),
    IN pNguongTon INT
)
proc_label: BEGIN
    DECLARE vDone INT DEFAULT 0;
    DECLARE vMaDichVu VARCHAR(10);
    DECLARE vTenDichVu VARCHAR(100);
    DECLARE vMaNhom VARCHAR(10);
    DECLARE vTenNhom VARCHAR(60);
    DECLARE vDonViTinh VARCHAR(30);
    DECLARE vGiaBan DECIMAL(12,0);
    DECLARE vSoLuongTon INT;
    DECLARE vTrangThaiKD VARCHAR(20);
    DECLARE vPhanLoai VARCHAR(20);
    DECLARE vDanhSach JSON;
    DECLARE vItem JSON;

    -- Khai báo CURSOR đọc danh mục dịch vụ theo nhóm hoặc toàn bộ
    DECLARE cur_dv CURSOR FOR
        SELECT d.`MaDichVu`, d.`TenDichVu`, d.`MaNhomDV`, n.`TenNhomDV`,
               v.`TenDonVi`, d.`GiaBanHienHanh`, d.`SoLuongTon`, d.`TrangThaiKinhDoanh`
        FROM `DICH_VU` d
        JOIN `NHOM_DICH_VU` n ON d.`MaNhomDV` = n.`MaNhomDV`
        JOIN `DON_VI_TINH` v ON d.`MaDonVi` = v.`MaDonVi`
        WHERE (pMaNhomDV IS NULL OR TRIM(pMaNhomDV) = '' OR d.`MaNhomDV` = TRIM(pMaNhomDV))
        ORDER BY d.`MaDichVu` ASC;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET vDone = 1;

    -- 1. Kiểm tra tham số đầu vào
    IF pNguongTon IS NULL OR pNguongTon < 0 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: Nguong ton phai la so khong am';
    END IF;

    -- 2. Kiểm tra nhóm dịch vụ có tồn tại không nếu được chỉ định
    IF pMaNhomDV IS NOT NULL AND TRIM(pMaNhomDV) <> '' THEN
        IF NOT EXISTS (SELECT 1 FROM `NHOM_DICH_VU` WHERE `MaNhomDV` = TRIM(pMaNhomDV)) THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60002, MESSAGE_TEXT = 'NOT_FOUND: Nhom dich vu khong ton tai';
        END IF;
    END IF;

    -- 3. Khởi tạo mảng JSON và mở CURSOR
    SET vDanhSach = JSON_ARRAY();
    OPEN cur_dv;

    read_loop: LOOP
        FETCH cur_dv INTO vMaDichVu, vTenDichVu, vMaNhom, vTenNhom,
                           vDonViTinh, vGiaBan, vSoLuongTon, vTrangThaiKD;
        IF vDone = 1 THEN
            LEAVE read_loop;
        END IF;

        -- 4. Sử dụng câu lệnh điều kiện IF phân loại trạng thái tồn kho
        IF vSoLuongTon = 0 THEN
            SET vPhanLoai = 'HetHang';
        ELSEIF vSoLuongTon <= pNguongTon THEN
            SET vPhanLoai = 'SapHet';
        ELSE
            SET vPhanLoai = 'DuHang';
        END IF;

        -- Đóng gói mặt hàng thành đối tượng JSON
        SET vItem = JSON_OBJECT(
            'MaDichVu', vMaDichVu,
            'TenDichVu', vTenDichVu,
            'MaNhomDV', vMaNhom,
            'TenNhomDV', vTenNhom,
            'DonViTinh', vDonViTinh,
            'GiaBanHienHanh', CAST(vGiaBan AS SIGNED),
            'SoLuongTon', vSoLuongTon,
            'TrangThaiKinhDoanh', vTrangThaiKD,
            'PhanLoaiTon', vPhanLoai
        );

        SET vDanhSach = JSON_ARRAY_APPEND(vDanhSach, '$', vItem);
    END LOOP;

    CLOSE cur_dv;

    -- 5. Trả một dòng JSON chứa danh sách mặt hàng
    SELECT vDanhSach AS `BaoCaoTonDichVu`;
END$$

DELIMITER ;
-- END 06_procedures/05_reports_p12.sql

-- BEGIN 08_triggers/01_history.sql
DELIMITER $$
CREATE TRIGGER tr_giao_dich_vi_update BEFORE UPDATE ON GIAO_DICH_VI FOR EACH ROW BEGIN IF OLD.TrangThaiGD IN ('ThanhCong','ThatBai') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_giao_dich_vi_delete BEFORE DELETE ON GIAO_DICH_VI FOR EACH ROW BEGIN IF OLD.TrangThaiGD IN ('ThanhCong','ThatBai') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_bien_lai_tien_may_update BEFORE UPDATE ON BIEN_LAI_TIEN_MAY FOR EACH ROW BEGIN IF OLD.TrangThaiBienLai='DaThanhToan' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_bien_lai_tien_may_delete BEFORE DELETE ON BIEN_LAI_TIEN_MAY FOR EACH ROW BEGIN IF OLD.TrangThaiBienLai='DaThanhToan' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_phieu_kho_update BEFORE UPDATE ON PHIEU_KHO FOR EACH ROW BEGIN IF OLD.TrangThaiPhieu='DaGhiSo' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_phieu_kho_delete BEFORE DELETE ON PHIEU_KHO FOR EACH ROW BEGIN IF OLD.TrangThaiPhieu='DaGhiSo' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_chi_tiet_goi_dich_vu_insert BEFORE INSERT ON CHI_TIET_GOI_DICH_VU FOR EACH ROW BEGIN IF (SELECT TrangThaiPhucVu FROM DON_GOI_DICH_VU WHERE MaDonHang=NEW.MaDonHang)<>'MoiDat' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_chi_tiet_goi_dich_vu_update BEFORE UPDATE ON CHI_TIET_GOI_DICH_VU FOR EACH ROW BEGIN IF (SELECT TrangThaiPhucVu FROM DON_GOI_DICH_VU WHERE MaDonHang=OLD.MaDonHang)<>'MoiDat' OR NOT (OLD.MaDonHang<=>NEW.MaDonHang) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_chi_tiet_goi_dich_vu_delete BEFORE DELETE ON CHI_TIET_GOI_DICH_VU FOR EACH ROW BEGIN IF (SELECT TrangThaiPhucVu FROM DON_GOI_DICH_VU WHERE MaDonHang=OLD.MaDonHang)<>'MoiDat' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_chi_tiet_phieu_kho_insert BEFORE INSERT ON CHI_TIET_PHIEU_KHO FOR EACH ROW BEGIN IF (SELECT TrangThaiPhieu FROM PHIEU_KHO WHERE MaPhieuKho=NEW.MaPhieuKho)<>'Nhap' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_chi_tiet_phieu_kho_update BEFORE UPDATE ON CHI_TIET_PHIEU_KHO FOR EACH ROW BEGIN IF (SELECT TrangThaiPhieu FROM PHIEU_KHO WHERE MaPhieuKho=OLD.MaPhieuKho)<>'Nhap' OR NOT (OLD.MaPhieuKho<=>NEW.MaPhieuKho) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_chi_tiet_phieu_kho_delete BEFORE DELETE ON CHI_TIET_PHIEU_KHO FOR EACH ROW BEGIN IF (SELECT TrangThaiPhieu FROM PHIEU_KHO WHERE MaPhieuKho=OLD.MaPhieuKho)<>'Nhap' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF; END$$
CREATE TRIGGER tr_order_immutable BEFORE UPDATE ON DON_GOI_DICH_VU FOR EACH ROW
BEGIN
  IF NOT (OLD.MaPhien<=>NEW.MaPhien) OR OLD.KenhDat<>NEW.KenhDat OR OLD.MaDonHang<>NEW.MaDonHang OR OLD.ThoiDiemDat<>NEW.ThoiDiemDat THEN
    SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT';
  END IF;
  IF (OLD.TongTien<>NEW.TongTien AND OLD.TrangThaiPhucVu<>'MoiDat') THEN
    SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT';
  END IF;
  IF OLD.TrangThaiThanhToan='DaThanhToan' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF;
END$$
CREATE TRIGGER tr_order_delete BEFORE DELETE ON DON_GOI_DICH_VU FOR EACH ROW
BEGIN
  IF OLD.TrangThaiPhucVu<>'MoiDat' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60011,MESSAGE_TEXT='IMMUTABLE_DOCUMENT'; END IF;
END$$
DELIMITER ;
-- END 08_triggers/01_history.sql

-- BEGIN 08_triggers/02_state_identity.sql
DELIMITER $$
CREATE TRIGGER tr_nguoi_choi_identity BEFORE DELETE ON NGUOI_CHOI FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM TAI_KHOAN WHERE MaTaiKhoan=OLD.MaTaiKhoan) AND NOT EXISTS(SELECT 1 FROM NHAN_VIEN WHERE MaTaiKhoan=OLD.MaTaiKhoan) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60015,MESSAGE_TEXT='DEPENDENCY_CONFLICT'; END IF; END$$
CREATE TRIGGER tr_nhan_vien_identity BEFORE DELETE ON NHAN_VIEN FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM TAI_KHOAN WHERE MaTaiKhoan=OLD.MaTaiKhoan) AND NOT EXISTS(SELECT 1 FROM NGUOI_CHOI WHERE MaTaiKhoan=OLD.MaTaiKhoan) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60015,MESSAGE_TEXT='DEPENDENCY_CONFLICT'; END IF; END$$
CREATE TRIGGER tr_order_state BEFORE UPDATE ON DON_GOI_DICH_VU FOR EACH ROW
BEGIN
  IF OLD.TrangThaiPhucVu<>NEW.TrangThaiPhucVu AND NOT (OLD.TrangThaiPhucVu='MoiDat' AND NEW.TrangThaiPhucVu='DaTiepNhan') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  IF NEW.TrangThaiPhucVu='DaTiepNhan' AND (NEW.MaNhanVienXuLy IS NULL OR NOT EXISTS(SELECT 1 FROM CHI_TIET_GOI_DICH_VU WHERE MaDonHang=NEW.MaDonHang) OR NEW.TongTien<>(SELECT SUM(ThanhTien) FROM CHI_TIET_GOI_DICH_VU WHERE MaDonHang=NEW.MaDonHang)) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
END$$
DELIMITER ;
-- END 08_triggers/02_state_identity.sql

-- BEGIN 08_triggers/03_order_detail_triggers.sql
-- BTL2 Quản lý quán Net – L09, Nhóm 10
-- Trigger liên bảng T-P12-02: Duy trì tổng tiền đầu đơn từ chi tiết gói dịch vụ (TD phụ trách)
-- Bảng kích hoạt: CHI_TIET_GOI_DICH_VU
-- Bảng chịu ảnh hưởng: DON_GOI_DICH_VU

DELIMITER $$

DROP TRIGGER IF EXISTS `tr_chi_tiet_goi_dich_vu_after_insert`$$
CREATE TRIGGER `tr_chi_tiet_goi_dich_vu_after_insert`
AFTER INSERT ON `CHI_TIET_GOI_DICH_VU`
FOR EACH ROW
BEGIN
    UPDATE `DON_GOI_DICH_VU`
    SET `TongTien` = `TongTien` + (NEW.`SoLuong` * NEW.`DonGiaBan`)
    WHERE `MaDonHang` = NEW.`MaDonHang`;
END$$

DROP TRIGGER IF EXISTS `tr_chi_tiet_goi_dich_vu_after_update`$$
CREATE TRIGGER `tr_chi_tiet_goi_dich_vu_after_update`
AFTER UPDATE ON `CHI_TIET_GOI_DICH_VU`
FOR EACH ROW
BEGIN
    UPDATE `DON_GOI_DICH_VU`
    SET `TongTien` = `TongTien` + (NEW.`SoLuong` * NEW.`DonGiaBan`) - (OLD.`SoLuong` * OLD.`DonGiaBan`)
    WHERE `MaDonHang` = NEW.`MaDonHang`;
END$$

DROP TRIGGER IF EXISTS `tr_chi_tiet_goi_dich_vu_after_delete`$$
CREATE TRIGGER `tr_chi_tiet_goi_dich_vu_after_delete`
AFTER DELETE ON `CHI_TIET_GOI_DICH_VU`
FOR EACH ROW
BEGIN
    UPDATE `DON_GOI_DICH_VU`
    SET `TongTien` = `TongTien` - (OLD.`SoLuong` * OLD.`DonGiaBan`)
    WHERE `MaDonHang` = OLD.`MaDonHang`;
END$$

DELIMITER ;
-- END 08_triggers/03_order_detail_triggers.sql

-- Insert the complete seed as a single transaction.
START TRANSACTION;

-- BEGIN 04_seed/01_reference_data.sql
-- Synthetic local demo accounts only. Password: MatKhau123! (change outside demo).
INSERT INTO NHOM_NGUOI_DUNG VALUES ('HoiVien','Hội viên'),('NhanVien','Nhân viên'),('VangLai','Vãng lai');
INSERT INTO KHU_VUC VALUES ('KV01','Khu thường',NULL),('KV02','Khu khác',NULL);
INSERT INTO NHOM_MAY VALUES ('VIP','Máy VIP',15000,NULL);
INSERT INTO BANG_GIA VALUES ('HoiVien','VIP',15000),('VangLai','VIP',15000),('NhanVien','VIP',15000);
INSERT INTO MAY_TRAM VALUES ('M01','Máy 01','AVAILABLE',1,1,'VIP','KV01'),('M02','Máy 02','AVAILABLE',1,2,'VIP','KV01'),('M03','Máy 03','MAINTENANCE',1,3,'VIP','KV01');
INSERT INTO NHOM_DICH_VU VALUES ('NDV01','Đồ ăn'),('NDV02','Đồ uống');
INSERT INTO DON_VI_TINH VALUES ('DVT01','Phần'),('DVT02','Chai');
INSERT INTO MAY_IN VALUES ('MI01','In quầy',NULL);
INSERT INTO DICH_VU VALUES ('DV01','Mì trứng',15000,50,'DangKinhDoanh','NDV01','DVT01','MI01'),('DV02','Nước ngọt',12000,100,'DangKinhDoanh','NDV02','DVT02','MI01');
INSERT INTO TAI_KHOAN(MaTaiKhoan,TenDangNhap,MatKhauBam,Ten,TrangThai,MaNhomND) VALUES ('TK01','admin','scrypt:32768:8:1$4Vo8NDFXxVQZeijE$b8550ee326f01ffe822f66bc82b81bc615a58956617aa52e027b230d2b0f2c90c7ea8fefabdf9542fc54ad66e276c4a7dfbda00712fa0c24147d680a9293faff','Demo admin','HoatDong','NhanVien');
INSERT INTO NHAN_VIEN VALUES ('TK01','QuanLy',0,'2026-01-01',NULL);
INSERT INTO TAI_KHOAN(MaTaiKhoan,TenDangNhap,MatKhauBam,Ten,TrangThai,MaNhomND) VALUES ('TK02','player1','scrypt:32768:8:1$4Vo8NDFXxVQZeijE$b8550ee326f01ffe822f66bc82b81bc615a58956617aa52e027b230d2b0f2c90c7ea8fefabdf9542fc54ad66e276c4a7dfbda00712fa0c24147d680a9293faff','Demo player1','HoatDong','HoiVien');
INSERT INTO NGUOI_CHOI VALUES ('TK02','DEMO-TK02',100000,'2026-01-01');
INSERT INTO TAI_KHOAN(MaTaiKhoan,TenDangNhap,MatKhauBam,Ten,TrangThai,MaNhomND) VALUES ('TK03','cashier1','scrypt:32768:8:1$4Vo8NDFXxVQZeijE$b8550ee326f01ffe822f66bc82b81bc615a58956617aa52e027b230d2b0f2c90c7ea8fefabdf9542fc54ad66e276c4a7dfbda00712fa0c24147d680a9293faff','Demo cashier1','HoatDong','NhanVien');
INSERT INTO NHAN_VIEN VALUES ('TK03','ThuNgan',0,'2026-01-01',NULL);
INSERT INTO TAI_KHOAN(MaTaiKhoan,TenDangNhap,MatKhauBam,Ten,TrangThai,MaNhomND) VALUES ('TK04','locked_user','scrypt:32768:8:1$4Vo8NDFXxVQZeijE$b8550ee326f01ffe822f66bc82b81bc615a58956617aa52e027b230d2b0f2c90c7ea8fefabdf9542fc54ad66e276c4a7dfbda00712fa0c24147d680a9293faff','Demo locked_user','Khoa','HoiVien');
INSERT INTO NGUOI_CHOI VALUES ('TK04','DEMO-TK04',100000,'2026-01-01');
INSERT INTO TAI_KHOAN(MaTaiKhoan,TenDangNhap,MatKhauBam,Ten,TrangThai,MaNhomND) VALUES ('TK05','player2','scrypt:32768:8:1$4Vo8NDFXxVQZeijE$b8550ee326f01ffe822f66bc82b81bc615a58956617aa52e027b230d2b0f2c90c7ea8fefabdf9542fc54ad66e276c4a7dfbda00712fa0c24147d680a9293faff','Demo player2','HoatDong','HoiVien');
INSERT INTO NGUOI_CHOI VALUES ('TK05','DEMO-TK05',100000,'2026-01-01');
INSERT INTO TAI_KHOAN(MaTaiKhoan,TenDangNhap,MatKhauBam,Ten,TrangThai,MaNhomND) VALUES ('TK06','dual_user','scrypt:32768:8:1$4Vo8NDFXxVQZeijE$b8550ee326f01ffe822f66bc82b81bc615a58956617aa52e027b230d2b0f2c90c7ea8fefabdf9542fc54ad66e276c4a7dfbda00712fa0c24147d680a9293faff','Demo dual_user','HoatDong','NhanVien');
INSERT INTO NHAN_VIEN VALUES ('TK06','ThuNgan',0,'2026-01-01',NULL);
INSERT INTO NGUOI_CHOI VALUES ('TK06','DEMO-TK06',100000,'2026-01-01');
INSERT INTO TAI_KHOAN(MaTaiKhoan,TenDangNhap,MatKhauBam,Ten,TrangThai,MaNhomND) VALUES ('TK07','barista','scrypt:32768:8:1$4Vo8NDFXxVQZeijE$b8550ee326f01ffe822f66bc82b81bc615a58956617aa52e027b230d2b0f2c90c7ea8fefabdf9542fc54ad66e276c4a7dfbda00712fa0c24147d680a9293faff','Demo barista','HoatDong','NhanVien');
INSERT INTO NHAN_VIEN VALUES ('TK07','PhaChe',0,'2026-01-01',NULL);
INSERT INTO TAI_KHOAN(MaTaiKhoan,TenDangNhap,MatKhauBam,Ten,TrangThai,MaNhomND) VALUES ('TK08','paused_user','scrypt:32768:8:1$4Vo8NDFXxVQZeijE$b8550ee326f01ffe822f66bc82b81bc615a58956617aa52e027b230d2b0f2c90c7ea8fefabdf9542fc54ad66e276c4a7dfbda00712fa0c24147d680a9293faff','Demo paused_user','TamDung','HoiVien');
INSERT INTO NGUOI_CHOI VALUES ('TK08','DEMO-TK08',100000,'2026-01-01');
INSERT INTO SO_DIEN_THOAI VALUES ('TK01','DEMO-PHONE');
INSERT INTO DIA_CHI_NV VALUES ('TK01',1,NULL,NULL,NULL,'Địa chỉ giả lập');
INSERT INTO CA_TRUC VALUES ('CA01','Ca sáng','2026-10-26 07:00:00','2026-10-26 12:00:00');
INSERT INTO PHAN_CONG_TRUC VALUES ('TK03','CA01','KV01',NULL);
-- END 04_seed/01_reference_data.sql

-- BEGIN 04_seed/02_demo_scenarios.sql
-- Backend demo starts without active sessions/orders/documents.
-- Reproducible business scenarios are created through API by tests/integration and tests/e2e.
-- END 04_seed/02_demo_scenarios.sql

-- BEGIN 04_seed/03_p12_demo_seed.sql
-- BTL2 Quản lý quán Net – L09, Nhóm 10
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
-- END 04_seed/03_p12_demo_seed.sql

COMMIT;

-- Expected result after a successful installation: 23 base tables.
SELECT DATABASE() AS DatabaseName, COUNT(*) AS TableCount
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE';
