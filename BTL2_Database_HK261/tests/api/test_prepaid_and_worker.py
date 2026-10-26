"""Math plus actual DB settlement timestamps, budget and late topup regression tests."""
from datetime import timedelta
from src import clock
from src.services.session_service import calculate_max_seconds,calculate_can_use_until,calculate_fee
from src.services.worker import scan_and_terminate_expired_sessions
from tests_helpers import login_as

def test_integer_arithmetic_formula_properties():
    for rate in [1,8000,10000,12000,15000,20000,25000]:
        for budget in [0,500,7500,15000,50000,100000]:
            seconds=calculate_max_seconds(budget,rate)
            assert seconds*rate//3600<=budget
            assert (seconds+1)*rate//3600>budget

def test_free_session_no_money_limit():
    assert calculate_max_seconds(0,0) is None

def test_can_use_until_format():
    start=clock.as_datetime('2026-10-26 08:00:00')
    assert calculate_can_use_until(start,15000,15000)=='2026-10-26T09:00:00+07:00'

def test_worker_closes_at_deadline_not_scan_time(client,sql):
    token=login_as(client,'admin')
    headers={'X-CSRF-Token':token}
    response=client.post('/api/v1/sessions',headers=headers,json={'MaPhien':'P_EXPIRED','MaMay':'M01','MaNguoiChoi':'TK02','HinhThucDangNhap':'TraTruoc','TienNapTruoc':0})
    assert response.status_code==201
    start=clock.now()-timedelta(hours=3)
    sql('UPDATE PHIEN_SU_DUNG SET ThoiDiemBatDau=%s WHERE MaPhien=%s',(start,'P_EXPIRED'))
    sql('UPDATE NGUOI_CHOI SET SoDuVi=15000 WHERE MaTaiKhoan=%s',('TK02',))
    assert scan_and_terminate_expired_sessions()==['P_EXPIRED']
    session=sql('SELECT * FROM PHIEN_SU_DUNG WHERE MaPhien=%s',('P_EXPIRED',))[0]
    receipt=sql('SELECT * FROM BIEN_LAI_TIEN_MAY WHERE MaPhien=%s',('P_EXPIRED',))[0]
    assert session['ThoiDiemKetThuc']==start+timedelta(hours=1)
    assert receipt['TongTienGio']==15000
    assert receipt['MaNhanVienThu'] is None
    assert sql('SELECT SoDuVi FROM NGUOI_CHOI WHERE MaTaiKhoan=%s',('TK02',))[0]['SoDuVi']==0
    assert scan_and_terminate_expired_sessions()==[]
