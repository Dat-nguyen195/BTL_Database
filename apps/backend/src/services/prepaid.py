from src.repositories.core import lock_row
"""Prepaid budget derives from wallet balance, never accrued holding.
No stored deadline is needed: all supported balance changes serialize on the wallet.
Expired sessions are settled at the old deadline BEFORE a topup can extend balance.
"""
from datetime import datetime, timedelta
from src import clock
from src.errors import NotFoundError, InvalidStateError, PrepaidExpiredError
from src.repositories.core import one, all_rows, execute

def calculate_max_seconds(budget, hourly_rate):
    if hourly_rate <= 0:
        return None
    return max(0, (3600 * (int(budget) + 1) - 1) // int(hourly_rate))

def calculate_fee(start_time, end_time, hourly_rate):
    seconds = max(0, int((clock.as_datetime(end_time) - clock.as_datetime(start_time)).total_seconds()))
    return seconds * int(hourly_rate) // 3600

def deadline(session, balance=None):
    if session['HinhThucDangNhap'] != 'TraTruoc':
        return None
    budget = session['TienNapTruoc'] if not session.get('MaNguoiChoi') else balance
    if budget is None:
        raise ValueError('Member deadline requires current locked wallet balance')
    seconds = calculate_max_seconds(budget, session['DonGiaGioApDung'])
    if seconds is None:
        return None
    started=clock.as_datetime(session['ThoiDiemBatDau'])
    # DATETIME cannot represent time beyond year 9999.
    seconds=min(seconds,int((datetime.max.replace(microsecond=0)-started).total_seconds()))
    return started+timedelta(seconds=seconds)

def lock_context(conn, session_id):
    hint = one(conn, 'SELECT * FROM PHIEN_SU_DUNG WHERE MaPhien=%s', (session_id,))
    if not hint:
        raise NotFoundError()
    wallet = None
    if hint.get('MaNguoiChoi'):
        wallet = lock_row(conn,'NGUOI_CHOI',hint['MaNguoiChoi'])
        if not wallet:
            raise NotFoundError()
    lock_row(conn,'MAY_TRAM',hint['MaMay'])
    locked = lock_row(conn,'PHIEN_SU_DUNG',session_id)
    if not locked or (locked['MaMay'], locked.get('MaNguoiChoi')) != (hint['MaMay'], hint.get('MaNguoiChoi')):
        raise InvalidStateError()
    return locked, wallet

def ensure_usable(session, wallet, at):
    if session['TrangThaiPhien'] != 'DangHoatDong':
        raise InvalidStateError('Phiên đã kết thúc.')
    expiry = deadline(session, int(wallet['SoDuVi']) if wallet else None)
    if expiry is not None and at >= expiry:
        raise PrepaidExpiredError()
    return expiry

def decorate(conn, session, at=None):
    if not session or session['TrangThaiPhien'] != 'DangHoatDong':
        return session
    at = at or clock.now()
    balance = None
    if session.get('MaNguoiChoi'):
        w = one(conn, 'SELECT SoDuVi FROM NGUOI_CHOI WHERE MaTaiKhoan=%s', (session['MaNguoiChoi'],))
        balance = int(w['SoDuVi'])
    expiry = deadline(session, balance)
    effective = min(at, expiry) if expiry else at
    session['PhiHienTai'] = calculate_fee(session['ThoiDiemBatDau'], effective, session['DonGiaGioApDung'])
    if session['HinhThucDangNhap'] == 'TraTruoc':
        session['CanUseUntil'] = expiry
    return session
