SELECT
    DATE(d.`ThoiDiemDat`) AS `NgayDat`,
    d.`KenhDat`,
    COUNT(d.`MaDonHang`) AS `SoLuongDon`,
    SUM(d.`TongTien`) AS `TongTienDonHang`
FROM `DON_GOI_DICH_VU` d
WHERE d.`TrangThaiThanhToan` = 'DaThanhToan'
  AND d.`ThoiDiemDat` >= '2026-10-01 00:00:00'
  AND d.`ThoiDiemDat` <= '2026-11-30 23:59:59'
GROUP BY DATE(d.`ThoiDiemDat`), d.`KenhDat`
ORDER BY `NgayDat` DESC, `TongTienDonHang` DESC;
