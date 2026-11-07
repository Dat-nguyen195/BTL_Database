"""Quản lý kết nối CSDL MySQL bằng mysql.connector theo docs/design/architecture.md và transactions.md.
"""
import logging
from typing import Any, Optional
import mysql.connector
from mysql.connector import Error as MySQLError
from src.config import Config
from src.errors import DatabaseUnavailableError, MYSQL_ERRNO_MAP, AppError

logger = logging.getLogger(__name__)

def get_db_connection():
    """Tạo kết nối mới đến CSDL MySQL với autocommit=False, timezone=+07:00, READ COMMITTED."""
    conn = None
    try:
        if Config.DB_ISOLATION_LEVEL != "READ COMMITTED":
            raise ValueError("DB_ISOLATION_LEVEL must be READ COMMITTED")
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset="utf8mb4",
            use_pure=True,
            autocommit=False,
            connection_timeout=5,
        )

        cursor = conn.cursor()
        # Đặt múi giờ phiên giao dịch +07:00 theo KT-03
        cursor.execute("SET time_zone = %s", (Config.DB_TIME_ZONE,))
        # Đặt mức cô lập READ COMMITTED theo KT-08
        cursor.execute(f"SET SESSION TRANSACTION ISOLATION LEVEL {Config.DB_ISOLATION_LEVEL}")
        cursor.close()
        return conn

    except MySQLError as err:
        if conn is not None:
            conn.close()
        logger.error("MySQL connection/setup failed, errno=%s", err.errno)
        raise DatabaseUnavailableError(
            message="Không thể kết nối đến cơ sở dữ liệu."
        )
    except Exception as exc:
        if conn is not None:
            conn.close()
        logger.error("Database connection configuration failed")
        raise DatabaseUnavailableError(
            message="Không thể kết nối đến cơ sở dữ liệu."
        )


def map_mysql_error(err: MySQLError) -> AppError:
    """Ánh xạ lỗi MySQL (SIGNAL hoặc Native) sang AppError tương ứng theo error_codes.md."""
    errno = getattr(err, "errno", None)
    msg = getattr(err, "msg", str(err))

    # 1. Kiểm tra mã SIGNAL nghiệp vụ 60001 - 60015
    if errno in MYSQL_ERRNO_MAP:
        code, status, default_msg = MYSQL_ERRNO_MAP[errno]
        message = default_msg
        return AppError(code=code, message=message, status_code=status)

    # 2. Xung đột Unique (1062)
    if errno == 1062:
        msg_lower = msg.lower()
        if "uq_phien_may_active" in msg_lower or "uq_phien_nguoi_active" in msg_lower:
            return AppError(
                code="ACTIVE_SESSION_EXISTS",
                message="Máy trạm hoặc người chơi đã có một phiên sử dụng đang hoạt động.",
                status_code=409,
            )
        if "uq_vi_thu_phien" in msg_lower or "uq_vi_thu_don" in msg_lower or "mayeucau" in msg_lower:
            return AppError(
                code="IDEMPOTENCY_CONFLICT",
                message="Giao dịch hoặc phiên đã được thực hiện trước đó với cùng khóa nghiệp vụ.",
                status_code=409,
            )
        return AppError(
            code="IDEMPOTENCY_CONFLICT",
            message="Dữ liệu bị trùng lặp khóa duy nhất trên hệ thống.",
            status_code=409,
        )

    # 3. Lỗi khóa ngoại FK (1451, 1452)
    if errno in (1451, 1452):
        return AppError(
            code="DEPENDENCY_CONFLICT",
            message="Ràng buộc khóa ngoại không cho phép thao tác này.",
            status_code=409,
        )

    # 4. Lỗi kết nối (2002, 2003, 2006, 2013)
    if errno in (2002, 2003, 2006, 2013):
        return DatabaseUnavailableError()

    # 5. Các lỗi cú pháp / kiểm tra CHECK / NOT NULL
    if errno in (3819, 1048, 1264, 1366):
        return AppError(
            code="INVALID_INPUT",
            message="Dữ liệu không thỏa mãn ràng buộc cho phép.",
            status_code=422,
        )

    # Mặc định trả InternalError nhưng không để lộ chi tiết SQL ra client
    logger.error(f"Lỗi MySQL chưa ánh xạ riêng: {errno} - {msg}")
    return AppError(
        code="INTERNAL_ERROR",
        message="Có lỗi xảy ra trong quá trình xử lý cơ sở dữ liệu.",
        status_code=500,
    )

