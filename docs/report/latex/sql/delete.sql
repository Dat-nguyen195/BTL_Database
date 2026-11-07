DELIMITER $$

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
