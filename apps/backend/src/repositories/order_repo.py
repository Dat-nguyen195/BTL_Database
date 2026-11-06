from src.errors import InternalError
"""Truy vấn và thao tác đơn gọi dịch vụ (Q04, tạo nháp, sp_tiep_nhan_don, sp_thanh_toan_don)."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from src.services.transaction import consume_call_results


def get_orders(
    conn,
    trang_thai_phuc_vu: Optional[str] = None,
    trang_thai_thanh_toan: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    ma_nguoi_choi: Optional[str] = None,
    sort_by: str = "ThoiDiemDat",
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    sort_whitelist = {
        "ThoiDiemDat": "d.ThoiDiemDat",
        "MaDonHang": "d.MaDonHang",
    }
    sort_column = sort_whitelist.get(sort_by, "d.ThoiDiemDat")

    where_clauses = ["1=1"]
    params: List[Any] = []

    if trang_thai_phuc_vu:
        where_clauses.append("d.TrangThaiPhucVu = %s")
        params.append(trang_thai_phuc_vu)
    if trang_thai_thanh_toan:
        where_clauses.append("d.TrangThaiThanhToan = %s")
        params.append(trang_thai_thanh_toan)
    if from_date and to_date:
        where_clauses.append("d.ThoiDiemDat >= %s")
        where_clauses.append("d.ThoiDiemDat < DATE_ADD(%s, INTERVAL 1 DAY)")
        params.extend([from_date, to_date])
    if ma_nguoi_choi:
        where_clauses.append("p.MaNguoiChoi = %s")
        params.append(ma_nguoi_choi)

    where_sql = " AND ".join(where_clauses)

    cursor = conn.cursor(dictionary=True)
    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM DON_GOI_DICH_VU d
        LEFT JOIN PHIEN_SU_DUNG p ON d.MaPhien = p.MaPhien
        WHERE {where_sql}
    """
    cursor.execute(count_sql, tuple(params))
    total_row = cursor.fetchone()
    total = total_row["total"] if total_row else 0

    offset = (page - 1) * page_size
    select_sql = f"""
        SELECT d.MaDonHang,
               d.ThoiDiemDat AS ThoiDiemDat,
               d.KenhDat, d.MaPhien, d.MaNhanVienXuLy,
               CAST(d.TongTien AS SIGNED) AS TongTien,
               d.TrangThaiPhucVu, d.TrangThaiThanhToan, d.HinhThucThanhToan,
               d.ThoiDiemThanhToan AS ThoiDiemThanhToan,
               p.MaNguoiChoi, p.MaMay
        FROM DON_GOI_DICH_VU d
        LEFT JOIN PHIEN_SU_DUNG p ON d.MaPhien = p.MaPhien
        WHERE {where_sql}
        ORDER BY {sort_column} ASC, d.MaDonHang ASC
        LIMIT %s OFFSET %s
    """
    cursor.execute(select_sql, tuple(params + [page_size, offset]))
    rows = cursor.fetchall()
    cursor.close()
    return rows, total


def get_order_by_id(conn, ma_don_hang: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT d.MaDonHang,
               d.ThoiDiemDat AS ThoiDiemDat,
               d.KenhDat, d.MaPhien, d.MaNhanVienXuLy,
               CAST(d.TongTien AS SIGNED) AS TongTien,
               d.TrangThaiPhucVu, d.TrangThaiThanhToan, d.HinhThucThanhToan,
               d.ThoiDiemThanhToan AS ThoiDiemThanhToan,
               p.MaNguoiChoi, p.MaMay
        FROM DON_GOI_DICH_VU d
        LEFT JOIN PHIEN_SU_DUNG p ON d.MaPhien = p.MaPhien
        WHERE d.MaDonHang = %s
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_don_hang,))
    row = cursor.fetchone()
    cursor.close()
    return row


def get_order_lines(conn, ma_don_hang: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT ct.MaDonHang, ct.MaDichVu, dv.TenDichVu,
               ct.SoLuong,
               CAST(ct.DonGiaBan AS SIGNED) AS DonGiaBan,
               CAST(ct.ThanhTien AS SIGNED) AS ThanhTien
        FROM CHI_TIET_GOI_DICH_VU ct
        JOIN DICH_VU dv ON ct.MaDichVu = dv.MaDichVu
        WHERE ct.MaDonHang = %s
        ORDER BY ct.MaDichVu ASC
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_don_hang,))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def insert_order_header(
    conn,
    ma_don_hang: str,
    kenh_dat: str,
    ma_phien: Optional[str],
    tong_tien: int,
    thoi_diem: datetime,
) -> None:
    sql = """
        INSERT INTO DON_GOI_DICH_VU (
            MaDonHang, ThoiDiemDat, KenhDat, MaPhien, TongTien,
            TrangThaiPhucVu, TrangThaiThanhToan, SoTienDaHoan
        ) VALUES (
            %s, %s, %s, %s, %s,
            'MoiDat', 'ChuaThanhToan', 0
        )
    """
    cursor = conn.cursor()
    cursor.execute(sql, (
        ma_don_hang,
        thoi_diem,
        kenh_dat,
        ma_phien,
        tong_tien,
    ))
    cursor.close()


def insert_order_line(
    conn,
    ma_don_hang: str,
    ma_dich_vu: str,
    so_luong: int,
    don_gia_ban: int,
) -> None:
    # ThanhTien là GENERATED ALWAYS STORED nên không insert trực tiếp cột này
    sql = """
        INSERT INTO CHI_TIET_GOI_DICH_VU (
            MaDonHang, MaDichVu, SoLuong, DonGiaBan
        ) VALUES (%s, %s, %s, %s)
    """
    cursor = conn.cursor()
    cursor.execute(sql, (ma_don_hang, ma_dich_vu, so_luong, don_gia_ban))
    cursor.close()


def call_sp_tiep_nhan_don(
    conn,
    ma_don_hang: str,
    ma_tac_nhan: str,
    thoi_diem: datetime,
) -> Tuple[str, bool]:
    cursor = conn.cursor()
    args = (
        ma_don_hang,
        ma_tac_nhan,
        thoi_diem,
    )
    cursor.callproc("sp_tiep_nhan_don", args)
    results = consume_call_results(cursor)
    cursor.close()

    if results and results[0]:
        first_row = results[0][0]
        return first_row[0], bool(first_row[1])
    raise InternalError("Routine không trả kết quả.")


def call_sp_thanh_toan_don(
    conn,
    ma_don_hang: str,
    ma_giao_dich: str,
    hinh_thuc_tt: str,
    ma_tac_nhan: str,
    thoi_diem: datetime,
) -> Tuple[str, bool]:
    cursor = conn.cursor()
    args = (
        ma_don_hang,
        ma_giao_dich,
        hinh_thuc_tt,
        ma_tac_nhan,
        thoi_diem,
    )
    cursor.callproc("sp_thanh_toan_don", args)
    results = consume_call_results(cursor)
    cursor.close()

    if results and results[0]:
        first_row = results[0][0]
        return first_row[0], bool(first_row[1])
    raise InternalError("Routine không trả kết quả.")

