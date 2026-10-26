"""Nghiệp vụ báo cáo thống kê quản lý Q05–Q08 (TD-03)."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from src.db import get_db_connection
from src.errors import ForbiddenError, InvalidInputError
from src.repositories import report_repo


def validate_date_range(from_date: Optional[str], to_date: Optional[str]) -> Tuple[str, str]:
    from src.validation import date_pair
    return date_pair(from_date,to_date,required=True)


def get_revenue_report(from_date: Optional[str], to_date: Optional[str], current_user: Dict[str, Any]) -> Dict[str, Any]:
    """Q05: Doanh thu thực tế (chỉ Quản lý). Không cộng nạp ví."""
    roles = current_user.get("roles", [])
    if "QuanLy" not in roles:
        raise ForbiddenError("Chỉ có Quản lý mới có quyền xem báo cáo doanh thu.")

    valid_from, valid_to = validate_date_range(from_date, to_date)
    conn = get_db_connection()
    try:
        return report_repo.get_revenue_report(conn, valid_from, valid_to)
    finally:
        conn.close()


def get_stock_report(threshold: Optional[str], current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Q06: Báo cáo tồn và hàng dưới ngưỡng (ThuNgan, QuanLy)."""
    roles = current_user.get("roles", [])
    if not any(r in ("ThuNgan", "QuanLy") for r in roles):
        raise ForbiddenError("Chỉ có Thu ngân hoặc Quản lý mới có quyền xem báo cáo tồn kho.")

    parsed_threshold = None
    if threshold is not None and threshold != "":
        try:
            parsed_threshold = int(threshold)
        except ValueError:
            raise InvalidInputError("Threshold phải là số nguyên không âm.")
        if parsed_threshold < 0:
            raise InvalidInputError("Threshold không được là số âm.")

    conn = get_db_connection()
    try:
        return report_repo.get_stock_report(conn, parsed_threshold)
    finally:
        conn.close()


def get_inventory_reconciliation_report(from_date: Optional[str], to_date: Optional[str], current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Q07: Đối soát biến động kho (chỉ Quản lý)."""
    roles = current_user.get("roles", [])
    if "QuanLy" not in roles:
        raise ForbiddenError("Chỉ có Quản lý mới có quyền xem báo cáo đối soát kho.")

    valid_from, valid_to = validate_date_range(from_date, to_date)
    conn = get_db_connection()
    try:
        return report_repo.get_reconciliation_report(conn, valid_from, valid_to)
    finally:
        conn.close()


def get_shifts_report(from_date: Optional[str], to_date: Optional[str], ma_nhan_vien: Optional[str], current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Q08: Lịch ca trực và phát hiện chồng giờ (chỉ Quản lý)."""
    roles = current_user.get("roles", [])
    if "QuanLy" not in roles:
        raise ForbiddenError("Chỉ có Quản lý mới có quyền xem báo cáo lịch ca trực.")

    valid_from, valid_to = validate_date_range(from_date, to_date)
    conn = get_db_connection()
    try:
        return report_repo.get_shifts_report(conn, valid_from, valid_to, ma_nhan_vien)
    finally:
        conn.close()
