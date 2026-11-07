"""Truy vấn danh mục dịch vụ món ăn / đồ uống / dịch vụ net."""
from typing import Any, Dict, List, Optional


def get_services(
    conn,
    ma_nhom_dv: Optional[str] = None,
    trang_thai: Optional[str] = None,
    sort_by: str = "MaDichVu",
) -> List[Dict[str, Any]]:
    sort_whitelist = {
        "MaDichVu": "dv.MaDichVu",
        "TenDichVu": "dv.TenDichVu",
        "GiaBanHienHanh": "dv.GiaBanHienHanh",
    }
    sort_column = sort_whitelist.get(sort_by, "dv.MaDichVu")

    sql = """
        SELECT dv.MaDichVu, dv.TenDichVu,
               CAST(dv.GiaBanHienHanh AS SIGNED) AS GiaBanHienHanh,
               dv.SoLuongTon, dv.TrangThaiKinhDoanh,
               dv.MaNhomDV, ndv.TenNhomDV,
               dv.MaDonVi, dvt.TenDonVi,
               dv.MaMayIn
        FROM DICH_VU dv
        JOIN NHOM_DICH_VU ndv ON dv.MaNhomDV = ndv.MaNhomDV
        JOIN DON_VI_TINH dvt ON dv.MaDonVi = dvt.MaDonVi
        WHERE 1=1
    """
    params = []
    if ma_nhom_dv:
        sql += " AND dv.MaNhomDV = %s"
        params.append(ma_nhom_dv)
    if trang_thai:
        sql += " AND dv.TrangThaiKinhDoanh = %s"
        params.append(trang_thai)

    sql += f" ORDER BY {sort_column} ASC"

    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_service_by_id(conn, ma_dich_vu: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT dv.MaDichVu, dv.TenDichVu,
               CAST(dv.GiaBanHienHanh AS SIGNED) AS GiaBanHienHanh,
               dv.SoLuongTon, dv.TrangThaiKinhDoanh,
               dv.MaNhomDV, ndv.TenNhomDV,
               dv.MaDonVi, dvt.TenDonVi,
               dv.MaMayIn
        FROM DICH_VU dv
        JOIN NHOM_DICH_VU ndv ON dv.MaNhomDV = ndv.MaNhomDV
        JOIN DON_VI_TINH dvt ON dv.MaDonVi = dvt.MaDonVi
        WHERE dv.MaDichVu = %s
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ma_dich_vu,))
    row = cursor.fetchone()
    cursor.close()
    return row


def get_services_by_ids_for_update(conn, service_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    from src.repositories.core import lock_row
    result={}
    for key in sorted(set(service_ids)):
        row=lock_row(conn,'DICH_VU',key)
        if row:
            result[key]=row
    return result
