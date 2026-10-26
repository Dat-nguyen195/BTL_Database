"""Kiểm tra API Xác thực, CSRF và phân quyền theo TD-09."""
import json


def get_csrf(client):
    """Helper lấy CSRF token và cookie session."""
    res = client.get("/api/v1/auth/csrf")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    return data["data"]["CsrfToken"]


def test_csrf_generation(client):
    """GET /auth/csrf cấp token hợp lệ và thiết lập cookie session."""
    csrf_token = get_csrf(client)
    assert isinstance(csrf_token, str)
    assert len(csrf_token) == 48


def test_login_missing_csrf(client):
    """POST /auth/login không có header X-CSRF-Token bị từ chối 403 CSRF_INVALID."""
    res = client.post(
        "/api/v1/auth/login",
        data=json.dumps({"TenDangNhap": "admin", "MatKhau": "MatKhau123!"}),
        content_type="application/json",
    )
    assert res.status_code == 403
    data = res.get_json()
    assert data["ok"] is False
    assert data["error"]["code"] == "CSRF_INVALID"


def test_login_wrong_password(client):
    """POST /auth/login sai mật khẩu trả về 401 UNAUTHENTICATED."""
    csrf_token = get_csrf(client)
    res = client.post(
        "/api/v1/auth/login",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps({"TenDangNhap": "admin", "MatKhau": "SaiMatKhau"}),
        content_type="application/json",
    )
    assert res.status_code == 401
    data = res.get_json()
    assert data["ok"] is False
    assert data["error"]["code"] == "UNAUTHENTICATED"


def test_login_locked_account(client):
    """POST /auth/login tài khoản trạng thái Khoa bị từ chối 403 ACCOUNT_INACTIVE."""
    csrf_token = get_csrf(client)
    res = client.post(
        "/api/v1/auth/login",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps({"TenDangNhap": "locked_user", "MatKhau": "MatKhau123!"}),
        content_type="application/json",
    )
    assert res.status_code == 403
    data = res.get_json()
    assert data["ok"] is False
    assert data["error"]["code"] == "ACCOUNT_INACTIVE"


def test_login_success_and_me(client):
    """POST /auth/login thành công, đổi token CSRF, truy vấn được GET /auth/me."""
    csrf_token = get_csrf(client)
    res = client.post(
        "/api/v1/auth/login",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps({"TenDangNhap": "admin", "MatKhau": "MatKhau123!"}),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["data"]["TenDangNhap"] == "admin"
    assert "QuanLy" in data["data"]["roles"]
    new_csrf = data["data"]["CsrfToken"]
    assert new_csrf != csrf_token

    # Kiểm tra GET /auth/me
    res_me = client.get("/api/v1/auth/me")
    assert res_me.status_code == 200
    me_data = res_me.get_json()
    assert me_data["ok"] is True
    assert me_data["data"]["MaTaiKhoan"] == "TK01"


def test_logout(client):
    """POST /auth/logout xóa session thành công."""
    csrf_token = get_csrf(client)
    client.post(
        "/api/v1/auth/login",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps({"TenDangNhap": "player1", "MatKhau": "MatKhau123!"}),
        content_type="application/json",
    )

    res_me = client.get("/api/v1/auth/me")
    assert res_me.status_code == 200

    new_csrf = res_me.get_json()["data"]["CsrfToken"]
    res_logout = client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": new_csrf},
    )
    assert res_logout.status_code == 200
    assert res_logout.get_json()["ok"] is True

    # Sau khi logout, truy vấn /auth/me bị 401
    res_me_after = client.get("/api/v1/auth/me")
    assert res_me_after.status_code == 401

