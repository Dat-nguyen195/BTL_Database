"""Định nghĩa 14 API đọc dữ liệu và báo cáo thống kê theo api_contract.md và TD-03."""
import uuid
from datetime import datetime
from flask import Blueprint, g, request
from src.auth import check_resource_access, get_current_user, login_required, roles_required
from src.db import get_db_connection
from src.errors import ForbiddenError, InvalidInputError, NotFoundError, make_success_response
from src.repositories import (
    inventory_repo,
    order_repo,
    service_repo,
    session_repo,
    wallet_repo,
    workstation_repo,
)
from src.services import report_service, session_service, wallet_service, prepaid
from src import clock
from src.validation import date_pair, identifier

read_bp = Blueprint("read", __name__)


def parse_pagination():
    """Trích xuất và validate page và pageSize (mặc định 20, tối đa 100)."""
    raw_page = request.args.get("page", 1)
    raw_size = request.args.get("pageSize", 20)
    try:
        page = int(raw_page)
        page_size = int(raw_size)
    except (ValueError, TypeError):
        raise InvalidInputError("page và pageSize phải là số nguyên dương.")

    if page < 1:
        raise InvalidInputError("page phải >= 1.")
    if page > 1000000:
        raise InvalidInputError("page không được vượt quá 1000000.")
    if page_size < 1 or page_size > 100:
        raise InvalidInputError("pageSize phải nằm trong khoảng từ 1 đến 100.")

    return page, page_size


def validate_optional_date_pair():
    return date_pair(request.args.get("FromDate"), request.args.get("ToDate"))


@read_bp.before_request
def validate_query():
    endpoint = (request.endpoint or '').split('.')[-1]
    specs = {
        'get_workstations': ({'MaKhuVuc','MaNhomMay','TrangThaiMay'}, {'MaMay','TenMay','TrangThaiMay'}),
        'get_sessions': ({'TrangThaiPhien','MaMay'}, {'MaPhien','ThoiDiemBatDau'}),
        'get_services': ({'MaNhomDV','TrangThaiKinhDoanh'}, {'MaDichVu','TenDichVu','GiaBanHienHanh'}),
        'get_wallet_transactions': ({'FromDate','ToDate'}, {'MaGiaoDich','ThoiDiemGD'}),
        'get_orders': ({'TrangThaiPhucVu','TrangThaiThanhToan','FromDate','ToDate'}, {'MaDonHang','ThoiDiemDat'}),
        'get_inventory_documents': ({'LoaiPhieu','TrangThaiPhieu'}, {'MaPhieuKho','ThoiDiemLap'}),
        'get_revenue_report': ({'FromDate','ToDate'}, set()),
        'get_stock_report': ({'Threshold'}, set()),
        'get_reconciliation_report': ({'FromDate','ToDate'}, set()),
        'get_shifts_report': ({'FromDate','ToDate','MaNhanVien'}, set()),
    }
    allowed, sorts = specs.get(endpoint, (set(), set()))
    allowed = allowed | ({'page','pageSize'} if endpoint in specs else set()) | ({'sort'} if sorts else set())
    if set(request.args)-allowed or any(len(request.args.getlist(k))!=1 for k in request.args):
        raise InvalidInputError('Tham số truy vấn không được phép hoặc bị lặp.')
    if 'sort' in request.args and request.args['sort'] not in sorts:
        raise InvalidInputError('Trường sort không được phép.')
    if 'page' in request.args or 'pageSize' in request.args:
        parse_pagination()
    for name,value in (request.view_args or {}).items():
        identifier(value,name,15 if name=='ma_nguoi_choi' else 20)
    for name in ('MaKhuVuc','MaNhomMay','MaMay','MaNhomDV','MaNhanVien'):
        if name in request.args:
            identifier(request.args[name],name,15 if name=='MaNhanVien' else 10)


def list_response(items):
    page,size=parse_pagination()
    return make_success_response(items[(page-1)*size:page*size],page=page,page_size=size,total=len(items),request_id=g.request_id)


# 1. GET /workstations
@read_bp.route("/workstations", methods=["GET"])
@login_required
def get_workstations():
    conn = get_db_connection()
    try:
        sort_by = request.args.get("sort", "MaMay")
        items = workstation_repo.get_workstations(
            conn,
            ma_khu_vuc=request.args.get("MaKhuVuc"),
            ma_nhom_may=request.args.get("MaNhomMay"),
            trang_thai=request.args.get("TrangThaiMay"),
            sort_by=sort_by,
        )
        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        return list_response(items)
    finally:
        conn.close()


