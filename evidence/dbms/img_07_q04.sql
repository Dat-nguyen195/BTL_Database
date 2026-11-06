SELECT
    nv.`MaTaiKhoan` AS `MaNhanVien`,
    tk.`Ten` AS `TenNhanVien`,
    nv.`ChucVu`,
    COUNT(DISTINCT pc.`MaCa`) AS `TongSoCaTruc`,
    ROUND(SUM(TIMESTAMPDIFF(MINUTE, ca.`ThoiDiemBatDau`, ca.`ThoiDiemKetThuc`)) / 60.0, 2) AS `TongGioTruc`
FROM `NHAN_VIEN` nv
JOIN `TAI_KHOAN` tk ON nv.`MaTaiKhoan` = tk.`MaTaiKhoan`
JOIN (
    SELECT DISTINCT `MaNhanVien`, `MaCa`
    FROM `PHAN_CONG_TRUC`
) pc ON nv.`MaTaiKhoan` = pc.`MaNhanVien`
JOIN `CA_TRUC` ca ON pc.`MaCa` = ca.`MaCa`
WHERE ca.`ThoiDiemBatDau` >= '2026-10-01 00:00:00'
  AND ca.`ThoiDiemKetThuc` <= '2026-11-30 23:59:59'
GROUP BY nv.`MaTaiKhoan`, tk.`Ten`, nv.`ChucVu`
ORDER BY `TongGioTruc` DESC, `TongSoCaTruc` DESC;
