"""Current database identity, CSRF and per-resource authorization."""
import secrets
from functools import wraps
from flask import g, request, session, has_request_context
from src.errors import AccountInactiveError, CsrfInvalidError, ForbiddenError, UnauthenticatedError

SYSTEM_ACTOR = object()  # Only internal worker/service code can pass this capability.

def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(24)
    return session["_csrf_token"]

def rotate_csrf_token():
    session["_csrf_token"] = secrets.token_hex(24)
    return session["_csrf_token"]

def load_identity(conn, user_id):
    from src.repositories import user_repo
    user = user_repo.get_user_by_id(conn, user_id)
    if not user:
        raise UnauthenticatedError()
    if user["TrangThai"] != "HoatDong":
        raise AccountInactiveError()
    return {
        "MaTaiKhoan": user_id,
        "TenDangNhap": user["TenDangNhap"],
        "HoTen": " ".join(x for x in (user.get("Ho"), user.get("TenDem"), user.get("Ten")) if x),
        "roles": user_repo.get_user_roles(conn, user_id),
    }

def transaction_identity(conn, actor):
    # Revalidate using the SAME connection as the write, never cookie roles.
    if not isinstance(actor, dict) or not actor.get("MaTaiKhoan"):
        raise UnauthenticatedError()
    return load_identity(conn, actor["MaTaiKhoan"])

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    if not hasattr(g, "current_user"):
        from src.db import get_db_connection
        conn = get_db_connection()
        try:
            g.current_user = load_identity(conn, user_id)
        except (AccountInactiveError, UnauthenticatedError):
            session.clear()
            raise
        finally:
            conn.close()
    return g.current_user

def verify_csrf():
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        token, expected = request.headers.get("X-CSRF-Token"), session.get("_csrf_token")
        if not token or not expected or not secrets.compare_digest(token, expected):
            raise CsrfInvalidError()

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not get_current_user():
            raise UnauthenticatedError()
        return f(*args, **kwargs)
    return wrapped

def require_roles(user, *roles):
    if not any(role in user.get("roles", ()) for role in roles):
        raise ForbiddenError()

def roles_required(*roles):
    def decorate(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if not user:
                raise UnauthenticatedError()
            require_roles(user, *roles)
            return f(*args, **kwargs)
        return wrapped
    return decorate

def resource_access(user, owner_id, staff_roles=("ThuNgan", "QuanLy")):
    if any(role in user.get("roles", ()) for role in staff_roles):
        return
    if owner_id and owner_id == user["MaTaiKhoan"] and "NguoiChoi" in user.get("roles", ()):
        return
    raise ForbiddenError()

def check_resource_access(owner_id, staff_roles=("ThuNgan", "QuanLy")):
    user = get_current_user()
    if not user:
        raise UnauthenticatedError()
    resource_access(user, owner_id, staff_roles)
