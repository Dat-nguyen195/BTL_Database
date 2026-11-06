"""Truy vấn danh mục máy trạm (Q01)."""
from typing import Any, Dict, List, Optional


def get_workstations(
    conn,
    ma_khu_vuc: Optional[str] = None,
    ma_nhom_may: Optional[str] = None,
    trang_thai: Optional[str] = None,
    sort_by: str = "MaMay",
) -> List[Dict[str, Any]]:
    # Whitelist sort field
    sort_whitelist = {
        "MaMay": "m.MaMay",
        "TenMay": "m.TenMay",
        "TrangThaiMay": "m.TrangThaiMay",
    }
    sort_column = sort_whitelist.get(sort_by, "m.MaMay")

    sql = """
        SELECT m.MaMay, m.TenMay, m.TrangThaiMay, m.ViTriHang, m.ViTriCot,
               m.MaNhomMay, nm.TenNhomMay, CAST(nm.DonGiaGioMacDinh AS SIGNED) AS DonGiaGioMacDinh,
               m.MaKhuVuc, kv.TenKhuVuc
        FROM MAY_TRAM m
        JOIN NHOM_MAY nm ON m.MaNhomMay = nm.MaNhomMay
        JOIN KHU_VUC kv ON m.MaKhuVuc = kv.MaKhuVuc
        WHERE 1=1
    """
    params = []
    if ma_khu_vuc:
        sql += " AND m.MaKhuVuc = %s"
        params.append(ma_khu_vuc)
    if ma_nhom_may:
        sql += " AND m.MaNhomMay = %s"
        params.append(ma_nhom_may)
    if trang_thai:
        sql += " AND m.TrangThaiMay = %s"
        params.append(trang_thai)

    sql += f" ORDER BY {sort_column} ASC"

    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_workstation_by_id(conn, ma_may: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT m.MaMay, m.TenMay, m.TrangThaiMay, m.ViTriHang, m.ViTriCot,
               m.MaNhomMay, nm.TenNhomMay, CAST(nm.DonGiaGioMacDinh AS SIGNED) AS DonGiaGioMacDinh,
               m.MaKhuVuc, kv.TenKhuVuc
        FROM MAY_TRAM m
        JOIN NHOM_MAY nm ON m.MaNhomMay = nm.MaNhomMay
        JOIN KHU_VUC kv ON m.MaKhuVuc = kv.MaKhuVuc
        WHERE m.MaMay = %s
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_may,))
    row = cursor.fetchone()
    cursor.close()
    return row

