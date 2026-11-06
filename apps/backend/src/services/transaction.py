"""Caller-owned atomic write, bounded whole-transaction retries and replay recovery."""
import logging
import random
import time
from mysql.connector import Error as MySQLError
from src.db import get_db_connection, map_mysql_error
from src.errors import TxRetryExhaustedError, InternalError

logger = logging.getLogger(__name__)

def consume_call_results(cursor):
    results = [result.fetchall() for result in cursor.stored_results()]
    if len(results) != 1 or len(results[0]) != 1 or len(results[0][0]) != 2:
        raise InternalError("Routine trả kết quả không đúng hợp đồng.")
    if results[0][0][1] not in (0, 1):
        raise InternalError("Routine trả cờ replay không hợp lệ.")
    return results

def run_in_transaction(func, *args, **kwargs):
    duplicate_recovered = False
    lock_failures = 0
    while True:
        conn = None
        retry = False
        try:
            conn = get_db_connection()
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as error:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    logger.warning("Rollback failed; closing connection")
            if not isinstance(error, MySQLError):
                raise
            if error.errno in (1213, 1205):
                lock_failures += 1
                if lock_failures >= 3:
                    raise TxRetryExhaustedError() from error
                retry = True
            elif error.errno == 1062 and not duplicate_recovered and not any(
                key in (error.msg or "").lower()
                for key in ("uq_phien_may_active", "uq_phien_nguoi_active")
            ):
                # Re-execute from a fresh transaction: normal replay checks verify
                # authority AND payload. Never turn an arbitrary duplicate into success.
                duplicate_recovered = True
                retry = True
            else:
                raise map_mysql_error(error) from error
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    logger.warning("Connection close failed")
        if retry:
            time.sleep(random.uniform(0.01, 0.04) * (1 + lock_failures))
