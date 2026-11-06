from src.repositories.core import lock_row
"""Atomic inventory drafts; exact replay comparison and manager-only posting."""
from src import clock
from src.auth import transaction_identity, require_roles
from src.errors import InvalidInputError, IdempotencyConflictError, NotFoundError
from src.validation import fields, identifier, choice, integer, text, INT_MAX, PRICE_MAX
from src.repositories import inventory_repo, service_repo
from src.repositories.core import one
from src.services.transaction import run_in_transaction

def dto(conn,key):
    result=inventory_repo.get_inventory_document_by_id(conn,key)
    if not result:
        raise NotFoundError()
    result['Lines']=inventory_repo.get_inventory_lines(conn,key)
    return result

def create_inventory_document(data,current_user):
    fields(data,{'MaPhieuKho','LoaiPhieu','GhiChuLyDo','Lines'},{'MaPhieuKho','LoaiPhieu','Lines'})
    key=identifier(data['MaPhieuKho'],'MaPhieuKho')
    kind=choice(data['LoaiPhieu'],'LoaiPhieu',('NhapKho','XuatHuy','KiemKe'))
    reason=text(data.get('GhiChuLyDo'),'GhiChuLyDo',255,True)
    reason=reason or None
    lines=data['Lines']
    if not isinstance(lines,list) or not lines:
        raise InvalidInputError('Lines phải có ít nhất một dòng.')
    requested={}
    quantity_field='SoLuongThucTe' if kind=='KiemKe' else 'SoLuong'
    for line in lines:
        fields(line,{'MaDichVu',quantity_field,'DonGiaVon'},{'MaDichVu',quantity_field,'DonGiaVon'})
        code=identifier(line['MaDichVu'],'MaDichVu',10)
        if code in requested:
            raise InvalidInputError('Không được lặp MaDichVu.')
        qty=integer(line[quantity_field],quantity_field,0 if kind=='KiemKe' else 1,INT_MAX)
        price=integer(line['DonGiaVon'],'DonGiaVon',0,PRICE_MAX)
        requested[code]=(qty,price)
    def action(conn):
        actor=transaction_identity(conn,current_user)
        require_roles(actor,'ThuNgan','QuanLy')
        existing=inventory_repo.get_inventory_document_by_id(conn,key)
        if existing:
            if existing['LoaiPhieu'] != kind or (existing.get('GhiChuLyDo') or None) != reason:
                raise IdempotencyConflictError()
            saved = inventory_repo.get_inventory_lines(conn, key)
            saved_map = {x['MaDichVu']: (int(x[quantity_field] or 0), int(x['DonGiaVon'])) for x in saved}
            if saved_map != requested:
                raise IdempotencyConflictError()
            existing['Lines'] = saved
            return existing, True
        items=service_repo.get_services_by_ids_for_update(conn,list(requested))
        at=clock.now()
        inventory_repo.insert_inventory_header(conn,key,kind,reason,actor['MaTaiKhoan'],at)
        for index,code in enumerate(sorted(requested),1):
            if code not in items:
                raise NotFoundError()
            qty,price=requested[code]
            book=int(items[code]['SoLuongTon']) if kind=='KiemKe' else None
            actual=qty if kind=='KiemKe' else None
            delta=(actual-book) if kind=='KiemKe' else (qty if kind=='NhapKho' else -qty)
            inventory_repo.insert_inventory_line(conn,key,index,code,0 if kind=='KiemKe' else qty,book,actual,delta,price)
        return dto(conn,key),False
    return run_in_transaction(action)

def post_inventory_document(key,current_user):
    identifier(key,'MaPhieuKho')
    def action(conn):
        actor=transaction_identity(conn,current_user)
        require_roles(actor,'QuanLy')
        doc=lock_row(conn,'PHIEU_KHO',key)
        if not doc:
            raise NotFoundError()
        if doc['TrangThaiPhieu']=='DaGhiSo':
            return dto(conn,key),True
        _,replay=inventory_repo.call_sp_ghi_so_phieu_kho(conn,key,actor['MaTaiKhoan'],clock.now())
        return dto(conn,key),replay
    return run_in_transaction(action)