# 2. GET /sessions
@read_bp.route("/sessions", methods=["GET"])
@login_required
def get_sessions():
    user = get_current_user()
    roles = user.get("roles", [])
    user_id = user["MaTaiKhoan"]
    is_staff = any(r in ("ThuNgan", "QuanLy") for r in roles)

    # Người chơi chỉ được xem phiên của chính mình
    ma_nguoi_choi = None if is_staff else user_id

    page, page_size = parse_pagination()
    sort_by = request.args.get("sort", "MaPhien")

    conn = get_db_connection()
    try:
        sessions, total = session_repo.get_sessions(
            conn,
            trang_thai=request.args.get("TrangThaiPhien"),
            ma_may=request.args.get("MaMay"),
            ma_nguoi_choi=ma_nguoi_choi,
            sort_by=sort_by,
            page=page,
            page_size=page_size,
        )

        for item in sessions:
            prepaid.decorate(conn,item)

        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        return make_success_response(
            sessions,
            page=page,
            page_size=page_size,
            total=total,
            request_id=req_id,
        )
    finally:
        conn.close()


# 3. GET /sessions/:MaPhien
@read_bp.route("/sessions/<ma_phien>", methods=["GET"])
@login_required
def get_session_detail(ma_phien):
    conn = get_db_connection()
    try:
        session_obj = session_repo.get_session_by_id(conn, ma_phien)
        if not session_obj:
            raise NotFoundError(f"Không tìm thấy phiên sử dụng {ma_phien}.")

        # Kiểm tra quyền truy cập tài nguyên
        check_resource_access(session_obj.get("MaNguoiChoi"))

        prepaid.decorate(conn,session_obj)

        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        return make_success_response(session_obj, request_id=req_id)
    finally:
        conn.close()


# 4. GET /services
@read_bp.route("/services", methods=["GET"])
@login_required
def get_services():
    conn = get_db_connection()
    try:
        sort_by = request.args.get("sort", "MaDichVu")
        items = service_repo.get_services(
            conn,
            ma_nhom_dv=request.args.get("MaNhomDV"),
            trang_thai=request.args.get("TrangThaiKinhDoanh"),
            sort_by=sort_by,
        )
        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        return list_response(items)
    finally:
        conn.close()


# 5. GET /wallets/:MaNguoiChoi
@read_bp.route("/wallets/<ma_nguoi_choi>", methods=["GET"])
@login_required
def get_wallet(ma_nguoi_choi):
    user = get_current_user()
    summary = wallet_service.get_wallet_summary(ma_nguoi_choi, user)
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(summary, request_id=req_id)


# 6. GET /wallets/:MaNguoiChoi/transactions
@read_bp.route("/wallets/<ma_nguoi_choi>/transactions", methods=["GET"])
@login_required
def get_wallet_transactions(ma_nguoi_choi):
    check_resource_access(ma_nguoi_choi)
    from_date, to_date = validate_optional_date_pair()
    page, page_size = parse_pagination()
    sort_by = request.args.get("sort", "ThoiDiemGD")

    conn = get_db_connection()
    try:
        txs, total = wallet_repo.get_transactions(
            conn,
            ma_nguoi_choi=ma_nguoi_choi,
            from_date=from_date,
            to_date=to_date,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
        )
        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        return make_success_response(
            txs,
            page=page,
            page_size=page_size,
            total=total,
            request_id=req_id,
        )
    finally:
        conn.close()


# 7. GET /orders
@read_bp.route("/orders", methods=["GET"])
@login_required
def get_orders():
    user = get_current_user()
    roles = user.get("roles", [])
    user_id = user["MaTaiKhoan"]
    is_staff = any(r in ("ThuNgan", "QuanLy", "PhaChe") for r in roles)

    # Người chơi chỉ xem được đơn tại máy của mình
    ma_nguoi_choi = None if is_staff else user_id

    from_date, to_date = validate_optional_date_pair()
    page, page_size = parse_pagination()
    sort_by = request.args.get("sort", "MaDonHang")

    conn = get_db_connection()
    try:
        orders, total = order_repo.get_orders(
            conn,
            trang_thai_phuc_vu=request.args.get("TrangThaiPhucVu"),
            trang_thai_thanh_toan=request.args.get("TrangThaiThanhToan"),
            from_date=from_date,
            to_date=to_date,
            ma_nguoi_choi=ma_nguoi_choi,
            sort_by=sort_by,
            page=page,
            page_size=page_size,
        )
        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        return make_success_response(
            orders,
            page=page,
            page_size=page_size,
            total=total,
            request_id=req_id,
        )
    finally:
        conn.close()


