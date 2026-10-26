"""Báo cáo quản lý (Q05–Q08) theo query_catalog.md và api_contract.md."""
from typing import Any, Dict, List, Optional


def get_revenue_report(conn, from_date: str, to_date: str) -> Dict[str, Any]:
    """Q05: Doanh thu thực tế theo ngày và kênh, KHÔNG cộng nạp ví theo BR-16."""
    cursor = conn.cursor(dictionary=True)

    # Doanh thu tiền giờ máy từ biên lai đã thanh toán
    sql_machine = """
        SELECT DATE_FORMAT(ThoiDiemThanhToan, '%Y-%m-%d') AS Ngay,
               'TienGio' AS LoaiDoanhThu,
               'TaiMay' AS Kenh,
               HinhThucThanhToan,
               COUNT(*) AS SoGiaoDich,
               CAST(SUM(TongTienGio) AS SIGNED) AS TongTien
        FROM BIEN_LAI_TIEN_MAY
        WHERE TrangThaiBienLai = 'DaThanhToan'
          AND ThoiDiemThanhToan >= %s
          AND ThoiDiemThanhToan < DATE_ADD(%s, INTERVAL 1 DAY)
        GROUP BY DATE_FORMAT(ThoiDiemThanhToan, '%Y-%m-%d'), HinhThucThanhToan
    """
    cursor.execute(sql_machine, (from_date, to_date))
    rows_machine = cursor.fetchall()

    # Doanh thu dịch vụ từ đơn hàng đã thanh toán
    sql_service = """
        SELECT DATE_FORMAT(ThoiDiemThanhToan, '%Y-%m-%d') AS Ngay,
               'DichVu' AS LoaiDoanhThu,
               KenhDat AS Kenh,
               HinhThucThanhToan,
               COUNT(*) AS SoGiaoDich,
               CAST(SUM(TongTien) AS SIGNED) AS TongTien
        FROM DON_GOI_DICH_VU
        WHERE TrangThaiThanhToan = 'DaThanhToan'
          AND ThoiDiemThanhToan >= %s
          AND ThoiDiemThanhToan < DATE_ADD(%s, INTERVAL 1 DAY)
        GROUP BY DATE_FORMAT(ThoiDiemThanhToan, '%Y-%m-%d'), KenhDat, HinhThucThanhToan
    """
    cursor.execute(sql_service, (from_date, to_date))
    rows_service = cursor.fetchall()

    cursor.close()

    all_breakdowns = rows_machine + rows_service
    total_revenue = sum(r["TongTien"] for r in all_breakdowns if r["TongTien"])

    return {
        "FromDate": from_date,
        "ToDate": to_date,
        "TongDoanhThu": total_revenue,
        "ChiTiet": all_breakdowns,
    }


