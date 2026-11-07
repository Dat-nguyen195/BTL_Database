DELIMITER $$

CREATE PROCEDURE `sp_khu_vuc_update`(
    IN pMaKhuVuc VARCHAR(50),
    IN pTenKhuVucMoi VARCHAR(100),
    IN pMoTaViTriMoi VARCHAR(255)
)
proc_label: BEGIN
    DECLARE vMa VARCHAR(10);
    DECLARE vTen VARCHAR(60);

    -- 1. Kiểm tra tham số đầu vào
    IF pMaKhuVuc IS NULL OR TRIM(pMaKhuVuc) = '' OR CHAR_LENGTH(TRIM(pMaKhuVuc)) > 10 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: MaKhuVuc khong hop le';
    END IF;

    IF pTenKhuVucMoi IS NULL OR TRIM(pTenKhuVucMoi) = '' OR CHAR_LENGTH(TRIM(pTenKhuVucMoi)) > 60 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: TenKhuVuc khong hop le';
    END IF;

    SET vMa = TRIM(pMaKhuVuc);
    SET vTen = TRIM(pTenKhuVucMoi);

    -- 2. Kiểm tra tồn tại
    IF NOT EXISTS (SELECT 1 FROM `KHU_VUC` WHERE `MaKhuVuc` = vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60002, MESSAGE_TEXT = 'NOT_FOUND: Khu vuc khong ton tai';
    END IF;

    -- 3. Kiểm tra trùng lặp tên với khu vực khác
    IF EXISTS (SELECT 1 FROM `KHU_VUC` WHERE `TenKhuVuc` = vTen AND `MaKhuVuc` <> vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: TenKhuVuc da ton tai o khu vuc khac';
    END IF;

    -- 4. Cập nhật dữ liệu (không sửa mã khu vực)
    UPDATE `KHU_VUC`
    SET `TenKhuVuc` = vTen,
        `MoTaViTri` = pMoTaViTriMoi
    WHERE `MaKhuVuc` = vMa;

    -- 5. Trả kết quả thực thi
    SELECT vMa AS `MaKhuVuc`, 'UPDATE' AS `ThaoTac`, ROW_COUNT() AS `SoDongTacDong`;
END$$

DELIMITER ;