# 8. GET /orders/:MaDonHang
@read_bp.route("/orders/<ma_don_hang>", methods=["GET"])
@login_required
def get_order_detail(ma_don_hang):
    conn = get_db_connection()
    try:
        order = order_repo.get_order_by_id(conn, ma_don_hang)
        if not order:
            raise NotFoundError(f"Không tìm thấy đơn hàng {ma_don_hang}.")

        # Kiểm tra quyền tài nguyên
        check_resource_access(order.get("MaNguoiChoi"), ("ThuNgan", "QuanLy", "PhaChe"))

        order["Lines"] = order_repo.get_order_lines(conn, ma_don_hang)
        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        return make_success_response(order, request_id=req_id)
    finally:
        conn.close()


# 9. GET /inventory-documents
@read_bp.route("/inventory-documents", methods=["GET"])
@roles_required("ThuNgan", "QuanLy")
def get_inventory_documents():
    page, page_size = parse_pagination()
    sort_by = request.args.get("sort", "MaPhieuKho")

    conn = get_db_connection()
    try:
        docs, total = inventory_repo.get_inventory_documents(
            conn,
            loai_phieu=request.args.get("LoaiPhieu"),
            trang_thai=request.args.get("TrangThaiPhieu"),
            sort_by=sort_by,
            page=page,
            page_size=page_size,
        )
        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        return make_success_response(
            docs,
            page=page,
            page_size=page_size,
            total=total,
            request_id=req_id,
        )
    finally:
        conn.close()


# 10. GET /inventory-documents/:MaPhieuKho
@read_bp.route("/inventory-documents/<ma_phieu_kho>", methods=["GET"])
@roles_required("ThuNgan", "QuanLy")
def get_inventory_document_detail(ma_phieu_kho):
    conn = get_db_connection()
    try:
        doc = inventory_repo.get_inventory_document_by_id(conn, ma_phieu_kho)
        if not doc:
            raise NotFoundError(f"Không tìm thấy phiếu kho {ma_phieu_kho}.")
        doc["Lines"] = inventory_repo.get_inventory_lines(conn, ma_phieu_kho)
        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        return make_success_response(doc, request_id=req_id)
    finally:
        conn.close()


# 11. GET /reports/revenue (Q05)
@read_bp.route("/reports/revenue", methods=["GET"])
@roles_required("QuanLy")
def get_revenue_report():
    user = get_current_user()
    from_date = request.args.get("FromDate")
    to_date = request.args.get("ToDate")
    report = report_service.get_revenue_report(from_date, to_date, user)
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(report,request_id=req_id)


# 12. GET /reports/stock (Q06)
@read_bp.route("/reports/stock", methods=["GET"])
@roles_required("ThuNgan", "QuanLy")
def get_stock_report():
    user = get_current_user()
    threshold = request.args.get("Threshold")
    report = report_service.get_stock_report(threshold, user)
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return list_response(report)


# 13. GET /reports/inventory-reconciliation (Q07)
@read_bp.route("/reports/inventory-reconciliation", methods=["GET"])
@roles_required("QuanLy")
def get_reconciliation_report():
    user = get_current_user()
    from_date = request.args.get("FromDate")
    to_date = request.args.get("ToDate")
    report = report_service.get_inventory_reconciliation_report(from_date, to_date, user)
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return list_response(report)


# 14. GET /reports/shifts (Q08)
@read_bp.route("/reports/shifts", methods=["GET"])
@roles_required("QuanLy")
def get_shifts_report():
    user = get_current_user()
    from_date = request.args.get("FromDate")
    to_date = request.args.get("ToDate")
    ma_nv = request.args.get("MaNhanVien")
    report = report_service.get_shifts_report(from_date, to_date, ma_nv, user)
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return list_response(report)

