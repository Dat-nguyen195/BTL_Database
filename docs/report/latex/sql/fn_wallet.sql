DELIMITER $$

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

DELIMITER ;
