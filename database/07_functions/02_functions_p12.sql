-- BTL2 Quản lý quán Net – L09, Nhóm 09
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
