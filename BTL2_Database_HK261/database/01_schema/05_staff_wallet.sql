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
