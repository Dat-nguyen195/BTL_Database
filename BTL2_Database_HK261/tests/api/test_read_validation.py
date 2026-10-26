"""Kiểm tra validation phân trang, lọc ngày và phân quyền tài nguyên API đọc (TD-03, TD-05)."""
import json


def login_as(client, username, password="MatKhau123!"):
    """Helper đăng nhập người dùng."""
    res_csrf = client.get("/api/v1/auth/csrf")
    csrf_token = res_csrf.get_json()["data"]["CsrfToken"]
    res = client.post(
        "/api/v1/auth/login",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps({"TenDangNhap": username, "MatKhau": password}),
        content_type="application/json",
    )
    assert res.status_code == 200
    return res.get_json()["data"]["CsrfToken"]


def test_unauthenticated_read_blocked(client):
    """Chưa đăng nhập truy cập /workstations bị chặn 401 UNAUTHENTICATED."""
    res = client.get("/api/v1/workstations")
    assert res.status_code == 401
    assert res.get_json()["error"]["code"] == "UNAUTHENTICATED"


def test_pagination_invalid_page(client):
    """Tham số page=0 bị từ chối 422 INVALID_INPUT."""
    login_as(client, "admin")
    res = client.get("/api/v1/sessions?page=0")
    assert res.status_code == 422
    assert res.get_json()["error"]["code"] == "INVALID_INPUT"


def test_pagination_invalid_pagesize(client):
    """Tham số pageSize > 100 bị từ chối 422 INVALID_INPUT."""
    login_as(client, "admin")
    res = client.get("/api/v1/sessions?pageSize=150")
    assert res.status_code == 422
    assert res.get_json()["error"]["code"] == "INVALID_INPUT"


def test_date_pair_missing_one(client):
    """Chỉ truyền FromDate mà thiếu ToDate bị từ chối 422 INVALID_INPUT."""
    login_as(client, "admin")
    res = client.get("/api/v1/reports/revenue?FromDate=2026-10-01")
    assert res.status_code == 422
    assert res.get_json()["error"]["code"] == "INVALID_INPUT"


def test_date_pair_reversed(client):
    """FromDate > ToDate bị từ chối 422 INVALID_INPUT."""
    login_as(client, "admin")
    res = client.get("/api/v1/reports/revenue?FromDate=2026-10-30&ToDate=2026-10-01")
    assert res.status_code == 422
    assert res.get_json()["error"]["code"] == "INVALID_INPUT"


def test_report_forbidden_for_player(client):
    """Người chơi (player1) truy cập báo cáo quản lý bị chặn 403 FORBIDDEN."""
    login_as(client, "player1")
    res = client.get("/api/v1/reports/revenue?FromDate=2026-10-01&ToDate=2026-10-26")
    assert res.status_code == 403
    assert res.get_json()["error"]["code"] == "FORBIDDEN"


def test_cross_player_wallet_forbidden(client):
    """Người chơi truy cập ví của người chơi khác bị chặn 403 FORBIDDEN."""
    login_as(client, "player1")
    # player1 là TK02, thử truy vấn ví TK99
    res = client.get("/api/v1/wallets/TK99")
    assert res.status_code == 403
    assert res.get_json()["error"]["code"] == "FORBIDDEN"


def test_staff_can_view_player_wallet(client):
    """Thu ngân / Quản lý có quyền xem ví của người chơi."""
    login_as(client, "cashier1")
    res = client.get("/api/v1/wallets/TK02")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["data"]["MaNguoiChoi"] == "TK02"
    assert data["data"]["SoDuVi"] == 100000

