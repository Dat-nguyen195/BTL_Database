DELIMITER $$

CREATE PROCEDURE `sp_bao_cao_ton_dich_vu`(
    IN pMaNhomDV VARCHAR(10),
    IN pNguongTon INT
)
proc_label: BEGIN
    DECLARE vDone INT DEFAULT 0;
    DECLARE vMaDichVu VARCHAR(10);
    DECLARE vTenDichVu VARCHAR(100);
    DECLARE vMaNhom VARCHAR(10);
    DECLARE vTenNhom VARCHAR(60);
    DECLARE vDonViTinh VARCHAR(30);
    DECLARE vGiaBan DECIMAL(12,0);
    DECLARE vSoLuongTon INT;
    DECLARE vTrangThaiKD VARCHAR(20);
    DECLARE vPhanLoai VARCHAR(20);
    DECLARE vDanhSach JSON;
    DECLARE vItem JSON;

    -- Khai báo CURSOR đọc danh mục dịch vụ theo nhóm hoặc toàn bộ
    DECLARE cur_dv CURSOR FOR
        SELECT d.`MaDichVu`, d.`TenDichVu`, d.`MaNhomDV`, n.`TenNhomDV`,
               v.`TenDonVi`, d.`GiaBanHienHanh`, d.`SoLuongTon`, d.`TrangThaiKinhDoanh`
        FROM `DICH_VU` d
        JOIN `NHOM_DICH_VU` n ON d.`MaNhomDV` = n.`MaNhomDV`
        JOIN `DON_VI_TINH` v ON d.`MaDonVi` = v.`MaDonVi`
        WHERE (pMaNhomDV IS NULL OR TRIM(pMaNhomDV) = '' OR d.`MaNhomDV` = TRIM(pMaNhomDV))
        ORDER BY d.`MaDichVu` ASC;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET vDone = 1;

    -- 1. Kiểm tra tham số đầu vào
    IF pNguongTon IS NULL OR pNguongTon < 0 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: Nguong ton phai la so khong am';
    END IF;

    -- 2. Kiểm tra nhóm dịch vụ có tồn tại không nếu được chỉ định
    IF pMaNhomDV IS NOT NULL AND TRIM(pMaNhomDV) <> '' THEN
        IF NOT EXISTS (SELECT 1 FROM `NHOM_DICH_VU` WHERE `MaNhomDV` = TRIM(pMaNhomDV)) THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60002, MESSAGE_TEXT = 'NOT_FOUND: Nhom dich vu khong ton tai';
        END IF;
    END IF;

    -- 3. Khởi tạo mảng JSON và mở CURSOR
    SET vDanhSach = JSON_ARRAY();
    OPEN cur_dv;

    read_loop: LOOP
        FETCH cur_dv INTO vMaDichVu, vTenDichVu, vMaNhom, vTenNhom,
                           vDonViTinh, vGiaBan, vSoLuongTon, vTrangThaiKD;
        IF vDone = 1 THEN
            LEAVE read_loop;
        END IF;

        -- 4. Sử dụng câu lệnh điều kiện IF phân loại trạng thái tồn kho
        IF vSoLuongTon = 0 THEN
            SET vPhanLoai = 'HetHang';
        ELSEIF vSoLuongTon <= pNguongTon THEN
            SET vPhanLoai = 'SapHet';
        ELSE
            SET vPhanLoai = 'DuHang';
        END IF;

        -- Đóng gói mặt hàng thành đối tượng JSON
        SET vItem = JSON_OBJECT(
            'MaDichVu', vMaDichVu,
            'TenDichVu', vTenDichVu,
            'MaNhomDV', vMaNhom,
            'TenNhomDV', vTenNhom,
            'DonViTinh', vDonViTinh,
            'GiaBanHienHanh', CAST(vGiaBan AS SIGNED),
            'SoLuongTon', vSoLuongTon,
            'TrangThaiKinhDoanh', vTrangThaiKD,
            'PhanLoaiTon', vPhanLoai
        );

        SET vDanhSach = JSON_ARRAY_APPEND(vDanhSach, '$', vItem);
    END LOOP;

    CLOSE cur_dv;

    -- 5. Trả một dòng JSON chứa danh sách mặt hàng
    SELECT vDanhSach AS `BaoCaoTonDichVu`;
END$$

DELIMITER ;
