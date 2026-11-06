-- BTL2 Quản lý quán Net – L09, Nhóm 09
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
