"""Cấu hình ứng dụng Backend BTL2 Quản lý quán Net.
Đọc từ biến môi trường và nạp .env nếu có.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Tìm tệp .env tại thư mục gốc dự án hoặc backend
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
dotenv_paths = [
    PROJECT_ROOT / ".env",
    Path(__file__).resolve().parent.parent / ".env",
    Path.cwd() / ".env",
]
for p in dotenv_paths:
    if p.is_file():
        load_dotenv(p)
        break


class Config:
    """Đối tượng cấu hình chuẩn theo docs/design/architecture.md và .env.example"""
    # Cơ sở dữ liệu MySQL
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "quan_net_btl2")
    DB_USER = os.getenv("DB_USER", "quan_net_app")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_TIME_ZONE = os.getenv("DB_TIME_ZONE", "+07:00")
    DB_ISOLATION_LEVEL = os.getenv("DB_ISOLATION_LEVEL", "READ COMMITTED")

    # Ứng dụng Flask
    APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "5000"))
    FRONTEND_API_BASE_URL = os.getenv("FRONTEND_API_BASE_URL", "/api/v1")

    # Bảo mật Session và CSRF
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    SESSION_COOKIE_NAME = "btl2_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() in ("true", "1", "yes")

    # Đường dẫn phục vụ Frontend
    FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

