from src.errors import InternalError
"""Truy vấn số dư, lịch sử ví và nạp ví (Q03, sp_nap_vi)."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from src.services.transaction import consume_call_results


def get_wallet(conn, ma_nguoi_choi: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT MaTaiKhoan, SoCCCD,
               CAST(SoDuVi AS SIGNED) AS SoDuVi,
               DATE_FORMAT(NgayDangKy, '%Y-%m-%d') AS NgayDangKy
        FROM NGUOI_CHOI
        WHERE MaTaiKhoan = %s
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_nguoi_choi,))
    row = cursor.fetchone()
    cursor.close()
    return row


def get_holding_amount(conn, ma_nguoi_choi: str) -> int:
    """Tính tổng tiền giữ chỗ từ các phiên TraTruoc đang hoạt động của người chơi."""
    sql = """
        SELECT COALESCE(SUM(TienGiuCho), 0) AS TongGiuCho
        FROM PHIEN_SU_DUNG
        WHERE MaNguoiChoi = %s
          AND TrangThaiPhien = 'DangHoatDong'
          AND HinhThucDangNhap = 'TraTruoc'
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_nguoi_choi,))
    row = cursor.fetchone()
    cursor.close()
    return int(row["TongGiuCho"]) if row and row["TongGiuCho"] is not None else 0


def get_transactions(
    conn,
    ma_nguoi_choi: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "ThoiDiemGD",
) -> Tuple[List[Dict[str, Any]], int]:
    sort_whitelist = {
        "ThoiDiemGD": "g.ThoiDiemGD",
        "MaGiaoDich": "g.MaGiaoDich",
    }
    sort_column = sort_whitelist.get(sort_by, "g.ThoiDiemGD")

    where_clauses = ["g.MaNguoiChoi = %s"]
    params: List[Any] = [ma_nguoi_choi]

    if from_date and to_date:
        where_clauses.append("g.ThoiDiemGD >= %s")
        where_clauses.append("g.ThoiDiemGD < DATE_ADD(%s, INTERVAL 1 DAY)")
        params.extend([from_date, to_date])

    where_sql = " AND ".join(where_clauses)

    cursor = conn.cursor(dictionary=True)
    count_sql = f"SELECT COUNT(*) AS total FROM GIAO_DICH_VI g WHERE {where_sql}"
    cursor.execute(count_sql, tuple(params))
    total_row = cursor.fetchone()
    total = total_row["total"] if total_row else 0

    offset = (page - 1) * page_size
    select_sql = f"""
        SELECT g.MaGiaoDich, g.MaYeuCau, g.LoaiGiaoDich,
               CAST(g.SoTien AS SIGNED) AS SoTien,
               g.ThoiDiemGD AS ThoiDiemGD,
               g.TrangThaiGD, g.PhuongThucGD, g.MaNguoiChoi,
               g.MaNhanVienXuLy, g.MaDonHang, g.MaPhien, g.MaGDGoc
        FROM GIAO_DICH_VI g
        WHERE {where_sql}
        ORDER BY {sort_column} DESC, g.MaGiaoDich ASC
        LIMIT %s OFFSET %s
    """
    cursor.execute(select_sql, tuple(params + [page_size, offset]))
    rows = cursor.fetchall()
    cursor.close()
    return rows, total


def get_transaction_by_id(conn, ma_giao_dich: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT MaGiaoDich, MaYeuCau, LoaiGiaoDich,
               CAST(SoTien AS SIGNED) AS SoTien,
               ThoiDiemGD AS ThoiDiemGD,
               TrangThaiGD, PhuongThucGD, MaNguoiChoi,
               MaNhanVienXuLy, MaDonHang, MaPhien, MaGDGoc
        FROM GIAO_DICH_VI
        WHERE MaGiaoDich = %s
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_giao_dich,))
    row = cursor.fetchone()
    cursor.close()
    return row


def get_transaction_by_yeu_cau(conn, ma_yeu_cau: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT MaGiaoDich, MaYeuCau, LoaiGiaoDich,
               CAST(SoTien AS SIGNED) AS SoTien,
               ThoiDiemGD AS ThoiDiemGD,
               TrangThaiGD, PhuongThucGD, MaNguoiChoi,
               MaNhanVienXuLy, MaDonHang, MaPhien, MaGDGoc
        FROM GIAO_DICH_VI
        WHERE MaYeuCau = %s
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_yeu_cau,))
    row = cursor.fetchone()
    cursor.close()
    return row


def call_sp_nap_vi(
    conn,
    ma_giao_dich: str,
    ma_yeu_cau: str,
    ma_nguoi_choi: str,
    so_tien: int,
    phuong_thuc: str,
    ma_tac_nhan: str,
    thoi_diem: datetime,
) -> Tuple[str, bool]:
    cursor = conn.cursor()
    args = (
        ma_giao_dich,
        ma_yeu_cau,
        ma_nguoi_choi,
        so_tien,
        phuong_thuc,
        ma_tac_nhan,
        thoi_diem,
    )
    cursor.callproc("sp_nap_vi", args)
    results = consume_call_results(cursor)
    cursor.close()

    if results and results[0]:
        first_row = results[0][0]
        return first_row[0], bool(first_row[1])
    raise InternalError("Routine không trả kết quả.")

