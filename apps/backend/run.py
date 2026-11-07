"""Entrypoint chạy ứng dụng backend BTL2 Quản lý quán Net.
Cách chạy:
    cd apps/backend
    python run.py
"""
import sys
from pathlib import Path

# Thêm đường dẫn backend vào sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.app import create_app
from src.config import Config
from src.services.worker import start_worker, stop_worker

app = create_app()

if __name__ == "__main__":
    # Khởi động worker daemon kiểm soát hạn dùng trả trước (TD-12)
    start_worker(interval=15)
    try:
        print(f"[*] Khởi động Backend tại http://{Config.BACKEND_HOST}:{Config.BACKEND_PORT}")
        print(f"[*] API Base URL: http://{Config.BACKEND_HOST}:{Config.BACKEND_PORT}{Config.FRONTEND_API_BASE_URL}")
        app.run(host=Config.BACKEND_HOST, port=Config.BACKEND_PORT, debug=False)
    finally:
        stop_worker()

