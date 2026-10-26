from src.errors import InternalError
"""Truy vấn và thao tác phiên sử dụng (Q02, sp_mo_phien, sp_ket_thuc_phien)."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from src.services.transaction import consume_call_results


def get_sessions(
    conn,
    trang_thai: Optional[str] = None,
    ma_may: Optional[str] = None,
    ma_nguoi_choi: Optional[str] = None,
    sort_by: str = "ThoiDiemBatDau",
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    sort_whitelist = {
        "ThoiDiemBatDau": "p.ThoiDiemBatDau",
        "MaPhien": "p.MaPhien",
    }
    sort_column = sort_whitelist.get(sort_by, "p.ThoiDiemBatDau")

    where_clauses = ["1=1"]
    params = []
    if trang_thai:
        where_clauses.append("p.TrangThaiPhien = %s")
        params.append(trang_thai)
    if ma_may:
        where_clauses.append("p.MaMay = %s")
        params.append(ma_may)
    if ma_nguoi_choi:
        where_clauses.append("p.MaNguoiChoi = %s")
        params.append(ma_nguoi_choi)

    where_sql = " AND ".join(where_clauses)

    cursor = conn.cursor(dictionary=True)
    # Đếm tổng số
    count_sql = f"SELECT COUNT(*) AS total FROM PHIEN_SU_DUNG p WHERE {where_sql}"
    cursor.execute(count_sql, tuple(params))
    total_row = cursor.fetchone()
    total = total_row["total"] if total_row else 0

    # Lấy danh sách trang
    offset = (page - 1) * page_size
    select_sql = f"""
        SELECT p.MaPhien, p.HinhThucDangNhap,
               p.ThoiDiemBatDau AS ThoiDiemBatDau,
               p.ThoiDiemKetThuc AS ThoiDiemKetThuc,
               CAST(p.DonGiaGioApDung AS SIGNED) AS DonGiaGioApDung,
               CAST(p.TienNapTruoc AS SIGNED) AS TienNapTruoc,
               CAST(p.TienGiuCho AS SIGNED) AS TienGiuCho,
               CAST(p.TongTienTamTinh AS SIGNED) AS TongTienTamTinh,
               p.TrangThaiPhien, p.MaMay, p.MaNguoiChoi,
               m.TenMay,
               tk.TenDangNhap
        FROM PHIEN_SU_DUNG p
        JOIN MAY_TRAM m ON p.MaMay = m.MaMay
        LEFT JOIN TAI_KHOAN tk ON p.MaNguoiChoi = tk.MaTaiKhoan
        WHERE {where_sql}
        ORDER BY {sort_column} ASC, p.MaPhien ASC
        LIMIT %s OFFSET %s
    """
    cursor.execute(select_sql, tuple(params + [page_size, offset]))
    rows = cursor.fetchall()
    cursor.close()
    return rows, total


def get_session_by_id(conn, ma_phien: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT p.MaPhien, p.HinhThucDangNhap,
               p.ThoiDiemBatDau AS ThoiDiemBatDau,
               p.ThoiDiemKetThuc AS ThoiDiemKetThuc,
               CAST(p.DonGiaGioApDung AS SIGNED) AS DonGiaGioApDung,
               CAST(p.TienNapTruoc AS SIGNED) AS TienNapTruoc,
               CAST(p.TienGiuCho AS SIGNED) AS TienGiuCho,
               CAST(p.TongTienTamTinh AS SIGNED) AS TongTienTamTinh,
               p.TrangThaiPhien, p.MaMay, p.MaNguoiChoi,
               m.TenMay,
               tk.TenDangNhap
        FROM PHIEN_SU_DUNG p
        JOIN MAY_TRAM m ON p.MaMay = m.MaMay
        LEFT JOIN TAI_KHOAN tk ON p.MaNguoiChoi = tk.MaTaiKhoan
        WHERE p.MaPhien = %s
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_phien,))
    row = cursor.fetchone()
    cursor.close()
    return row


def get_active_prepaid_sessions(conn) -> List[Dict[str, Any]]:
    sql = """
        SELECT p.MaPhien, p.HinhThucDangNhap, p.ThoiDiemBatDau,
               CAST(p.DonGiaGioApDung AS SIGNED) AS DonGiaGioApDung,
               CAST(p.TienNapTruoc AS SIGNED) AS TienNapTruoc,
               CAST(p.TienGiuCho AS SIGNED) AS TienGiuCho,
               p.TrangThaiPhien, p.MaMay, p.MaNguoiChoi
        FROM PHIEN_SU_DUNG p
        WHERE p.TrangThaiPhien = 'DangHoatDong'
          AND p.HinhThucDangNhap = 'TraTruoc'
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def call_sp_mo_phien(
    conn,
    ma_phien: str,
    ma_may: str,
    ma_nguoi_choi: Optional[str],
    hinh_thuc: str,
    tien_nap_truoc: int,
    ma_tac_nhan: str,
    thoi_diem: datetime,
) -> Tuple[str, bool]:
    cursor = conn.cursor()
    args = (
        ma_phien,
        ma_may,
        ma_nguoi_choi,
        hinh_thuc,
        tien_nap_truoc,
        ma_tac_nhan,
        thoi_diem,
    )
    cursor.callproc("sp_mo_phien", args)
    results = consume_call_results(cursor)
    cursor.close()

    if results and results[0]:
        first_row = results[0][0]
        ma_doi_tuong = first_row[0]
        da_thuc_hien_truoc = bool(first_row[1])
        return ma_doi_tuong, da_thuc_hien_truoc
    raise InternalError("Routine không trả kết quả.")


def call_sp_ket_thuc_phien(
    conn,
    ma_phien: str,
    ma_bien_lai: str,
    ma_giao_dich: str,
    hinh_thuc_tt: str,
    tien_nhan: int,
    ma_tac_nhan: str,
    thoi_diem: datetime,
) -> Tuple[str, bool]:
    cursor = conn.cursor()
    args = (
        ma_phien,
        ma_bien_lai,
        ma_giao_dich,
        hinh_thuc_tt,
        tien_nhan,
        ma_tac_nhan,
        thoi_diem,
    )
    cursor.callproc("sp_ket_thuc_phien", args)
    results = consume_call_results(cursor)
    cursor.close()

    if results and results[0]:
        first_row = results[0][0]
        ma_doi_tuong = first_row[0]
        da_thuc_hien_truoc = bool(first_row[1])
        return ma_doi_tuong, da_thuc_hien_truoc
    raise InternalError("Routine không trả kết quả.")

