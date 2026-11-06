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
