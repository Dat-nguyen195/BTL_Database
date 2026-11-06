DELIMITER $$

CREATE PROCEDURE `sp_khu_vuc_insert`(
    IN pMaKhuVuc VARCHAR(50),
    IN pTenKhuVuc VARCHAR(100),
    IN pMoTaViTri VARCHAR(255)
)
proc_label: BEGIN
    DECLARE vMa VARCHAR(10);
    DECLARE vTen VARCHAR(60);

    -- 1. Kiểm tra tham số đầu vào
    IF pMaKhuVuc IS NULL OR TRIM(pMaKhuVuc) = '' OR CHAR_LENGTH(TRIM(pMaKhuVuc)) > 10 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: MaKhuVuc khong hop le';
    END IF;

    IF pTenKhuVuc IS NULL OR TRIM(pTenKhuVuc) = '' OR CHAR_LENGTH(TRIM(pTenKhuVuc)) > 60 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: TenKhuVuc khong hop le';
    END IF;

    SET vMa = TRIM(pMaKhuVuc);
    SET vTen = TRIM(pTenKhuVuc);

    -- 2. Kiểm tra trùng lặp khóa chính
    IF EXISTS (SELECT 1 FROM `KHU_VUC` WHERE `MaKhuVuc` = vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60009, MESSAGE_TEXT = 'IDEMPOTENCY_CONFLICT: MaKhuVuc da ton tai';
    END IF;

    -- 3. Kiểm tra trùng lặp tên khu vực (UNIQUE)
    IF EXISTS (SELECT 1 FROM `KHU_VUC` WHERE `TenKhuVuc` = vTen) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: TenKhuVuc da ton tai';
    END IF;

    -- 4. Thực hiện thêm mới
    INSERT INTO `KHU_VUC` (`MaKhuVuc`, `TenKhuVuc`, `MoTaViTri`)
    VALUES (vMa, vTen, pMoTaViTri);

    -- 5. Trả kết quả thực thi
    SELECT vMa AS `MaKhuVuc`, 'INSERT' AS `ThaoTac`, ROW_COUNT() AS `SoDongTacDong`;
END$$

DELIMITER ;
