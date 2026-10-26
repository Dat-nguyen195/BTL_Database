"""Kiểm tra 8 API ghi, kiểm soát nghiệp vụ, chống gửi lặp (replay) và xung đột (TD-04, TD-11)."""
import json


def login_as(client, username, password="MatKhau123!"):
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


def test_open_session_and_replay(client):
    """Mở phiên sử dụng thành công (201) và replay cùng mã/nội dung trả 200 replayed=true."""
    csrf_token = login_as(client, "admin")

    payload = {
        "MaPhien": "P001",
        "MaMay": "M01",
        "MaNguoiChoi": "TK02",
        "HinhThucDangNhap": "TraTruoc",
        "TienNapTruoc": 0,
    }

    # 1. Mở lần đầu: 201 Created, replayed = False
    res1 = client.post(
        "/api/v1/sessions",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res1.status_code == 201
    data1 = res1.get_json()
    assert data1["ok"] is True
    assert data1["meta"]["replayed"] is False
    assert data1["data"]["MaPhien"] == "P001"

    # 2. Gửi lại y hệt: 200 OK, replayed = True (chống gửi lặp)
    res2 = client.post(
        "/api/v1/sessions",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2["ok"] is True
    assert data2["meta"]["replayed"] is True

    # 3. Gửi cùng MaPhien nhưng đổi số tiền -> 409 IDEMPOTENCY_CONFLICT
    conflict_payload = dict(payload, MaMay="M02")
    res3 = client.post(
        "/api/v1/sessions",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps(conflict_payload),
        content_type="application/json",
    )
    assert res3.status_code == 409
    assert res3.get_json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"


def test_topup_and_replay(client):
    """Nạp ví với MaYeuCau nap:{UUID}: 201 lần đầu, 200 khi gửi lại, 409 khi đổi số tiền."""
    csrf_token = login_as(client, "cashier1")

    payload = {
        "MaGiaoDich": "G001",
        "MaYeuCau": "nap:550e8400-e29b-41d4-a716-446655440000",
        "MaNguoiChoi": "TK02",
        "SoTien": 50000,
        "PhuongThucGD": "TienMat",
    }

    # 1. Nạp lần đầu
    res1 = client.post(
        "/api/v1/wallet/topups",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res1.status_code == 201
    data1 = res1.get_json()
    assert data1["ok"] is True
    assert data1["meta"]["replayed"] is False

    # 2. Replay
    res2 = client.post(
        "/api/v1/wallet/topups",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2["ok"] is True
    assert data2["meta"]["replayed"] is True

    # 3. Đổi số tiền trên cùng MaYeuCau -> 409
    res3 = client.post(
        "/api/v1/wallet/topups",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps(dict(payload, SoTien=200000)),
        content_type="application/json",
    )
    assert res3.status_code == 409
    assert res3.get_json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"


def test_order_atomic_creation_and_lines_validation(client):
    """Tạo đơn hàng nháp: kiểm tra trùng lặp món trong Lines, tính tổng server, replay."""
    csrf_token = login_as(client, "admin")

    # Mở phiên trước để gắn đơn TaiMay
    client.post(
        "/api/v1/sessions",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps({
            "MaPhien": "P002",
            "MaMay": "M01",
            "MaNguoiChoi": "TK02",
            "HinhThucDangNhap": "TraSau",
            "TienNapTruoc": 0,
        }),
        content_type="application/json",
    )

    # 1. Đơn có món bị lặp trong Lines bị từ chối 422 INVALID_INPUT
    dup_payload = {
        "MaDonHang": "O001",
        "KenhDat": "TaiMay",
        "MaPhien": "P002",
        "Lines": [
            {"MaDichVu": "DV01", "SoLuong": 2},
            {"MaDichVu": "DV01", "SoLuong": 1},
        ],
    }
    res_dup = client.post(
        "/api/v1/orders",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps(dup_payload),
        content_type="application/json",
    )
    assert res_dup.status_code == 422
    assert res_dup.get_json()["error"]["code"] == "INVALID_INPUT"

    # 2. Đơn hợp lệ: 201 Created, tổng tiền chụp từ giá DB: (2 * 15000) + (1 * 12000) = 42000
    valid_payload = {
        "MaDonHang": "O001",
        "KenhDat": "TaiMay",
        "MaPhien": "P002",
        "Lines": [
            {"MaDichVu": "DV01", "SoLuong": 2},
            {"MaDichVu": "DV02", "SoLuong": 1},
        ],
    }
    res_ok = client.post(
        "/api/v1/orders",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    assert res_ok.status_code == 201
    data_ok = res_ok.get_json()
    assert data_ok["ok"] is True
    assert data_ok["data"]["TongTien"] == 42000
    assert len(data_ok["data"]["Lines"]) == 2

    # 3. Replay cùng mã và lines -> 200 replayed=true
    res_rep = client.post(
        "/api/v1/orders",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    assert res_rep.status_code == 200
    assert res_rep.get_json()["meta"]["replayed"] is True


def test_inventory_document_kiem_ke(client):
    """Tạo phiếu kiểm kê chụp số lượng sổ sách từ DB và tính chênh lệch."""
    csrf_token = login_as(client, "admin")

    payload = {
        "MaPhieuKho": "PK001",
        "LoaiPhieu": "KiemKe",
        "GhiChuLyDo": "Kiem ke dinh ky thang 10",
        "Lines": [
            {"MaDichVu": "DV01", "SoLuongThucTe": 48, "DonGiaVon": 10000},
        ],
    }

    res = client.post(
        "/api/v1/inventory-documents",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["ok"] is True
    line = data["data"]["Lines"][0]
    assert line["STTDong"] == 1
    assert line["SoLuongSoSach"] == 50  # Tồn ban đầu của DV01 trong seed mock
    assert line["SoLuongThucTe"] == 48
    assert line["SoLuongChenhLech"] == -2

