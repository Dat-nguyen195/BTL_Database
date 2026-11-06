"""Định nghĩa 8 API ghi nghiệp vụ theo api_contract.md và TD-04."""
import uuid
from flask import Blueprint, g, request
from src.auth import get_current_user, login_required, verify_csrf
from src.errors import BadJsonError, make_success_response
from src.services import (
    inventory_service,
    order_service,
    session_service,
    wallet_service,
)

write_bp = Blueprint("write", __name__)


def get_json_body() -> dict:
    from src.validation import json_body
    return json_body(request)


# 1. POST /sessions
@write_bp.route("/sessions", methods=["POST"])
@login_required
def open_session():
    verify_csrf()
    body = get_json_body()
    user = get_current_user()

    session_data, replayed = session_service.open_session(body, user)
    status_code = 200 if replayed else 201
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(
        session_data,
        replayed=replayed,
        request_id=req_id,
        status_code=status_code,
    )


# 2. POST /sessions/:MaPhien/close
@write_bp.route("/sessions/<ma_phien>/close", methods=["POST"])
@login_required
def close_session(ma_phien):
    verify_csrf()
    body = get_json_body()
    user = get_current_user()

    closed_data, replayed = session_service.close_session(ma_phien, body, user)
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(
        closed_data,
        replayed=replayed,
        request_id=req_id,
        status_code=200,
    )


# 3. POST /wallet/topups
@write_bp.route("/wallet/topups", methods=["POST"])
@login_required
def topup_wallet():
    verify_csrf()
    body = get_json_body()
    user = get_current_user()

    tx_data, replayed = wallet_service.topup_wallet(body, user)
    status_code = 200 if replayed else 201
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(
        tx_data,
        replayed=replayed,
        request_id=req_id,
        status_code=status_code,
    )


# 4. POST /orders
@write_bp.route("/orders", methods=["POST"])
@login_required
def create_order():
    verify_csrf()
    body = get_json_body()
    user = get_current_user()

    order_data, replayed = order_service.create_order(body, user)
    status_code = 200 if replayed else 201
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(
        order_data,
        replayed=replayed,
        request_id=req_id,
        status_code=status_code,
    )


# 5. POST /orders/:MaDonHang/accept
@write_bp.route("/orders/<ma_don_hang>/accept", methods=["POST"])
@login_required
def accept_order(ma_don_hang):
    verify_csrf()
    from src.validation import fields
    fields(get_json_body(), set())
    user = get_current_user()

    accepted_data, replayed = order_service.accept_order(ma_don_hang, user)
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(
        accepted_data,
        replayed=replayed,
        request_id=req_id,
        status_code=200,
    )


# 6. POST /orders/:MaDonHang/pay
@write_bp.route("/orders/<ma_don_hang>/pay", methods=["POST"])
@login_required
def pay_order(ma_don_hang):
    verify_csrf()
    body = get_json_body()
    user = get_current_user()

    paid_data, replayed = order_service.pay_order(ma_don_hang, body, user)
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(
        paid_data,
        replayed=replayed,
        request_id=req_id,
        status_code=200,
    )


# 7. POST /inventory-documents
@write_bp.route("/inventory-documents", methods=["POST"])
@login_required
def create_inventory_document():
    verify_csrf()
    body = get_json_body()
    user = get_current_user()

    doc_data, replayed = inventory_service.create_inventory_document(body, user)
    status_code = 200 if replayed else 201
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(
        doc_data,
        replayed=replayed,
        request_id=req_id,
        status_code=status_code,
    )


# 8. POST /inventory-documents/:MaPhieuKho/post
@write_bp.route("/inventory-documents/<ma_phieu_kho>/post", methods=["POST"])
@login_required
def post_inventory_document(ma_phieu_kho):
    verify_csrf()
    from src.validation import fields
    fields(get_json_body(), set())
    user = get_current_user()

    posted_data, replayed = inventory_service.post_inventory_document(ma_phieu_kho, user)
    req_id = getattr(g, "request_id", str(uuid.uuid4()))
    return make_success_response(
        posted_data,
        replayed=replayed,
        request_id=req_id,
        status_code=200,
    )

