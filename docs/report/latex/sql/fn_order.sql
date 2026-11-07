DELIMITER $$

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
