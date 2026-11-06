SELECT
    d.`MaDichVu`,
    d.`TenDichVu`,
    ndv.`TenNhomDV`,
    dvt.`TenDonVi`,
    d.`GiaBanHienHanh`,
    d.`SoLuongTon`
FROM `DICH_VU` d
JOIN `NHOM_DICH_VU` ndv ON d.`MaNhomDV` = ndv.`MaNhomDV`
JOIN `DON_VI_TINH` dvt ON d.`MaDonVi` = dvt.`MaDonVi`
WHERE d.`TrangThaiKinhDoanh` = 'DangKinhDoanh'
  AND d.`MaNhomDV` = 'NDV01'
  AND d.`GiaBanHienHanh` BETWEEN 10000 AND 50000
ORDER BY d.`GiaBanHienHanh` DESC, d.`MaDichVu` ASC;
