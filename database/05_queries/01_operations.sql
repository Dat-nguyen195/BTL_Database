-- BTL2 Quản lý quán Net – L09, Nhóm 09
-- Bộ truy vấn vận hành P1-2 (MD & BD phụ trách)
-- Đáp ứng yêu cầu mục 1.3 của Mẫu Báo Cáo P1-2

-- ============================================================================
-- Q-P12-01 (MD phụ trách): Danh sách máy trạm theo khu vực, nhóm và trạng thái
-- Yêu cầu: SELECT, FROM, WHERE, ORDER BY (Bảng chính: MAY_TRAM)
-- Use case: Thu ngân / Quản lý theo dõi tình trạng máy tại từng khu vực trên sơ đồ máy
-- ============================================================================
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

-- ============================================================================
-- Q-P12-02 (BD phụ trách): Dịch vụ đang bán theo nhóm dịch vụ và khoảng giá
-- Yêu cầu: SELECT, FROM, WHERE, ORDER BY (Bảng chính: DICH_VU)
-- Use case: Khách hàng xem thực đơn món ăn/uống theo khoảng giá trên giao diện gọi món
-- ============================================================================
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

-- ============================================================================
-- Q-P12-03 (BD phụ trách): Thống kê tổng tiền đơn hàng đã thanh toán theo ngày và kênh
-- Yêu cầu: SELECT, FROM, WHERE, GROUP BY, ORDER BY, SUM/COUNT (Bảng chính: DON_GOI_DICH_VU)
-- Use case: Quản lý tổng hợp doanh số gọi món theo kênh đặt (Tại máy / Tại quầy)
-- ============================================================================
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
