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
