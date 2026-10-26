"""Review probes: assertions describe required behavior; failures reproduce findings."""
from datetime import datetime, timedelta
from src import clock
from tests_helpers import login_as, post


def test_old_order_must_reserve_current_session_hour_fee(client, monkeypatch):
    at = datetime(2026, 10, 26, 12, 0, 0)
    monkeypatch.setattr(clock, 'now', lambda: at)
    admin = login_as(client)
    r = post(client, '/sessions', admin, {'MaPhien':'P_OLD','MaMay':'M01','MaNguoiChoi':'TK02','HinhThucDangNhap':'MienPhi','TienNapTruoc':0})
    assert r.status_code == 201, r.json
    r = post(client, '/orders', admin, {'MaDonHang':'O_OLD','KenhDat':'TaiMay','MaPhien':'P_OLD','Lines':[{'MaDichVu':'DV01','SoLuong':1}]})
    assert r.status_code == 201, r.json
    assert post(client, '/orders/O_OLD/accept', admin, {}).status_code == 200
    assert post(client, '/sessions/P_OLD/close', admin, {'HinhThucThanhToan':'MienPhi','TienNhan':0}).status_code == 200
    r = post(client, '/sessions', admin, {'MaPhien':'P_NEW','MaMay':'M01','MaNguoiChoi':'TK02','HinhThucDangNhap':'TraTruoc','TienNapTruoc':0})
    assert r.status_code == 201, r.json
    at += timedelta(hours=6)
    player = login_as(client, 'player1')
    before = client.get('/api/v1/wallets/TK02').json['data']
    r = post(client, '/orders/O_OLD/pay', player, {'HinhThucThanhToan':'TruVi'})
    after = client.get('/api/v1/wallets/TK02').json['data']
    print('OLD_ORDER_RESERVATION', {'before':before,'payment_status':r.status_code,'payment':r.json,'after':after})
    assert r.status_code == 409 and r.json['error']['code']=='INSUFFICIENT_FUNDS'
    assert after['SoDuVi'] == before['SoDuVi']


def test_inventory_replay_changed_type_returns_conflict(client):
    token = login_as(client)
    r = post(client, '/inventory-documents', token, {'MaPhieuKho':'K_REVIEW','LoaiPhieu':'NhapKho','Lines':[{'MaDichVu':'DV01','SoLuong':1,'DonGiaVon':1000}]})
    assert r.status_code == 201, r.json
    r = post(client, '/inventory-documents', token, {'MaPhieuKho':'K_REVIEW','LoaiPhieu':'KiemKe','Lines':[{'MaDichVu':'DV01','SoLuongThucTe':50,'DonGiaVon':1000}]})
    print('INVENTORY_TYPE_REPLAY', r.status_code, r.json)
    assert r.status_code == 409 and r.json['error']['code']=='IDEMPOTENCY_CONFLICT'


def test_pagination_overflow_returns_input_error(client):
    login_as(client)
    r=client.get('/api/v1/orders?page=100000000000000000000&pageSize=20')
    print('PAGINATION_OVERFLOW', r.status_code, r.json)
    assert r.status_code == 422 and r.json['error']['code']=='INVALID_INPUT'
