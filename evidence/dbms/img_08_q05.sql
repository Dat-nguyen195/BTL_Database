SELECT
    nc.`MaTaiKhoan` AS `MaHoiVien`,
    tk.`Ten` AS `TenHoiVien`,
    nc.`SoCCCD`,
    nc.`SoDuVi`,
    nc.`NgayDangKy`
FROM `NGUOI_CHOI` nc
JOIN `TAI_KHOAN` tk ON nc.`MaTaiKhoan` = tk.`MaTaiKhoan`
WHERE nc.`SoDuVi` > (
    SELECT AVG(sub_nc.`SoDuVi`)
    FROM `NGUOI_CHOI` sub_nc
    WHERE sub_nc.`MaTaiKhoan` IN (
        SELECT DISTINCT gd.`MaNguoiChoi`
        FROM `GIAO_DICH_VI` gd
        WHERE gd.`TrangThaiGD` = 'ThanhCong'
          AND gd.`ThoiDiemGD` >= '2026-10-01 00:00:00'
          AND gd.`ThoiDiemGD` <= '2026-11-30 23:59:59'
    )
)
ORDER BY nc.`SoDuVi` DESC, nc.`MaTaiKhoan` ASC;
