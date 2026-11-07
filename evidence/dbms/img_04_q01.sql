SELECT
    m.`MaMay`,
    m.`TenMay`,
    m.`TrangThaiMay`,
    k.`TenKhuVuc`,
    nm.`TenNhomMay`,
    nm.`DonGiaGioMacDinh`,
    m.`ViTriHang`,
    m.`ViTriCot`
FROM `MAY_TRAM` m
JOIN `KHU_VUC` k ON m.`MaKhuVuc` = k.`MaKhuVuc`
JOIN `NHOM_MAY` nm ON m.`MaNhomMay` = nm.`MaNhomMay`
WHERE m.`TrangThaiMay` IN ('AVAILABLE', 'ONLINE')
  AND k.`MaKhuVuc` = 'KV01'
ORDER BY m.`ViTriHang` ASC, m.`ViTriCot` ASC;
