from src.errors import InternalError
"""Truy vấn và thao tác chứng từ kho (tạo nháp, sp_ghi_so_phieu_kho)."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from src.services.transaction import consume_call_results


def get_inventory_documents(
    conn,
    loai_phieu: Optional[str] = None,
    trang_thai: Optional[str] = None,
    sort_by: str = "ThoiDiemLap",
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    sort_whitelist = {
        "ThoiDiemLap": "p.ThoiDiemLap",
        "MaPhieuKho": "p.MaPhieuKho",
    }
    sort_column = sort_whitelist.get(sort_by, "p.ThoiDiemLap")

    where_clauses = ["1=1"]
    params: List[Any] = []

    if loai_phieu:
        where_clauses.append("p.LoaiPhieu = %s")
        params.append(loai_phieu)
    if trang_thai:
        where_clauses.append("p.TrangThaiPhieu = %s")
        params.append(trang_thai)

    where_sql = " AND ".join(where_clauses)

    cursor = conn.cursor(dictionary=True)
    count_sql = f"SELECT COUNT(*) AS total FROM PHIEU_KHO p WHERE {where_sql}"
    cursor.execute(count_sql, tuple(params))
    total_row = cursor.fetchone()
    total = total_row["total"] if total_row else 0

    offset = (page - 1) * page_size
    select_sql = f"""
        SELECT p.MaPhieuKho, p.LoaiPhieu, p.TrangThaiPhieu,
               p.ThoiDiemLap AS ThoiDiemLap,
               p.ThoiDiemGhiSo AS ThoiDiemGhiSo,
               p.GhiChuLyDo, p.MaNhanVienLap, p.MaDonHang
        FROM PHIEU_KHO p
        WHERE {where_sql}
        ORDER BY {sort_column} ASC, p.MaPhieuKho ASC
        LIMIT %s OFFSET %s
    """
    cursor.execute(select_sql, tuple(params + [page_size, offset]))
    rows = cursor.fetchall()
    cursor.close()
    return rows, total


def get_inventory_document_by_id(conn, ma_phieu_kho: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT p.MaPhieuKho, p.LoaiPhieu, p.TrangThaiPhieu,
               p.ThoiDiemLap AS ThoiDiemLap,
               p.ThoiDiemGhiSo AS ThoiDiemGhiSo,
               p.GhiChuLyDo, p.MaNhanVienLap, p.MaDonHang
        FROM PHIEU_KHO p
        WHERE p.MaPhieuKho = %s
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_phieu_kho,))
    row = cursor.fetchone()
    cursor.close()
    return row


def get_inventory_lines(conn, ma_phieu_kho: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT ct.MaPhieuKho, ct.STTDong, ct.MaDichVu, dv.TenDichVu,
               ct.SoLuong, ct.SoLuongSoSach, ct.SoLuongThucTe, ct.SoLuongChenhLech,
               CAST(ct.DonGiaVon AS SIGNED) AS DonGiaVon
        FROM CHI_TIET_PHIEU_KHO ct
        JOIN DICH_VU dv ON ct.MaDichVu = dv.MaDichVu
        WHERE ct.MaPhieuKho = %s
        ORDER BY ct.STTDong ASC
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_phieu_kho,))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def insert_inventory_header(
    conn,
    ma_phieu_kho: str,
    loai_phieu: str,
    ghi_chu: Optional[str],
    ma_nhan_vien: str,
    thoi_diem: datetime,
) -> None:
    sql = """
        INSERT INTO PHIEU_KHO (
            MaPhieuKho, LoaiPhieu, TrangThaiPhieu, ThoiDiemLap,
            GhiChuLyDo, MaNhanVienLap
        ) VALUES (%s, %s, 'Nhap', %s, %s, %s)
    """
    cursor = conn.cursor()
    cursor.execute(sql, (
        ma_phieu_kho,
        loai_phieu,
        thoi_diem,
        ghi_chu,
        ma_nhan_vien,
    ))
    cursor.close()


def insert_inventory_line(
    conn,
    ma_phieu_kho: str,
    stt_dong: int,
    ma_dich_vu: str,
    so_luong: int,
    so_luong_so_sach: Optional[int],
    so_luong_thuc_te: Optional[int],
    so_luong_chenh_lech: int,
    don_gia_von: int,
) -> None:
    sql = """
        INSERT INTO CHI_TIET_PHIEU_KHO (
            MaPhieuKho, STTDong, MaDichVu, SoLuong,
            SoLuongSoSach, SoLuongThucTe, SoLuongChenhLech, DonGiaVon
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor = conn.cursor()
    cursor.execute(sql, (
        ma_phieu_kho,
        stt_dong,
        ma_dich_vu,
        so_luong,
        so_luong_so_sach,
        so_luong_thuc_te,
        so_luong_chenh_lech,
        don_gia_von,
    ))
    cursor.close()


def call_sp_ghi_so_phieu_kho(
    conn,
    ma_phieu_kho: str,
    ma_tac_nhan: str,
    thoi_diem: datetime,
) -> Tuple[str, bool]:
    cursor = conn.cursor()
    args = (
        ma_phieu_kho,
        ma_tac_nhan,
        thoi_diem,
    )
    cursor.callproc("sp_ghi_so_phieu_kho", args)
    results = consume_call_results(cursor)
    cursor.close()

    if results and results[0]:
        first_row = results[0][0]
        return first_row[0], bool(first_row[1])
    raise InternalError("Routine không trả kết quả.")

