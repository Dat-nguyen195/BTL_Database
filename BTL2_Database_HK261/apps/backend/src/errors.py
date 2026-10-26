"""Định nghĩa mã lỗi, ngoại lệ nghiệp vụ và hàm định dạng response chuẩn.
Tuân thủ error_codes.md và api_contract.md.
"""
from typing import Any, Dict, Optional
from flask import jsonify, Response
from src.clock import json_value

# Bảng ánh xạ SIGNAL MYSQL_ERRNO sang error code và HTTP status
MYSQL_ERRNO_MAP = {
    60001: ("INVALID_INPUT", 422, "Dữ liệu đầu vào không hợp lệ."),
    60002: ("NOT_FOUND", 404, "Không tìm thấy tài nguyên yêu cầu."),
    60003: ("FORBIDDEN", 403, "Không có quyền thực hiện thao tác trên tài nguyên này."),
    60004: ("MACHINE_UNAVAILABLE", 409, "Máy trạm hiện không ở trạng thái sẵn sàng (AVAILABLE)."),
    60005: ("ACTIVE_SESSION_EXISTS", 409, "Máy hoặc người chơi đã có phiên sử dụng đang hoạt động."),
    60006: ("INSUFFICIENT_FUNDS", 409, "Số dư khả dụng trong ví không đủ sau khi tính phần giữ chỗ."),
    60007: ("INSUFFICIENT_STOCK", 409, "Không đủ số lượng hàng tồn kho cho ít nhất một mặt hàng yêu cầu."),
    60008: ("INVALID_STATE", 409, "Trạng thái hoặc hình thức thanh toán không hợp lệ cho thao tác này."),
    60009: ("IDEMPOTENCY_CONFLICT", 409, "Cùng mã đối tượng/yêu cầu nhưng nội dung nghiệp vụ gửi lên bị sai lệch."),
    60010: ("INVENTORY_SNAPSHOT_STALE", 409, "Ảnh kiểm kê sổ sách không còn khớp với số tồn thực tế hiện tại."),
    60011: ("IMMUTABLE_DOCUMENT", 409, "Chứng từ hoặc dòng chi tiết đã chốt, không được phép chỉnh sửa hoặc xóa."),
    60012: ("INVALID_WALLET_OWNER", 403, "Ví thanh toán không thuộc về chủ phiên sử dụng hoặc chủ đơn hàng."),
    60013: ("ACCOUNT_INACTIVE", 403, "Tài khoản đang bị khóa hoặc tạm dừng hoạt động."),
    60014: ("PREPAID_EXPIRED", 409, "Phiên chơi trả trước đã hết hạn dùng được cấp."),
    60015: ("DEPENDENCY_CONFLICT", 409, "Xung đột khóa ngoại hoặc ràng buộc quan hệ hiện có ngăn cản thao tác."),
}


class AppError(Exception):
    """Lớp ngoại lệ cơ sở cho toàn bộ lỗi nghiệp vụ và hệ thống của ứng dụng."""
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        err_obj: Dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            err_obj["details"] = self.details
        return err_obj


# Các ngoại lệ cụ thể thường dùng
class InvalidInputError(AppError):
    def __init__(self, message: str = "Dữ liệu đầu vào không hợp lệ.", details: Optional[Dict[str, Any]] = None):
        super().__init__("INVALID_INPUT", message, 422, details)


class NotFoundError(AppError):
    def __init__(self, message: str = "Không tìm thấy tài nguyên yêu cầu.", details: Optional[Dict[str, Any]] = None):
        super().__init__("NOT_FOUND", message, 404, details)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Không có quyền thực hiện thao tác trên tài nguyên này.", details: Optional[Dict[str, Any]] = None):
        super().__init__("FORBIDDEN", message, 403, details)


class MachineUnavailableError(AppError):
    def __init__(self, message: str = "Máy không ở trạng thái AVAILABLE.", details: Optional[Dict[str, Any]] = None):
        super().__init__("MACHINE_UNAVAILABLE", message, 409, details)


class ActiveSessionExistsError(AppError):
    def __init__(self, message: str = "Máy hoặc hội viên đã có phiên đang hoạt động.", details: Optional[Dict[str, Any]] = None):
        super().__init__("ACTIVE_SESSION_EXISTS", message, 409, details)


class InsufficientFundsError(AppError):
    def __init__(self, message: str = "Không đủ số dư khả dụng sau giữ chỗ.", details: Optional[Dict[str, Any]] = None):
        super().__init__("INSUFFICIENT_FUNDS", message, 409, details)


class InsufficientStockError(AppError):
    def __init__(self, message: str = "Không đủ tồn cho ít nhất một mặt hàng.", details: Optional[Dict[str, Any]] = None):
        super().__init__("INSUFFICIENT_STOCK", message, 409, details)


