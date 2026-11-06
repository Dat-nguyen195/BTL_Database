DELIMITER $$

CREATE PROCEDURE `sp_bao_cao_doanh_thu_ngay`(
    IN pNgayBatDau DATE,
    IN pNgayKetThuc DATE
)
proc_label: BEGIN
    DECLARE vNgayHienTai DATE;
    DECLARE vThuMay DECIMAL(12,0);
    DECLARE vThuDichVu DECIMAL(12,0);
    DECLARE vHoanDichVu DECIMAL(12,0);
    DECLARE vDanhSach JSON;
    DECLARE vItem JSON;

    -- 1. Kiểm tra tham số đầu vào
    IF pNgayBatDau IS NULL OR pNgayKetThuc IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: Ngay bat dau va ngay ket thuc khong duoc de trong';
    END IF;

    IF pNgayBatDau > pNgayKetThuc THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: Ngay bat dau phai nho hon hoac bang ngay ket thuc';
    END IF;

    IF DATEDIFF(pNgayKetThuc, pNgayBatDau) > 31 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 60001, MESSAGE_TEXT = 'INVALID_INPUT: Khoang thoi gian bao cao khong vuot qua 31 ngay';
    END IF;

    -- 2. Khởi tạo mảng JSON và biến chạy ngày
    SET vDanhSach = JSON_ARRAY();
    SET vNgayHienTai = pNgayBatDau;

    -- 3. Vòng lặp WHILE duyệt qua từng ngày trong khoảng xét
    WHILE vNgayHienTai <= pNgayKetThuc DO
        -- Thu tiền máy từ các biên lai đã thanh toán trong ngày
        SELECT COALESCE(SUM(`TongTienGio`), 0)
        INTO vThuMay
        FROM `BIEN_LAI_TIEN_MAY`
        WHERE `TrangThaiBienLai` = 'DaThanhToan'
          AND DATE(`ThoiDiemThanhToan`) = vNgayHienTai;

        -- Thu tiền dịch vụ phát sinh theo thời điểm thanh toán
        SELECT COALESCE(SUM(`TongTien`), 0)
        INTO vThuDichVu
        FROM `DON_GOI_DICH_VU`
        WHERE `TrangThaiThanhToan` IN ('DaThanhToan', 'DaHoanTien')
          AND DATE(`ThoiDiemThanhToan`) = vNgayHienTai;

        -- Tiền hoàn dịch vụ phát sinh theo thời điểm hoàn tiền thực tế
        SELECT COALESCE(SUM(`SoTienDaHoan`), 0)
        INTO vHoanDichVu
        FROM `DON_GOI_DICH_VU`
        WHERE `SoTienDaHoan` > 0
          AND `ThoiDiemHoanTien` IS NOT NULL
          AND DATE(`ThoiDiemHoanTien`) = vNgayHienTai;

        -- Đóng gói kết quả ngày thành đối tượng JSON
        SET vItem = JSON_OBJECT(
            'Ngay', DATE_FORMAT(vNgayHienTai, '%Y-%m-%d'),
            'ThuTienMay', CAST(vThuMay AS SIGNED),
            'ThuDichVu', CAST(vThuDichVu AS SIGNED),
            'HoanDichVu', CAST(vHoanDichVu AS SIGNED),
            'DoanhThuRong', CAST((vThuMay + vThuDichVu - vHoanDichVu) AS SIGNED)
        );

        SET vDanhSach = JSON_ARRAY_APPEND(vDanhSach, '$', vItem);

        -- Chuyển sang ngày tiếp theo
        SET vNgayHienTai = DATE_ADD(vNgayHienTai, INTERVAL 1 DAY);
    END WHILE;

    -- 4. Trả một dòng JSON chứa danh sách kết quả từng ngày
    SELECT vDanhSach AS `BaoCaoDoanhThuNgay`;
END$$

DELIMITER ;
