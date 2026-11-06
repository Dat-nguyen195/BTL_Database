-- BTL2 Quản lý quán Net – L09, Nhóm 09
-- Ba thủ tục INSERT / UPDATE / DELETE trên bảng KHU_VUC (MD phụ trách)
-- Đáp ứng yêu cầu mục 2.1 của Mẫu Báo Cáo P1-2

DELIMITER $$

DROP PROCEDURE IF EXISTS `sp_khu_vuc_insert`$$
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

DROP PROCEDURE IF EXISTS `sp_khu_vuc_update`$$
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

DROP PROCEDURE IF EXISTS `sp_khu_vuc_delete`$$
CREATE PROCEDURE `sp_khu_vuc_delete`(
    IN pMaKhuVuc VARCHAR(50)
)
proc_label: BEGIN
    DECLARE vMa VARCHAR(10);

    -- 1. Kiểm tra tham số đầu vào
    IF pMaKhuVuc IS NULL OR TRIM(pMaKhuVuc) = '' OR CHAR_LENGTH(TRIM(pMaKhuVuc)) > 10 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: MaKhuVuc khong hop le';
    END IF;

    SET vMa = TRIM(pMaKhuVuc);

    -- 2. Kiểm tra tồn tại
    IF NOT EXISTS (SELECT 1 FROM `KHU_VUC` WHERE `MaKhuVuc` = vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60002, MESSAGE_TEXT = 'NOT_FOUND: Khu vuc khong ton tai';
    END IF;

    -- 3. Kiểm tra khóa ngoại tham chiếu từ MAY_TRAM
    IF EXISTS (SELECT 1 FROM `MAY_TRAM` WHERE `MaKhuVuc` = vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60015, MESSAGE_TEXT = 'DEPENDENCY_CONFLICT: Con may tram thuoc khu vuc nay';
    END IF;

    -- 4. Kiểm tra khóa ngoại tham chiếu từ PHAN_CONG_TRUC
    IF EXISTS (SELECT 1 FROM `PHAN_CONG_TRUC` WHERE `MaKhuVuc` = vMa) THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60015, MESSAGE_TEXT = 'DEPENDENCY_CONFLICT: Con phan cong truc thuoc khu vuc nay';
    END IF;

    -- 5. Thực hiện xóa
    DELETE FROM `KHU_VUC` WHERE `MaKhuVuc` = vMa;

    -- 6. Trả kết quả thực thi
    SELECT vMa AS `MaKhuVuc`, 'DELETE' AS `ThaoTac`, ROW_COUNT() AS `SoDongTacDong`;
END$$

DELIMITER ;
