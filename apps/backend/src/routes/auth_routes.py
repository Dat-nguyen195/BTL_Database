"""Các endpoint xác thực danh tính: /auth/csrf, /auth/login, /auth/me, /auth/logout."""
import uuid
from flask import Blueprint, g, request
from src.auth import generate_csrf_token, login_required, verify_csrf
from src.errors import BadJsonError, make_success_response
from src.services import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/csrf", methods=["GET"])
def get_csrf():
    """GET /api/v1/auth/csrf: Lấy CSRF token cho session."""
    token = generate_csrf_token()
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response({"CsrfToken": token}, request_id=req_id)


@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/v1/auth/login: Đăng nhập tài khoản, đổi session và cấp CSRF token mới."""
    verify_csrf()

    if not request.is_json:
        raise BadJsonError("Content-Type phải là application/json.")

    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise BadJsonError("JSON body không hợp lệ.")

    from src.validation import fields
    fields(body, {"TenDangNhap", "MatKhau"}, {"TenDangNhap", "MatKhau"})
    username = body.get("TenDangNhap")
    password = body.get("MatKhau")

    user_info = auth_service.login_user(username, password)
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(user_info, request_id=req_id)


@auth_bp.route("/me", methods=["GET"])
@login_required
def get_me():
    """GET /api/v1/auth/me: Lấy thông tin danh tính và vai trò người dùng hiện tại."""
    profile = auth_service.get_current_user_profile()
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(profile, request_id=req_id)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """POST /api/v1/auth/logout: Đăng xuất và xóa session."""
    verify_csrf()
    auth_service.logout_user()
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response({}, request_id=req_id)

