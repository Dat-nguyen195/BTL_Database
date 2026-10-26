from src.repositories.core import lock_row
"""Order drafts and CALL actions with current permissions and durable replay checks."""
from src import clock
from src.auth import transaction_identity, require_roles, resource_access
from src.errors import InvalidInputError, IdempotencyConflictError, NotFoundError, ForbiddenError
from src.validation import fields, identifier, choice, integer, INT_MAX, MONEY_MAX
from src.repositories import order_repo, service_repo
from src.repositories.core import one
from src.services import prepaid
from src.services.transaction import run_in_transaction
from src.services.session_service import new_code

def dto(conn,key):
    result = order_repo.get_order_by_id(conn,key)
    if not result:
        raise NotFoundError()
    result['Lines'] = order_repo.get_order_lines(conn,key)
    return result

def lock_order(conn,key):
    hint = order_repo.get_order_by_id(conn,key)
    if not hint:
        raise NotFoundError()
    session, wallet = (prepaid.lock_context(conn,hint['MaPhien']) if hint.get('MaPhien') else (None,None))
    locked = lock_row(conn,'DON_GOI_DICH_VU',key)
    if not locked or locked.get('MaPhien') != hint.get('MaPhien'):
        from src.errors import InvalidStateError
        raise InvalidStateError()
    locked['MaNguoiChoi'] = session.get('MaNguoiChoi') if session else None
    return locked,session,wallet

def create_order(data,current_user):
    fields(data,{'MaDonHang','KenhDat','MaPhien','Lines'},{'MaDonHang','KenhDat','Lines'})
    key = identifier(data['MaDonHang'],'MaDonHang')
    channel = choice(data['KenhDat'],'KenhDat',('TaiMay','TaiQuay'))
    session_id = identifier(data.get('MaPhien'),'MaPhien',nullable=True)
    if (channel == 'TaiMay') != (session_id is not None):
        raise InvalidInputError('TaiMay cần MaPhien; TaiQuay không nhận MaPhien.')
    lines = data['Lines']
    if not isinstance(lines,list) or not lines:
        raise InvalidInputError('Lines phải có ít nhất một dòng.')
    requested = {}
    for line in lines:
        fields(line,{'MaDichVu','SoLuong'},{'MaDichVu','SoLuong'})
        code=identifier(line['MaDichVu'],'MaDichVu',10)
        if code in requested:
            raise InvalidInputError('Không được lặp MaDichVu.')
        requested[code]=integer(line['SoLuong'],'SoLuong',1,INT_MAX)
    def action(conn):
        actor=transaction_identity(conn,current_user)
        staff=any(r in actor['roles'] for r in ('ThuNgan','QuanLy'))
        if not staff:
            require_roles(actor,'NguoiChoi')
            if channel != 'TaiMay':
                raise ForbiddenError()
        existing=order_repo.get_order_by_id(conn,key)
        # Resource ownership is checked before both replay and creation.
        session,wallet = prepaid.lock_context(conn,session_id) if session_id else (None,None)
        if session:
            resource_access(actor,session.get('MaNguoiChoi'))
        if existing:
            resource_access(actor,existing.get('MaNguoiChoi'))
            saved=order_repo.get_order_lines(conn,key)
            if existing['KenhDat'] != channel or existing.get('MaPhien') != session_id or {x['MaDichVu']:x['SoLuong'] for x in saved} != requested:
                raise IdempotencyConflictError()
            existing['Lines']=saved
            return existing,True
        at=clock.now()
        if session:
            prepaid.ensure_usable(session,wallet,at)
        items=service_repo.get_services_by_ids_for_update(conn,list(requested))
        total=0
        for code,qty in requested.items():
            if code not in items:
                raise NotFoundError()
            if items[code]['TrangThaiKinhDoanh'] != 'DangKinhDoanh':
                raise InvalidInputError('Dịch vụ ngừng kinh doanh.')
            total += int(items[code]['GiaBanHienHanh'])*qty
        if total > MONEY_MAX:
            raise InvalidInputError('Tổng tiền vượt miền DECIMAL(12,0).')
        order_repo.insert_order_header(conn,key,channel,session_id,total,at)
        for code in sorted(requested):
            order_repo.insert_order_line(conn,key,code,requested[code],int(items[code]['GiaBanHienHanh']))
        return dto(conn,key),False
    return run_in_transaction(action)

def accept_order(key,current_user):
    identifier(key,'MaDonHang')
    def action(conn):
        actor=transaction_identity(conn,current_user)
        require_roles(actor,'ThuNgan','PhaChe','QuanLy')
        order,session,wallet=lock_order(conn,key)
        if order['TrangThaiPhucVu'] in ('DaTiepNhan','DangCheBien','DaGiao'):
            return dto(conn,key),True
        at=clock.now()
        if session:
            prepaid.ensure_usable(session,wallet,at)
        _,replay=order_repo.call_sp_tiep_nhan_don(conn,key,actor['MaTaiKhoan'],at)
        return dto(conn,key),replay
    return run_in_transaction(action)

def pay_order(key,data,current_user):
    identifier(key,'MaDonHang')
    fields(data,{'HinhThucThanhToan'},{'HinhThucThanhToan'})
    method=choice(data['HinhThucThanhToan'],'HinhThucThanhToan',('TienMat','ChuyenKhoan','TruVi'))
    transaction_id=new_code('G')
    def action(conn):
        actor=transaction_identity(conn,current_user)
        order,session,wallet=lock_order(conn,key)
        resource_access(actor,order.get('MaNguoiChoi'))
        if not any(r in actor['roles'] for r in ('ThuNgan','QuanLy')) and method != 'TruVi':
            raise ForbiddenError()
        if order['TrangThaiThanhToan'] == 'DaThanhToan':
            if order['HinhThucThanhToan'] != method:
                raise IdempotencyConflictError()
            return dto(conn,key),True
        at=clock.now()
        if session and session['TrangThaiPhien']=='DangHoatDong':
            prepaid.ensure_usable(session,wallet,at)
        _,replay=order_repo.call_sp_thanh_toan_don(conn,key,transaction_id,method,actor['MaTaiKhoan'],at)
        result=dto(conn,key)
        if session:
            # Balance may have changed; return the newly granted limit immediately.
            result['CanUseUntil']=prepaid.decorate(conn,dict(session)).get('CanUseUntil')
        return result,replay
    return run_in_transaction(action)
