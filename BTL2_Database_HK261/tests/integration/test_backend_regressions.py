"""Regression coverage for review R01–R16 using actual MySQL and restricted runtime grants."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from uuid import uuid4
from unittest.mock import MagicMock
import pytest
import mysql.connector
from src import clock
from src.app import create_app
from src.config import Config
from src.db import get_db_connection
from src.errors import InvalidInputError
from src.repositories.core import lock_row
from src.services import transaction, order_service
from src.services.worker import scan_and_terminate_expired_sessions
from tests_helpers import login_as, post


def open_member(client,token,key='P_TEST',owner='TK02',machine='M01',kind='TraTruoc'):
    result=post(client,'/sessions',token,{'MaPhien':key,'MaMay':machine,'MaNguoiChoi':owner,'HinhThucDangNhap':kind,'TienNapTruoc':0})
    assert result.status_code==201,result.json
    return result.json['data']


def order(client,token,key='O_TEST',qty=1,session=None):
    result=post(client,'/orders',token,{'MaDonHang':key,'KenhDat':'TaiMay' if session else 'TaiQuay','MaPhien':session,'Lines':[{'MaDichVu':'DV01','SoLuong':qty}]})
    assert result.status_code==201,result.json
    return result.json['data']


def topup_body(key='G_TEST',amount=10000):
    return {'MaGiaoDich':key,'MaYeuCau':'nap:'+str(uuid4()),'MaNguoiChoi':'TK02','SoTien':amount,'PhuongThucGD':'TienMat'}


def test_secret_is_required(monkeypatch):
    monkeypatch.setattr(Config,'SECRET_KEY','')
    with pytest.raises(RuntimeError):create_app()


@pytest.mark.parametrize('status',['Khoa','TamDung'])
def test_account_revocation_applies_next_request(client,sql,status):
    login_as(client)
    sql('UPDATE TAI_KHOAN SET TrangThai=%s WHERE MaTaiKhoan=%s',(status,'TK01'))
    result=client.get('/api/v1/inventory-documents')
    assert result.status_code==403
    assert result.json['error']['code']=='ACCOUNT_INACTIVE'


def test_role_revocation_and_dual_roles(client,sql):
    login_as(client,'dual_user')
    me=client.get('/api/v1/auth/me').json['data']
    assert {'NguoiChoi','ThuNgan'}<=set(me['roles'])
    sql("UPDATE NHAN_VIEN SET ChucVu='PhaChe' WHERE MaTaiKhoan='TK06'")
    assert client.get('/api/v1/inventory-documents').status_code==403


@pytest.mark.parametrize('amount',[1.9,True,'100',-1,0,10**12])
def test_topup_rejects_noninteger_and_out_of_range(client,amount):
    token=login_as(client)
    response=post(client,'/wallet/topups',token,topup_body(amount=amount))
    assert response.status_code==422


@pytest.mark.parametrize('line',[None,1,[],{'MaDichVu':'DV01','SoLuong':True},{'MaDichVu':'DV01','SoLuong':1,'DonGiaBan':1}])
def test_invalid_order_line_returns_422(client,line):
    token=login_as(client)
    response=post(client,'/orders',token,{'MaDonHang':'O_BAD','KenhDat':'TaiQuay','Lines':[line]})
    assert response.status_code==422


def test_malformed_json_and_unknown_fields(client):
    token=login_as(client)
    response=client.post('/api/v1/orders',data='{',content_type='application/json',headers={'X-CSRF-Token':token})
    assert response.status_code==400
    assert response.json['error']['code']=='BAD_JSON'
    assert post(client,'/orders/O_BAD/accept',token,{'MaNhanVien':'TK01'}).status_code==422
    payload=topup_body();payload['SoDuVi']=10**9
    assert post(client,'/wallet/topups',token,payload).status_code==422


def test_wallet_uses_balance_not_accrued_holding(client,sql):
    token=login_as(client)
    data=open_member(client,token)
    assert clock.as_datetime(data['CanUseUntil'])-clock.as_datetime(data['ThoiDiemBatDau'])==timedelta(seconds=24000)
    assert sql("SELECT TienGiuCho FROM PHIEN_SU_DUNG WHERE MaPhien='P_TEST'")[0]['TienGiuCho']==0
    assert scan_and_terminate_expired_sessions()==[]


def test_expired_session_cannot_create_order(client,sql):
    token=login_as(client)
    open_member(client,token)
    sql("UPDATE PHIEN_SU_DUNG SET ThoiDiemBatDau=%s WHERE MaPhien='P_TEST'",(clock.now()-timedelta(days=1),))
    response=post(client,'/orders',token,{'MaDonHang':'O_EXPIRED','KenhDat':'TaiMay','MaPhien':'P_TEST','Lines':[{'MaDichVu':'DV01','SoLuong':1}]})
    assert response.status_code==409
    assert response.json['error']['code']=='PREPAID_EXPIRED'
    assert sql("SELECT COUNT(*) AS n FROM DON_GOI_DICH_VU")[0]['n']==0


def test_late_topup_settles_old_expiry_before_adding_money(client,sql):
    token=login_as(client)
    open_member(client,token)
    started=clock.now()-timedelta(hours=3)
    sql("UPDATE PHIEN_SU_DUNG SET ThoiDiemBatDau=%s WHERE MaPhien='P_TEST'",(started,))
    sql("UPDATE NGUOI_CHOI SET SoDuVi=15000 WHERE MaTaiKhoan='TK02'")
    response=post(client,'/wallet/topups',token,topup_body())
    assert response.status_code==201,response.json
    session=sql("SELECT * FROM PHIEN_SU_DUNG WHERE MaPhien='P_TEST'")[0]
    assert session['ThoiDiemKetThuc']==started+timedelta(hours=1)
    assert sql("SELECT SoDuVi FROM NGUOI_CHOI WHERE MaTaiKhoan='TK02'")[0]['SoDuVi']==10000


def test_pay_replay_enforces_owner_and_method(client,sql):
    token=login_as(client)
    open_member(client,token,kind='TraSau')
    order(client,token,session='P_TEST')
    assert post(client,'/orders/O_TEST/accept',token,{}).status_code==200
    assert post(client,'/orders/O_TEST/pay',token,{'HinhThucThanhToan':'TruVi'}).status_code==200
    assert post(client,'/orders/O_TEST/pay',token,{'HinhThucThanhToan':'TienMat'}).status_code==409
    token=login_as(client,'player2')
    assert post(client,'/orders/O_TEST/pay',token,{'HinhThucThanhToan':'TruVi'}).status_code==403


def test_replay_survives_session_close_and_new_catalog_price(client,sql):
    token=login_as(client)
    open_member(client,token,kind='TraSau')
    payload={'MaDonHang':'O_TEST','KenhDat':'TaiMay','MaPhien':'P_TEST','Lines':[{'MaDichVu':'DV01','SoLuong':1}]}
    assert post(client,'/orders',token,payload).status_code==201
    assert post(client,'/sessions/P_TEST/close',token,{'HinhThucThanhToan':'TruVi','TienNhan':0}).status_code==200
    sql("UPDATE DICH_VU SET GiaBanHienHanh=99000 WHERE MaDichVu='DV01'")
    response=post(client,'/orders',token,payload)
    assert response.status_code==200 and response.json['meta']['replayed']
    assert response.json['data']['TongTien']==15000


@pytest.mark.parametrize('change',[{'MaDichVu':'DV02'},{'SoLuong':999},{'DonGiaVon':999}])
def test_inventory_replay_compares_all_line_fields(client,change):
    token=login_as(client)
    payload={'MaPhieuKho':'K_TEST','LoaiPhieu':'NhapKho','GhiChuLyDo':'Original','Lines':[{'MaDichVu':'DV01','SoLuong':1,'DonGiaVon':10}]}
    assert post(client,'/inventory-documents',token,payload).status_code==201
    payload['Lines'][0].update(change)
    assert post(client,'/inventory-documents',token,payload).status_code==409


def test_topup_replay_checks_actor(client):
    token=login_as(client)
    payload=topup_body()
    assert post(client,'/wallet/topups',token,payload).status_code==201
    token=login_as(client,'cashier1')
    assert post(client,'/wallet/topups',token,payload).status_code==409


def test_second_line_failure_rolls_back_header_and_first_line(client,sql,monkeypatch):
    token=login_as(client)
    original=order_service.order_repo.insert_order_line
    count=0
    def fail_second(*args,**kwargs):
        nonlocal count
        count+=1
        if count==2:raise InvalidInputError('injected second-line failure')
        return original(*args,**kwargs)
    monkeypatch.setattr(order_service.order_repo,'insert_order_line',fail_second)
    response=post(client,'/orders',token,{'MaDonHang':'O_FAIL','KenhDat':'TaiQuay','Lines':[{'MaDichVu':'DV01','SoLuong':1},{'MaDichVu':'DV02','SoLuong':1}]})
    assert response.status_code==422
    assert sql('SELECT COUNT(*) AS n FROM DON_GOI_DICH_VU')[0]['n']==0
    assert sql('SELECT COUNT(*) AS n FROM CHI_TIET_GOI_DICH_VU')[0]['n']==0
    assert sql("SELECT SoLuongTon FROM DICH_VU WHERE MaDichVu='DV01'")[0]['SoLuongTon']==50


def test_accept_partial_stock_change_rolls_back_all_lines(client,sql):
    token=login_as(client)
    sql("UPDATE DICH_VU SET SoLuongTon=0 WHERE MaDichVu='DV02'")
    response=post(client,'/orders',token,{'MaDonHang':'O_STOCK','KenhDat':'TaiQuay','Lines':[{'MaDichVu':'DV01','SoLuong':1},{'MaDichVu':'DV02','SoLuong':1}]})
    assert response.status_code==201
    response=post(client,'/orders/O_STOCK/accept',token,{})
    assert response.status_code==409 and response.json['error']['code']=='INSUFFICIENT_STOCK'
    assert sql("SELECT SoLuongTon FROM DICH_VU WHERE MaDichVu='DV01'")[0]['SoLuongTon']==50
    assert sql("SELECT TrangThaiPhucVu FROM DON_GOI_DICH_VU WHERE MaDonHang='O_STOCK'")[0]['TrangThaiPhucVu']=='MoiDat'


def race_posts(app,requests):
    clients=[]
    for name,path,body in requests:
        client=app.test_client();token=login_as(client,name)
        clients.append((client,token,path,body))
    barrier=Barrier(len(clients))
    def send(item):
        c,t,p,b=item
        barrier.wait(timeout=10)
        return post(c,p,t,b)
    with ThreadPoolExecutor(max_workers=len(clients)) as pool:
        return list(pool.map(send,clients))


@pytest.mark.parametrize('same_owner',[False,True])
def test_two_connections_cannot_open_duplicate_active_session(app,sql,same_owner):
    bodies=[{'MaPhien':'P_RACE_'+str(i),'MaMay':'M01' if not same_owner else 'M0'+str(i+1),'MaNguoiChoi':'TK02' if same_owner else ('TK02' if i==0 else 'TK05'),'HinhThucDangNhap':'TraTruoc','TienNapTruoc':0} for i in range(2)]
    responses=race_posts(app,[('admin','/sessions',b) for b in bodies])
    assert sorted(r.status_code for r in responses)==[201,409]
    assert sql("SELECT COUNT(*) AS n FROM PHIEN_SU_DUNG WHERE TrangThaiPhien='DangHoatDong'")[0]['n']==1


def test_two_identical_draft_requests_replay_after_unique_conflict(app,sql):
    payload={'MaDonHang':'O_RACE','KenhDat':'TaiQuay','Lines':[{'MaDichVu':'DV01','SoLuong':1}]}
    responses=race_posts(app,[('admin','/orders',payload),('cashier1','/orders',payload)])
    assert sorted(r.status_code for r in responses)==[200,201]
    assert sum(r.json['meta']['replayed'] for r in responses)==1
    assert sql('SELECT COUNT(*) AS n FROM CHI_TIET_GOI_DICH_VU')[0]['n']==1


def test_two_orders_compete_for_last_item(app,client,sql):
    token=login_as(client)
    sql("UPDATE DICH_VU SET SoLuongTon=1 WHERE MaDichVu='DV01'")
    order(client,token,'O_A');order(client,token,'O_B')
    responses=race_posts(app,[('admin','/orders/O_A/accept',{}),('cashier1','/orders/O_B/accept',{})])
    assert sorted(r.status_code for r in responses)==[200,409]
    assert sql("SELECT SoLuongTon FROM DICH_VU WHERE MaDichVu='DV01'")[0]['SoLuongTon']==0


def test_two_debits_cannot_spend_same_balance(app,client,sql):
    token=login_as(client)
    open_member(client,token,kind='TraSau')
    for key in ['O_A','O_B']:
        order(client,token,key,qty=4,session='P_TEST')
        assert post(client,f'/orders/{key}/accept',token,{}).status_code==200
    responses=race_posts(app,[('admin','/orders/O_A/pay',{'HinhThucThanhToan':'TruVi'}),('cashier1','/orders/O_B/pay',{'HinhThucThanhToan':'TruVi'})])
    assert sorted(r.status_code for r in responses)==[200,409]
    assert sql("SELECT SoDuVi FROM NGUOI_CHOI WHERE MaTaiKhoan='TK02'")[0]['SoDuVi']==40000
    assert sql("SELECT COUNT(*) AS n FROM GIAO_DICH_VI WHERE LoaiGiaoDich='TruTienDichVu'")[0]['n']==1


def test_real_1205_rolls_back_then_retries_fresh_connection(db_conn,monkeypatch):
    db_conn.start_transaction()
    cursor=db_conn.cursor();cursor.execute("SELECT * FROM NGUOI_CHOI WHERE MaTaiKhoan='TK02' FOR UPDATE");cursor.fetchall();cursor.close()
    original=transaction.get_db_connection
    connections=[]
    def connect():
        if connections:db_conn.rollback()
        conn=original();cur=conn.cursor();cur.execute('SET innodb_lock_wait_timeout=1');cur.close()
        connections.append(conn)
        return conn
    monkeypatch.setattr(transaction,'get_db_connection',connect)
    attempts=[]
    def action(conn):
        attempts.append(conn)
        try:return lock_row(conn,'NGUOI_CHOI','TK02')['MaTaiKhoan']
        except mysql.connector.Error as error:
            assert error.errno==1205
            raise
    assert transaction.run_in_transaction(action)=='TK02'
    assert len(attempts)==2 and attempts[0] is not attempts[1]


def test_real_deadlock_retries_entire_action(db_conn):
    barrier=Barrier(2)
    observed=[]
    attempts=[0,0]
    def run(index):
        first,second=('M01','M02') if index==0 else ('M02','M01')
        def action(conn):
            attempts[index]+=1
            lock_row(conn,'MAY_TRAM',first)
            if attempts[index]==1:barrier.wait(timeout=10)
            try:lock_row(conn,'MAY_TRAM',second)
            except mysql.connector.Error as error:
                observed.append(error.errno)
                raise
            return True
        return transaction.run_in_transaction(action)
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(run,[0,1]))==[True,True]
    assert 1213 in observed
    assert sum(attempts)==3


def test_barista_can_read_but_cannot_create_counter_order(client):
    token=login_as(client)
    order(client,token)
    token=login_as(client,'barista')
    assert client.get('/api/v1/orders/O_TEST').status_code==200
    assert post(client,'/orders',token,{'MaDonHang':'O_DENIED','KenhDat':'TaiQuay','Lines':[{'MaDichVu':'DV01','SoLuong':1}]}).status_code==403
    assert post(client,'/orders/O_TEST/accept',token,{}).status_code==200


def test_q07_counts_sales_without_inventory_documents(client,sql):
    token=login_as(client)
    order(client,token,qty=2)
    assert post(client,'/orders/O_TEST/accept',token,{}).status_code==200
    today=clock.now().date().isoformat()
    result=client.get(f'/api/v1/reports/inventory-reconciliation?FromDate={today}&ToDate={today}')
    assert result.status_code==200
    row=next(x for x in result.json['data'] if x['MaDichVu']=='DV01')
    assert (row['TongBan'],row['BienDongRong'],row['TonHienTai'])==(2,-2,48)


def test_shifts_deduplicate_same_shift_and_include_overnight(client,sql):
    login_as(client)
    sql("INSERT INTO PHAN_CONG_TRUC VALUES ('TK03','CA01','KV02',NULL)")
    sql("INSERT INTO CA_TRUC VALUES ('CA_NIGHT','Ca đêm','2026-10-25 22:00:00','2026-10-26 06:00:00')")
    sql("INSERT INTO PHAN_CONG_TRUC VALUES ('TK03','CA_NIGHT','KV01',NULL)")
    result=client.get('/api/v1/reports/shifts?FromDate=2026-10-26&ToDate=2026-10-26')
    assert result.status_code==200
    rows=result.json['data']
    assert len(rows)==3
    assert not any(row['ChongGio'] for row in rows)


def test_runtime_cannot_update_wallet_or_stock(db_conn):
    conn=get_db_connection()
    try:
        with pytest.raises(mysql.connector.Error) as error:
            cursor=conn.cursor();cursor.execute("UPDATE NGUOI_CHOI SET SoDuVi=1 WHERE MaTaiKhoan='TK02'")
        assert error.value.errno==1142
    finally:
        conn.rollback();conn.close()


def test_sql_and_python_deadlines_agree_at_rounding_boundaries(sql):
    from src.services.prepaid import calculate_max_seconds
    started=clock.as_datetime('2026-10-25 23:30:00')
    for rate in [1,15000,20000,50000,9999999999]:
        for budget in [0,1,14999,19999,49999,100000]:
            actual=sql('SELECT fn_han_phien(%s,%s,%s) AS deadline',(started,budget,rate))[0]['deadline']
            assert actual==started+timedelta(seconds=calculate_max_seconds(budget,rate))


def test_guest_prepaid_uses_original_deposit_and_replays(client,sql):
    token=login_as(client)
    response=post(client,'/sessions',token,{'MaPhien':'P_GUEST','MaMay':'M01','MaNguoiChoi':None,'HinhThucDangNhap':'TraTruoc','TienNapTruoc':15000})
    assert response.status_code==201
    body={'HinhThucThanhToan':'TienMat','TienNhan':0}
    response=post(client,'/sessions/P_GUEST/close',token,body)
    assert response.status_code==200,response.json
    assert response.json['data']['BienLai']['TienNhan']==15000
    assert post(client,'/sessions/P_GUEST/close',token,body).json['meta']['replayed']
    assert post(client,'/sessions/P_GUEST/close',token,dict(body,TienNhan=100)).status_code==422
    assert sql('SELECT COUNT(*) AS n FROM GIAO_DICH_VI')[0]['n']==0


def test_free_session_creates_zero_receipt_without_wallet_transaction(client,sql):
    token=login_as(client)
    response=post(client,'/sessions',token,{'MaPhien':'P_FREE','MaMay':'M01','MaNguoiChoi':None,'HinhThucDangNhap':'MienPhi','TienNapTruoc':0})
    assert response.status_code==201
    response=post(client,'/sessions/P_FREE/close',token,{'HinhThucThanhToan':'MienPhi','TienNhan':0})
    assert response.status_code==200,response.json
    assert response.json['data']['BienLai']['TongTienGio']==0
    assert sql('SELECT COUNT(*) AS n FROM GIAO_DICH_VI')[0]['n']==0


def test_stale_inventory_snapshot_rolls_back_all_changes(client,sql):
    token=login_as(client)
    body={'MaPhieuKho':'K_STALE','LoaiPhieu':'KiemKe','Lines':[{'MaDichVu':'DV01','SoLuongThucTe':48,'DonGiaVon':10000}]}
    assert post(client,'/inventory-documents',token,body).status_code==201
    sql("UPDATE DICH_VU SET SoLuongTon=49 WHERE MaDichVu='DV01'")
    response=post(client,'/inventory-documents/K_STALE/post',token,{})
    assert response.status_code==409 and response.json['error']['code']=='INVENTORY_SNAPSHOT_STALE'
    assert sql("SELECT SoLuongTon FROM DICH_VU WHERE MaDichVu='DV01'")[0]['SoLuongTon']==49
    assert sql("SELECT TrangThaiPhieu FROM PHIEU_KHO WHERE MaPhieuKho='K_STALE'")[0]['TrangThaiPhieu']=='Nhap'


def test_holding_prevents_spending_accrued_hour_fee(client,sql):
    token=login_as(client)
    open_member(client,token)
    sql("UPDATE PHIEN_SU_DUNG SET ThoiDiemBatDau=%s WHERE MaPhien='P_TEST'",(clock.now()-timedelta(hours=1),))
    sql("UPDATE NGUOI_CHOI SET SoDuVi=20000 WHERE MaTaiKhoan='TK02'")
    order(client,token,session='P_TEST')
    assert post(client,'/orders/O_TEST/accept',token,{}).status_code==200
    response=post(client,'/orders/O_TEST/pay',token,{'HinhThucThanhToan':'TruVi'})
    assert response.status_code==409 and response.json['error']['code']=='INSUFFICIENT_FUNDS'
    assert sql("SELECT SoDuVi FROM NGUOI_CHOI WHERE MaTaiKhoan='TK02'")[0]['SoDuVi']==20000


def test_wallet_spend_shortens_deadline_and_topup_extends_it(client,sql):
    token=login_as(client)
    opened=open_member(client,token)
    original=clock.as_datetime(opened['CanUseUntil'])
    order(client,token,session='P_TEST')
    assert post(client,'/orders/O_TEST/accept',token,{}).status_code==200
    paid=post(client,'/orders/O_TEST/pay',token,{'HinhThucThanhToan':'TruVi'})
    assert paid.status_code==200
    reduced=clock.as_datetime(paid.json['data']['CanUseUntil'])
    assert reduced<original
    topped=post(client,'/wallet/topups',token,topup_body(amount=15000))
    assert topped.status_code==201
    assert clock.as_datetime(topped.json['data']['CanUseUntil'])==original