def get_stock_report(conn, threshold: Optional[int] = None) -> List[Dict[str, Any]]:
    """Q06: Tồn khả dụng và mặt hàng dưới ngưỡng báo động tồn kho."""
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT dv.MaDichVu, dv.TenDichVu, dv.SoLuongTon,
               CAST(dv.GiaBanHienHanh AS SIGNED) AS GiaBanHienHanh,
               dv.TrangThaiKinhDoanh,
               ndv.TenNhomDV, dvt.TenDonVi
        FROM DICH_VU dv
        JOIN NHOM_DICH_VU ndv ON dv.MaNhomDV = ndv.MaNhomDV
        JOIN DON_VI_TINH dvt ON dv.MaDonVi = dvt.MaDonVi
        WHERE 1=1
    """
    params = []
    if threshold is not None:
        sql += " AND dv.SoLuongTon <= %s"
        params.append(threshold)

    sql += " ORDER BY dv.SoLuongTon ASC, dv.MaDichVu ASC"
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_reconciliation_report(conn, from_date: str, to_date: str) -> List[Dict[str, Any]]:
    """Q07: Đối soát biến động tồn kho giữa nhập, xuất hủy, kiểm kê và bán ra."""
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT dv.MaDichVu,dv.TenDichVu,dv.SoLuongTon AS TonHienTai,
               COALESCE(k.TongNhap,0) AS TongNhap,
               COALESCE(k.TongXuatHuy,0) AS TongXuatHuy,
               COALESCE(k.ChenhLechKiemKe,0) AS ChenhLechKiemKe,
               COALESCE(s.TongBan,0) AS TongBan,
               COALESCE(k.DeltaKho,0)-COALESCE(s.TongBan,0) AS BienDongRong
        FROM DICH_VU dv
        LEFT JOIN (
          SELECT ct.MaDichVu,
            SUM(IF(pk.LoaiPhieu='NhapKho',ct.SoLuong,0)) AS TongNhap,
            SUM(IF(pk.LoaiPhieu='XuatHuy',ct.SoLuong,0)) AS TongXuatHuy,
            SUM(IF(pk.LoaiPhieu='KiemKe',ct.SoLuongChenhLech,0)) AS ChenhLechKiemKe,
            SUM(ct.SoLuongChenhLech) AS DeltaKho
          FROM PHIEU_KHO pk JOIN CHI_TIET_PHIEU_KHO ct ON ct.MaPhieuKho=pk.MaPhieuKho
          WHERE pk.TrangThaiPhieu='DaGhiSo' AND pk.ThoiDiemGhiSo >= %s
            AND pk.ThoiDiemGhiSo < DATE_ADD(%s,INTERVAL 1 DAY)
          GROUP BY ct.MaDichVu
        ) k ON k.MaDichVu=dv.MaDichVu
        LEFT JOIN (
          SELECT ct.MaDichVu,SUM(ct.SoLuong) AS TongBan
          FROM DON_GOI_DICH_VU d JOIN CHI_TIET_GOI_DICH_VU ct ON ct.MaDonHang=d.MaDonHang
          WHERE (d.TrangThaiPhucVu IN ('DaTiepNhan','DangCheBien','DaGiao')
             OR (d.TrangThaiPhucVu='DaHuy' AND d.TrangThaiTruocHuy IN ('DangCheBien','DaGiao')))
            AND d.ThoiDiemDat >= %s AND d.ThoiDiemDat < DATE_ADD(%s,INTERVAL 1 DAY)
          GROUP BY ct.MaDichVu
        ) s ON s.MaDichVu=dv.MaDichVu
        ORDER BY dv.MaDichVu
    """
    cursor.execute(sql, (from_date, to_date, from_date, to_date))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_shifts_report(conn, from_date: str, to_date: str, ma_nhan_vien: Optional[str] = None) -> List[Dict[str, Any]]:
    """Q08: Lịch ca trực và phát hiện xung đột / chồng chéo giờ làm việc."""
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT pc.MaNhanVien, tk.Ho, tk.TenDem, tk.Ten,
               c.MaCa, c.TenCa,
               c.ThoiDiemBatDau AS ThoiDiemBatDau,
               c.ThoiDiemKetThuc AS ThoiDiemKetThuc,
               pc.MaKhuVuc, kv.TenKhuVuc, pc.GhiChuNhiemVu
        FROM PHAN_CONG_TRUC pc
        JOIN CA_TRUC c ON pc.MaCa = c.MaCa
        JOIN TAI_KHOAN tk ON pc.MaNhanVien = tk.MaTaiKhoan
        JOIN KHU_VUC kv ON pc.MaKhuVuc = kv.MaKhuVuc
        WHERE c.ThoiDiemKetThuc > %s
          AND c.ThoiDiemBatDau < DATE_ADD(%s, INTERVAL 1 DAY)
    """
    params = [from_date, to_date]
    if ma_nhan_vien:
        sql += " AND pc.MaNhanVien = %s"
        params.append(ma_nhan_vien)

    sql += " ORDER BY pc.MaNhanVien ASC, c.ThoiDiemBatDau ASC"
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    cursor.close()

    # Thuật toán phát hiện chồng giờ: cùng 1 nhân viên có ca sau bắt đầu trước khi ca trước kết thúc
    # (Hai ca tiếp giáp [kết thúc ca 1 == bắt đầu ca 2] được phép theo query_catalog Q08)
    for i in range(len(rows)):
        rows[i]["ChongGio"] = False
        for j in range(len(rows)):
            if i != j and rows[i]["MaNhanVien"] == rows[j]["MaNhanVien"] and rows[i]["MaCa"] != rows[j]["MaCa"]:
                start_i = rows[i]["ThoiDiemBatDau"]
                end_i = rows[i]["ThoiDiemKetThuc"]
                start_j = rows[j]["ThoiDiemBatDau"]
                end_j = rows[j]["ThoiDiemKetThuc"]
                # Chồng giờ nếu: start_i < end_j VÀ start_j < end_i
                if start_i < end_j and start_j < end_i:
                    rows[i]["ChongGio"] = True
                    break

    return rows

