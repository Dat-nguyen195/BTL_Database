"""Truy vấn người dùng và xác định vai trò thực tế từ CSDL."""
from typing import Any, Dict, List, Optional


def get_user_by_username(conn, username: str) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT MaTaiKhoan, TenDangNhap, MatKhauBam, Ho, TenDem, Ten, TrangThai, MaNhomND
        FROM TAI_KHOAN
        WHERE TenDangNhap = %s
    """
    cursor.execute(sql, (username,))
    row = cursor.fetchone()
    cursor.close()
    return row


def get_user_by_id(conn, user_id: str) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT MaTaiKhoan, TenDangNhap, MatKhauBam, Ho, TenDem, Ten, TrangThai, MaNhomND
        FROM TAI_KHOAN
        WHERE MaTaiKhoan = %s
    """
    cursor.execute(sql, (user_id,))
    row = cursor.fetchone()
    cursor.close()
    return row


def get_user_roles(conn, user_id: str) -> List[str]:
    """Lấy danh sách vai trò từ quan hệ NGUOI_CHOI và NHAN_VIEN.ChucVu.
    Không suy quyền từ NHOM_NGUOI_DUNG theo KT-09.
    """
    roles = []
    cursor = conn.cursor()

    # Kiểm tra người chơi
    cursor.execute("SELECT 1 FROM NGUOI_CHOI WHERE MaTaiKhoan = %s LIMIT 1", (user_id,))
    if cursor.fetchone():
        roles.append("NguoiChoi")

    # Kiểm tra nhân viên và chức vụ
    cursor.execute("SELECT ChucVu FROM NHAN_VIEN WHERE MaTaiKhoan = %s LIMIT 1", (user_id,))
    nv_row = cursor.fetchone()
    if nv_row:
        roles.append("NhanVien")
        chuc_vu = nv_row[0]
        if chuc_vu in ("ThuNgan", "PhaChe", "QuanLy"):
            roles.append(chuc_vu)

    cursor.close()
    return roles

