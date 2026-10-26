"""Nghiệp vụ xác thực, đăng nhập và phân quyền theo TD-09."""
import unicodedata
from typing import Any, Dict
from flask import session
from werkzeug.security import check_password_hash
from src.auth import rotate_csrf_token
from src.db import get_db_connection
from src.errors import (
    AccountInactiveError,
    AppError,
    InvalidInputError,
    UnauthenticatedError,
)
from src.repositories import user_repo


def normalize_username(username: str) -> str:
    """Chuẩn hóa tên đăng nhập: trim và Unicode NFC theo KT-03."""
    if not username:
        return ""
    trimmed = username.strip()
    return unicodedata.normalize("NFC", trimmed)


def login_user(username: str, password: str) -> Dict[str, Any]:
    """Xác thực đăng nhập người dùng:
    - Chuẩn hóa tên đăng nhập
    - Kiểm tra mật khẩu băm bằng Werkzeug
    - Chỉ cho phép tài khoản trạng thái HoatDong
    - Đổi session và CSRF token
    """
    if not username or not password:
        raise InvalidInputError("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")

    from src.validation import text
    text(username, "TenDangNhap", 50)
    text(password, "MatKhau", 1024)
    norm_user = normalize_username(username)
    conn = get_db_connection()
    try:
        user = user_repo.get_user_by_username(conn, norm_user)
        if not user:
            raise UnauthenticatedError("Tên đăng nhập hoặc mật khẩu không chính xác.")

        # Kiểm tra trạng thái tài khoản
        if user["TrangThai"] != "HoatDong":
            raise AccountInactiveError("Tài khoản đang bị khóa hoặc tạm dừng.")

        # Kiểm tra mật khẩu băm bằng Werkzeug
        hash_val = user.get("MatKhauBam") or ""
        try:
            pw_ok = check_password_hash(hash_val, password)
        except (ValueError, TypeError):
            pw_ok = False

        if not pw_ok:
            raise UnauthenticatedError("Tên đăng nhập hoặc mật khẩu không chính xác.")

        # Lấy vai trò thực tế từ DB
        roles = user_repo.get_user_roles(conn, user["MaTaiKhoan"])

        # Tạo tên đầy đủ
        ho_ten_parts = [user.get("Ho"), user.get("TenDem"), user.get("Ten")]
        full_name = " ".join([p for p in ho_ten_parts if p]) or user["TenDangNhap"]

        # Làm mới session và CSRF token sau đăng nhập thành công
        session.clear()
        session["user_id"] = user["MaTaiKhoan"]
        session["username"] = user["TenDangNhap"]
        session["full_name"] = full_name
        session["roles"] = roles
        csrf_token = rotate_csrf_token()

        return {
            "MaTaiKhoan": user["MaTaiKhoan"],
            "TenDangNhap": user["TenDangNhap"],
            "HoTen": full_name,
            "roles": roles,
            "CsrfToken": csrf_token,
        }
    finally:
        conn.close()


def get_current_user_profile() -> Dict[str, Any]:
    """Lấy thông tin và quyền hạn người dùng hiện tại từ session."""
    user_id = session.get("user_id")
    if not user_id:
        raise UnauthenticatedError("Chưa đăng nhập.")

    conn = get_db_connection()
    try:
        user = user_repo.get_user_by_id(conn, user_id)
        if not user or user["TrangThai"] != "HoatDong":
            session.clear()
            raise AccountInactiveError("Tài khoản không còn hoạt động.")

        roles = user_repo.get_user_roles(conn, user_id)
        ho_ten_parts = [user.get("Ho"), user.get("TenDem"), user.get("Ten")]
        full_name = " ".join([p for p in ho_ten_parts if p]) or user["TenDangNhap"]

        return {
            "MaTaiKhoan": user["MaTaiKhoan"],
            "TenDangNhap": user["TenDangNhap"],
            "HoTen": full_name,
            "roles": roles,
            "CsrfToken": session.get("_csrf_token"),
        }
    finally:
        conn.close()


def logout_user() -> None:
    """Xóa hoàn toàn session người dùng."""
    session.clear()

