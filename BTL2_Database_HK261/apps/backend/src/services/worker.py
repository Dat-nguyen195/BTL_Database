"""One demo worker; rechecks locked balance/deadline through the shared service."""
import logging
import threading
from src import clock
from src.auth import SYSTEM_ACTOR
from src.db import get_db_connection
from src.repositories import session_repo
from src.services import prepaid
from src.services.session_service import close_session

logger = logging.getLogger(__name__)
_worker_thread = None
_stop_event = threading.Event()

def scan_and_terminate_expired_sessions(mock_now=None):
    # mock_now only controls scan selection in isolated tests; settlement clock is server-owned.
    at = mock_now or clock.now()
    conn = get_db_connection()
    try:
        sessions = session_repo.get_active_prepaid_sessions(conn)
        candidates = []
        for s in sessions:
            prepaid.decorate(conn,s,at)
            if s.get('CanUseUntil') is not None and at >= s['CanUseUntil']:
                candidates.append(s)
    finally:
        conn.close()
    closed = []
    for s in candidates:
        try:
            method = 'TruVi' if s.get('MaNguoiChoi') else 'TienMat'
            result,_ = close_session(s['MaPhien'],{'HinhThucThanhToan':method,'TienNhan':0},SYSTEM_ACTOR)
            if result['TrangThaiPhien'] == 'DaKetThuc':
                closed.append(s['MaPhien'])
        except Exception:
            logger.exception('Worker settlement failed for session %s',s['MaPhien'])
    return closed

def _worker_loop(interval):
    while not _stop_event.is_set():
        try:
            scan_and_terminate_expired_sessions()
        except Exception:
            logger.exception('Worker scan failed')
        _stop_event.wait(interval)

def start_worker(interval=15):
    global _worker_thread
    if _worker_thread is None or not _worker_thread.is_alive():
        _stop_event.clear()
        _worker_thread = threading.Thread(target=_worker_loop,args=(interval,),daemon=True)
        _worker_thread.start()

def stop_worker():
    global _worker_thread
    _stop_event.set()
    if _worker_thread:
        _worker_thread.join(timeout=2)
        if not _worker_thread.is_alive():
            _worker_thread = None