class InvalidStateError(AppError):
    def __init__(self, message: str = "Trạng thái hoặc hình thức thu không hợp lệ.", details: Optional[Dict[str, Any]] = None):
        super().__init__("INVALID_STATE", message, 409, details)


class IdempotencyConflictError(AppError):
    def __init__(self, message: str = "Cùng khóa/mã đối tượng nhưng nội dung nghiệp vụ khác.", details: Optional[Dict[str, Any]] = None):
        super().__init__("IDEMPOTENCY_CONFLICT", message, 409, details)


class InventorySnapshotStaleError(AppError):
    def __init__(self, message: str = "Ảnh kiểm kê không khớp tồn hiện tại.", details: Optional[Dict[str, Any]] = None):
        super().__init__("INVENTORY_SNAPSHOT_STALE", message, 409, details)


class ImmutableDocumentError(AppError):
    def __init__(self, message: str = "Chứng từ/dòng đã chốt, không cho sửa/xóa.", details: Optional[Dict[str, Any]] = None):
        super().__init__("IMMUTABLE_DOCUMENT", message, 409, details)


class InvalidWalletOwnerError(AppError):
    def __init__(self, message: str = "Ví không thuộc chủ phiên/đơn.", details: Optional[Dict[str, Any]] = None):
        super().__init__("INVALID_WALLET_OWNER", message, 403, details)


class AccountInactiveError(AppError):
    def __init__(self, message: str = "Tài khoản đang bị khóa hoặc tạm dừng.", details: Optional[Dict[str, Any]] = None):
        super().__init__("ACCOUNT_INACTIVE", message, 403, details)


class PrepaidExpiredError(AppError):
    def __init__(self, message: str = "Đã hết hạn dùng trả trước.", details: Optional[Dict[str, Any]] = None):
        super().__init__("PREPAID_EXPIRED", message, 409, details)


class DependencyConflictError(AppError):
    def __init__(self, message: str = "Khóa tham chiếu/quan hệ hiện có không cho thao tác.", details: Optional[Dict[str, Any]] = None):
        super().__init__("DEPENDENCY_CONFLICT", message, 409, details)


class UnauthenticatedError(AppError):
    def __init__(self, message: str = "Chưa đăng nhập hoặc phiên làm việc đã hết hạn.", details: Optional[Dict[str, Any]] = None):
        super().__init__("UNAUTHENTICATED", message, 401, details)


class CsrfInvalidError(AppError):
    def __init__(self, message: str = "Token CSRF thiếu hoặc không hợp lệ.", details: Optional[Dict[str, Any]] = None):
        super().__init__("CSRF_INVALID", message, 403, details)


class BadJsonError(AppError):
    def __init__(self, message: str = "Payload JSON không hợp lệ.", details: Optional[Dict[str, Any]] = None):
        super().__init__("BAD_JSON", message, 400, details)


class TxRetryExhaustedError(AppError):
    def __init__(self, message: str = "Giao dịch xung đột sau nhiều lần thử lại; vui lòng thử lại sau.", details: Optional[Dict[str, Any]] = None):
        super().__init__("TX_RETRY_EXHAUSTED", message, 503, details)


class DatabaseUnavailableError(AppError):
    def __init__(self, message: str = "Không kết nối được DB; không hiển thị dữ liệu giả thay thế.", details: Optional[Dict[str, Any]] = None):
        super().__init__("DATABASE_UNAVAILABLE", message, 503, details)


class InternalError(AppError):
    def __init__(self, message: str = "Lỗi nội bộ hệ thống.", details: Optional[Dict[str, Any]] = None):
        super().__init__("INTERNAL_ERROR", message, 500, details)


def make_success_response(
    data: Any,
    replayed: bool = False,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    total: Optional[int] = None,
    request_id: str = "",
    status_code: int = 200,
) -> tuple[Response, int]:
    """Tạo response envelope thành công đúng hợp đồng api_contract.md."""
    meta: Dict[str, Any] = {"replayed": replayed}
    if page is not None:
        meta["page"] = page
    if page_size is not None:
        meta["pageSize"] = page_size
    if total is not None:
        meta["total"] = total

    payload = {
        "ok": True,
        "data": data,
        "meta": meta,
        "requestId": request_id,
    }
    return jsonify(json_value(payload)), status_code


def make_error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None,
    request_id: str = "",
) -> tuple[Response, int]:
    """Tạo response envelope lỗi đúng hợp đồng error_codes.md."""
    err_body: Dict[str, Any] = {
        "code": code,
        "message": message,
    }
    if details:
        err_body["details"] = details

    payload = {
        "ok": False,
        "error": err_body,
        "requestId": request_id,
    }
    return jsonify(json_value(payload)), status_code

