"""Atomic session operations and server-controlled settlement time."""
import secrets
from datetime import timedelta
from src import clock
from src.auth import SYSTEM_ACTOR, transaction_identity, resource_access, require_roles
from src.errors import ForbiddenError, IdempotencyConflictError, NotFoundError
from src.validation import fields, identifier, choice, integer
from src.repositories import session_repo
from src.repositories.core import one, call
from src.services.transaction import run_in_transaction
from src.services import prepaid

calculate_max_seconds = prepaid.calculate_max_seconds
calculate_fee = prepaid.calculate_fee

def calculate_can_use_until(start_time, budget, hourly_rate):
    seconds = calculate_max_seconds(budget, hourly_rate)
    return None if seconds is None else clock.json_value(clock.as_datetime(start_time) + timedelta(seconds=seconds))

def new_code(prefix):
    return prefix + secrets.token_hex(10)[:19].upper()

def open_session(data, current_user):
    fields(data, {'MaPhien','MaMay','MaNguoiChoi','HinhThucDangNhap','TienNapTruoc'}, {'MaPhien','MaMay','HinhThucDangNhap','TienNapTruoc'})
    key = identifier(data['MaPhien'],'MaPhien')
    machine = identifier(data['MaMay'],'MaMay',10)
    owner = identifier(data.get('MaNguoiChoi'),'MaNguoiChoi',15,True)
    kind = choice(data['HinhThucDangNhap'],'HinhThucDangNhap',('TraTruoc','TraSau','MienPhi'))
    amount = integer(data['TienNapTruoc'],'TienNapTruoc')
    def action(conn):
        actor = transaction_identity(conn, current_user)
        staff = any(r in actor['roles'] for r in ('ThuNgan','QuanLy'))
        effective_owner = owner
        if not staff:
            require_roles(actor, 'NguoiChoi')
            if kind != 'TraTruoc' or (owner is not None and owner != actor['MaTaiKhoan']):
                raise ForbiddenError()
            effective_owner = actor['MaTaiKhoan']
        if kind == 'MienPhi':
            require_roles(actor, 'QuanLy')
        if amount and (effective_owner is not None or kind != 'TraTruoc'):
            from src.errors import InvalidInputError
            raise InvalidInputError('TienNapTruoc chỉ dành cho vãng lai trả trước.')
        _, replay = session_repo.call_sp_mo_phien(conn,key,machine,effective_owner,kind,amount,actor['MaTaiKhoan'],clock.now())
        result = session_repo.get_session_by_id(conn,key)
        if not result:
            raise NotFoundError()
        return prepaid.decorate(conn,result), replay
    return run_in_transaction(action)

def settle_locked(conn, session, wallet, at, actor_id, method, received, receipt_id, transaction_id):
    expiry = prepaid.deadline(session, int(wallet['SoDuVi']) if wallet else None)
    # Even a manual close after expiry settles only at the granted deadline.
    effective = min(at, expiry) if expiry else at
    _, replay = session_repo.call_sp_ket_thuc_phien(conn,session['MaPhien'],receipt_id,transaction_id,method,received,actor_id,effective)
    result = session_repo.get_session_by_id(conn,session['MaPhien'])
    result['BienLai'] = one(conn,'SELECT * FROM BIEN_LAI_TIEN_MAY WHERE MaPhien=%s',(session['MaPhien'],))
    return result, replay

def close_session(ma_phien, data, current_user):
    identifier(ma_phien,'MaPhien')
    fields(data, {'HinhThucThanhToan','TienNhan'}, {'HinhThucThanhToan'})
    method = choice(data['HinhThucThanhToan'],'HinhThucThanhToan',('TienMat','ChuyenKhoan','TruVi','ChuaThu','MienPhi'))
    received = integer(data.get('TienNhan',0),'TienNhan')
    receipt_id, transaction_id = new_code('B'),new_code('G')
    def action(conn):
        actor = None if current_user is SYSTEM_ACTOR else transaction_identity(conn,current_user)
        session, wallet = prepaid.lock_context(conn,ma_phien)
        if actor:
            resource_access(actor, session.get('MaNguoiChoi'))
            if not any(r in actor['roles'] for r in ('ThuNgan','QuanLy')) and method != 'TruVi':
                raise ForbiddenError()
        else:
            # Internal caller may only close an actually expired prepaid session.
            expiry = prepaid.deadline(session, int(wallet['SoDuVi']) if wallet else None)
            if session['TrangThaiPhien'] == 'DangHoatDong' and (expiry is None or clock.now() < expiry):
                return session, True
        effective_received = received
        if session.get('MaNguoiChoi') is None and session['HinhThucDangNhap']=='TraTruoc':
            if received != 0:
                from src.errors import InvalidInputError
                raise InvalidInputError('Vãng lai trả trước dùng tiền đã nạp; TienNhan khi đóng phải bằng 0.')
            effective_received = int(session['TienNapTruoc'])
        if session['TrangThaiPhien'] == 'DaKetThuc':
            receipt = one(conn,'SELECT * FROM BIEN_LAI_TIEN_MAY WHERE MaPhien=%s',(ma_phien,))
            expected = 'TienMat' if method == 'ChuaThu' else method
            if not receipt or receipt['HinhThucThanhToan'] != expected or int(receipt['TienNhan']) != effective_received or (method == 'ChuaThu') != (receipt['TrangThaiBienLai'] == 'ChuaThanhToan'):
                raise IdempotencyConflictError()
            session['BienLai'] = receipt
            return session, True
        return settle_locked(conn, session, wallet, clock.now(), actor['MaTaiKhoan'] if actor else None, method, effective_received, receipt_id,transaction_id)
    return run_in_transaction(action)
