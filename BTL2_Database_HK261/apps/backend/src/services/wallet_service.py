from src.repositories.core import lock_row
"""Wallet operations; settle expired budget before accepting a late topup."""
from src import clock
from src.auth import transaction_identity, require_roles, resource_access
from src.errors import IdempotencyConflictError, NotFoundError
from src.validation import fields, identifier, request_key, choice, integer
from src.db import get_db_connection
from src.repositories import wallet_repo
from src.repositories.core import one, all_rows
from src.services import prepaid
from src.services.session_service import settle_locked, new_code
from src.services.transaction import run_in_transaction

def get_wallet_summary(key,current_user,conn=None):
    identifier(key,'MaNguoiChoi',15)
    resource_access(current_user,key)
    own=conn is None
    conn=conn or get_db_connection()
    try:
        wallet=wallet_repo.get_wallet(conn,key)
        if not wallet:
            raise NotFoundError()
        sessions=all_rows(conn,"SELECT * FROM PHIEN_SU_DUNG WHERE MaNguoiChoi=%s AND TrangThaiPhien='DangHoatDong'",(key,))
        at=clock.now()
        holding=0
        expiry=None
        for s in sessions:
            if s['HinhThucDangNhap']=='TraTruoc':
                expiry=prepaid.deadline(s,int(wallet['SoDuVi']))
                holding+=prepaid.calculate_fee(s['ThoiDiemBatDau'],min(at,expiry) if expiry else at,s['DonGiaGioApDung'])
        return {'MaNguoiChoi':key,'SoDuVi':int(wallet['SoDuVi']),'TienGiuCho':holding,'SoDuKhaDung':int(wallet['SoDuVi'])-holding,'ThoiDiemTinh':at,'CanUseUntil':expiry}
    finally:
        if own:
            conn.close()

def topup_wallet(data,current_user):
    fields(data,{'MaGiaoDich','MaYeuCau','MaNguoiChoi','SoTien','PhuongThucGD'},{'MaGiaoDich','MaYeuCau','MaNguoiChoi','SoTien','PhuongThucGD'})
    key=identifier(data['MaGiaoDich'],'MaGiaoDich')
    request_id=request_key(data['MaYeuCau'])
    owner=identifier(data['MaNguoiChoi'],'MaNguoiChoi',15)
    amount=integer(data['SoTien'],'SoTien',1)
    method=choice(data['PhuongThucGD'],'PhuongThucGD',('TienMat','ChuyenKhoan'))
    receipt_id,settlement_id=new_code('B'),new_code('G')
    def action(conn):
        actor=transaction_identity(conn,current_user)
        require_roles(actor,'ThuNgan','QuanLy')
        wallet=lock_row(conn,'NGUOI_CHOI',owner)
        if not wallet:
            raise NotFoundError()
        existing=wallet_repo.get_transaction_by_yeu_cau(conn,request_id)
        if existing:
            if (existing['MaNguoiChoi'],int(existing['SoTien']),existing['PhuongThucGD'],existing.get('MaNhanVienXuLy'),existing['MaGiaoDich']) != (owner,amount,method,actor['MaTaiKhoan'],key):
                raise IdempotencyConflictError()
            return existing,True
        active=all_rows(conn,"SELECT * FROM PHIEN_SU_DUNG WHERE MaNguoiChoi=%s AND TrangThaiPhien='DangHoatDong'",(owner,))
        for hint in active:
            session,locked_wallet=prepaid.lock_context(conn,hint['MaPhien'])
            expiry=prepaid.deadline(session,int(locked_wallet['SoDuVi']))
            if expiry is not None and clock.now()>=expiry:
                settle_locked(conn,session,locked_wallet,clock.now(),None,'TruVi',0,receipt_id,settlement_id)
        _,replay=wallet_repo.call_sp_nap_vi(conn,key,request_id,owner,amount,method,actor['MaTaiKhoan'],clock.now())
        result=wallet_repo.get_transaction_by_yeu_cau(conn,request_id)
        if not result:
            raise NotFoundError()
        result['CanUseUntil']=get_wallet_summary(owner,actor,conn).get('CanUseUntil')
        return result,replay
    return run_in_transaction(action)
