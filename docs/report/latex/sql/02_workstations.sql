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
