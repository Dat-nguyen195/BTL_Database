DELIMITER $$

CREATE TRIGGER `tr_chi_tiet_goi_dich_vu_after_insert`
AFTER INSERT ON `CHI_TIET_GOI_DICH_VU`
FOR EACH ROW
BEGIN
    UPDATE `DON_GOI_DICH_VU`
    SET `TongTien` = `TongTien` + (NEW.`SoLuong` * NEW.`DonGiaBan`)
    WHERE `MaDonHang` = NEW.`MaDonHang`;
END$$

CREATE TRIGGER `tr_chi_tiet_goi_dich_vu_after_update`
AFTER UPDATE ON `CHI_TIET_GOI_DICH_VU`
FOR EACH ROW
BEGIN
    UPDATE `DON_GOI_DICH_VU`
    SET `TongTien` = `TongTien` + (NEW.`SoLuong` * NEW.`DonGiaBan`) - (OLD.`SoLuong` * OLD.`DonGiaBan`)
    WHERE `MaDonHang` = NEW.`MaDonHang`;
END$$

CREATE TRIGGER `tr_chi_tiet_goi_dich_vu_after_delete`
AFTER DELETE ON `CHI_TIET_GOI_DICH_VU`
FOR EACH ROW
BEGIN
    UPDATE `DON_GOI_DICH_VU`
    SET `TongTien` = `TongTien` - (OLD.`SoLuong` * OLD.`DonGiaBan`)
    WHERE `MaDonHang` = OLD.`MaDonHang`;
END$$

DELIMITER ;
