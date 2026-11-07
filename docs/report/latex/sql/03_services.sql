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
