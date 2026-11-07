"""Kiểm tra ba luồng đầu cuối (E2E) theo kịch bản demo D1, D2, D3 của nhóm (TD-06)."""
import json


def login(client, username, password="MatKhau123!"):
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


def test_e2e_scenario_1_workstation_session(client):
    """Kịch bản D1: Chọn máy -> Mở phiên -> Xem phí/hạn dùng -> Kết thúc phiên -> Quyết toán."""
    csrf_token = login(client, "admin")

    # 1. Xem danh sách máy trạm
    res_m = client.get("/api/v1/workstations")
    assert res_m.status_code == 200
    machines = res_m.get_json()["data"]
    assert len(machines) > 0
    machine_id = machines[0]["MaMay"]

    # 2. Mở phiên sử dụng
    res_open = client.post(
        "/api/v1/sessions",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps({
            "MaPhien": "P_E2E_01",
            "MaMay": machine_id,
            "MaNguoiChoi": "TK02",
            "HinhThucDangNhap": "TraTruoc",
            "TienNapTruoc": 0,
        }),
        content_type="application/json",
    )
    assert res_open.status_code == 201
    s_data = res_open.get_json()["data"]
    assert s_data["MaPhien"] == "P_E2E_01"
    assert "CanUseUntil" in s_data

    # 3. Xem chi tiết phiên đang chạy
    res_detail = client.get("/api/v1/sessions/P_E2E_01")
    assert res_detail.status_code == 200
    assert res_detail.get_json()["data"]["TrangThaiPhien"] == "DangHoatDong"

    # 4. Kết thúc phiên
    res_close = client.post(
        "/api/v1/sessions/P_E2E_01/close",
        headers={"X-CSRF-Token": csrf_token},
        data=json.dumps({
            "HinhThucThanhToan": "TruVi",
            "TienNhan": 0,
        }),
        content_type="application/json",
    )
    assert res_close.status_code == 200
    assert res_close.get_json()["data"]["TrangThaiPhien"] == "DaKetThuc"


def test_e2e_scenario_2_wallet_and_order(client):
    """Kịch bản D2: Nạp ví có MaYeuCau -> Đặt đơn dịch vụ -> Tiếp nhận -> Thanh toán ví."""
    csrf_cashier = login(client, "cashier1")

    # 1. Nạp ví
    req_uuid = "nap:550e8400-e29b-41d4-a716-446655440001"
    res_topup = client.post(
        "/api/v1/wallet/topups",
        headers={"X-CSRF-Token": csrf_cashier},
        data=json.dumps({
            "MaGiaoDich": "G_E2E_01",
            "MaYeuCau": req_uuid,
            "MaNguoiChoi": "TK02",
            "SoTien": 100000,
            "PhuongThucGD": "TienMat",
        }),
        content_type="application/json",
    )
    assert res_topup.status_code == 201

    # 2. Mở phiên cho người chơi TK02
    client.post(
        "/api/v1/sessions",
        headers={"X-CSRF-Token": csrf_cashier},
        data=json.dumps({
            "MaPhien": "P_E2E_02",
            "MaMay": "M01",
            "MaNguoiChoi": "TK02",
            "HinhThucDangNhap": "TraSau",
            "TienNapTruoc": 0,
        }),
        content_type="application/json",
    )

    # 3. Tạo đơn hàng nháp (chụp giá server)
    res_order = client.post(
        "/api/v1/orders",
        headers={"X-CSRF-Token": csrf_cashier},
        data=json.dumps({
            "MaDonHang": "O_E2E_01",
            "KenhDat": "TaiMay",
            "MaPhien": "P_E2E_02",
            "Lines": [
                {"MaDichVu": "DV01", "SoLuong": 2},
            ],
        }),
        content_type="application/json",
    )
    assert res_order.status_code == 201
    assert res_order.get_json()["data"]["TongTien"] == 30000

    # 4. Tiếp nhận đơn hàng (trừ kho 1 lần duy nhất)
    res_accept = client.post(
        "/api/v1/orders/O_E2E_01/accept",
        headers={"X-CSRF-Token": csrf_cashier},
        data=json.dumps({}),
        content_type="application/json",
    )
    assert res_accept.status_code == 200
    assert res_accept.get_json()["data"]["TrangThaiPhucVu"] == "DaTiepNhan"

    # 5. Thanh toán đơn hàng qua ví (TruVi)
    res_pay = client.post(
        "/api/v1/orders/O_E2E_01/pay",
        headers={"X-CSRF-Token": csrf_cashier},
        data=json.dumps({"HinhThucThanhToan": "TruVi"}),
        content_type="application/json",
    )
    assert res_pay.status_code == 200
    assert res_pay.get_json()["data"]["TrangThaiThanhToan"] == "DaThanhToan"


def test_e2e_scenario_3_inventory_and_reports(client):
    """Kịch bản D3: Tạo phiếu kho -> Ghi sổ -> Xem báo cáo tồn và doanh thu (không cộng nạp ví)."""
    csrf_mgr = login(client, "admin")

    # 1. Tạo phiếu kho nhập
    res_doc = client.post(
        "/api/v1/inventory-documents",
        headers={"X-CSRF-Token": csrf_mgr},
        data=json.dumps({
            "MaPhieuKho": "PK_E2E_01",
            "LoaiPhieu": "NhapKho",
            "GhiChuLyDo": "Nhap bo sung kho",
            "Lines": [
                {"MaDichVu": "DV01", "SoLuong": 20, "DonGiaVon": 10000},
            ],
        }),
        content_type="application/json",
    )
    assert res_doc.status_code == 201

    # 2. Ghi sổ phiếu kho
    res_post = client.post(
        "/api/v1/inventory-documents/PK_E2E_01/post",
        headers={"X-CSRF-Token": csrf_mgr},
        data=json.dumps({}),
        content_type="application/json",
    )
    assert res_post.status_code == 200
    assert res_post.get_json()["data"]["TrangThaiPhieu"] == "DaGhiSo"

    # 3. Xem báo cáo tồn kho Q06
    res_stock = client.get("/api/v1/reports/stock?Threshold=100")
    assert res_stock.status_code == 200
    assert len(res_stock.get_json()["data"]) > 0

    # 4. Xem báo cáo doanh thu Q05 (loại trừ nạp ví)
    res_rev = client.get("/api/v1/reports/revenue?FromDate=2026-10-01&ToDate=2026-10-31")
    assert res_rev.status_code == 200
    rev_data = res_rev.get_json()["data"]
    # Kiểm tra không có bút toán NapTien trong báo cáo doanh thu
    for item in rev_data["ChiTiet"]:
        assert item["LoaiDoanhThu"] in ("TienGio", "DichVu")

