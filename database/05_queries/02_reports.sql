-- BTL2 Quản lý quán Net – L09, Nhóm 10
-- Bộ truy vấn báo cáo & phân tích P1-2 (TT & HT phụ trách)
-- Đáp ứng yêu cầu mục 1.3 của Mẫu Báo Cáo P1-2

-- ============================================================================
-- Q-P12-04 (TT phụ trách): Tổng số ca và thời lượng trực của nhân viên trong khoảng ngày
-- Yêu cầu: SELECT, FROM, WHERE, GROUP BY, ORDER BY, COUNT/SUM (Bảng: NHAN_VIEN, CA_TRUC, PHAN_CONG_TRUC)
-- Quy tắc: Khử trùng cặp (MaNhanVien, MaCa) trước khi cộng giờ (vì 1 NV có thể phụ trách nhiều khu trong 1 ca)
-- Use case: Quản lý chấm công và tổng hợp số giờ làm việc thực tế của nhân viên
-- ============================================================================
SELECT
    nv.`MaTaiKhoan` AS `MaNhanVien`,
    tk.`Ten` AS `TenNhanVien`,
    nv.`ChucVu`,
    COUNT(DISTINCT pc.`MaCa`) AS `TongSoCaTruc`,
    ROUND(SUM(TIMESTAMPDIFF(MINUTE, ca.`ThoiDiemBatDau`, ca.`ThoiDiemKetThuc`)) / 60.0, 2) AS `TongGioTruc`
FROM `NHAN_VIEN` nv
JOIN `TAI_KHOAN` tk ON nv.`MaTaiKhoan` = tk.`MaTaiKhoan`
JOIN (
    -- Khử trùng nhân viên - ca trực trước khi tính thời lượng
    SELECT DISTINCT `MaNhanVien`, `MaCa`
    FROM `PHAN_CONG_TRUC`
) pc ON nv.`MaTaiKhoan` = pc.`MaNhanVien`
JOIN `CA_TRUC` ca ON pc.`MaCa` = ca.`MaCa`
WHERE ca.`ThoiDiemBatDau` >= '2026-10-01 00:00:00'
  AND ca.`ThoiDiemKetThuc` <= '2026-11-30 23:59:59'
GROUP BY nv.`MaTaiKhoan`, tk.`Ten`, nv.`ChucVu`
ORDER BY `TongGioTruc` DESC, `TongSoCaTruc` DESC;

-- ============================================================================
-- Q-P12-05 (HT phụ trách): Hội viên có số dư lớn hơn trung bình của nhóm hội viên có GD ví thành công
-- Yêu cầu: 2 cấp truy vấn lồng (nested queries), AGGREGATE FUNCTION AVG (Bảng: NGUOI_CHOI, GIAO_DICH_VI)
-- Cấu trúc: SoDuVi > (SELECT AVG(...) ... IN (SELECT ...))
-- Use case: Phân tích nhóm khách hàng trung thành, có số dư cao để gửi chương trình khuyến mãi/VIP
-- ============================================================================
SELECT
    nc.`MaTaiKhoan` AS `MaHoiVien`,
    tk.`Ten` AS `TenHoiVien`,
    nc.`SoCCCD`,
    nc.`SoDuVi`,
    nc.`NgayDangKy`
FROM `NGUOI_CHOI` nc
JOIN `TAI_KHOAN` tk ON nc.`MaTaiKhoan` = tk.`MaTaiKhoan`
WHERE nc.`SoDuVi` > (
    -- Cấp lồng 1: Tính số dư trung bình của nhóm hội viên có phát sinh giao dịch ví thành công
    SELECT AVG(sub_nc.`SoDuVi`)
    FROM `NGUOI_CHOI` sub_nc
    WHERE sub_nc.`MaTaiKhoan` IN (
        -- Cấp lồng 2: Lấy danh sách mã hội viên có giao dịch ví thành công trong khoảng xét
        SELECT DISTINCT gd.`MaNguoiChoi`
        FROM `GIAO_DICH_VI` gd
        WHERE gd.`TrangThaiGD` = 'ThanhCong'
          AND gd.`ThoiDiemGD` >= '2026-10-01 00:00:00'
          AND gd.`ThoiDiemGD` <= '2026-11-30 23:59:59'
    )
)
ORDER BY nc.`SoDuVi` DESC, nc.`MaTaiKhoan` ASC;
