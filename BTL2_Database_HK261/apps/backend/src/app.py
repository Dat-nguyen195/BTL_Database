"""Flask App Factory phục vụ cả API /api/v1 và Frontend cùng origin cổng 5000 (KT-04, KT-05, TD-02)."""
import logging
import os
import uuid
from pathlib import Path
from flask import Flask, g, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException
from src.config import Config
from src.errors import AppError, make_error_response
from src.routes import api_bp

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app(test_config=None) -> Flask:
    """Tạo và cấu hình Flask Application Factory."""
    app = Flask(__name__, static_folder=None)

    # Nạp cấu hình
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["SESSION_COOKIE_NAME"] = Config.SESSION_COOKIE_NAME
    app.config["SESSION_COOKIE_HTTPONLY"] = Config.SESSION_COOKIE_HTTPONLY
    app.config["SESSION_COOKIE_SAMESITE"] = Config.SESSION_COOKIE_SAMESITE
    app.config["SESSION_COOKIE_SECURE"] = Config.SESSION_COOKIE_SECURE

    if test_config:
        app.config.update(test_config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY phải được cấu hình riêng trong môi trường.")

    # Đăng ký Blueprint API v1
    app.register_blueprint(api_bp, url_prefix=Config.FRONTEND_API_BASE_URL)

    # Gán Request ID cho mỗi request phục vụ truy vết log và chống lộ bí mật
    @app.before_request
    def set_request_id():
        g.request_id = str(uuid.uuid4())

    @app.after_request
    def add_headers(response):
        response.headers["X-Request-Id"] = getattr(g, "request_id", "")
        return response

    # Phục vụ Frontend cùng origin theo KT-05
    frontend_dir = Path(Config.FRONTEND_DIR)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        # Không chặn các route của API
        if path.startswith("api/"):
            return make_error_response("NOT_FOUND", "API endpoint không tồn tại.", 404, request_id=g.request_id)

        target_file = frontend_dir / path
        if path and target_file.is_file():
            return send_from_directory(frontend_dir, path)

        index_file = frontend_dir / "index.html"
        if index_file.is_file():
            return send_from_directory(frontend_dir, "index.html")

        return """
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <title>BTL2 Quản lý quán Net - Backend & API v1</title>
            <style>
                body { font-family: system-ui, sans-serif; margin: 40px; line-height: 1.6; }
                .badge { background: #10b981; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
                code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <h1>Quản lý quán Net – L09, Nhóm 10</h1>
            <p><span class="badge">Backend Sẵn Sàng</span> Cổng 5000 đang hoạt động.</p>
            <p>API Base URL: <code>/api/v1</code> (Đủ 26 endpoint theo hợp đồng).</p>
            <ul>
                <li>Lấy token CSRF: <code>GET /api/v1/auth/csrf</code></li>
                <li>Đăng nhập: <code>POST /api/v1/auth/login</code></li>
                <li>Danh mục máy trạm: <code>GET /api/v1/workstations</code></li>
                <li>Dịch vụ: <code>GET /api/v1/services</code></li>
            </ul>
        </body>
        </html>
        """, 200

    # Đăng ký xử lý ngoại lệ nghiệp vụ và lỗi hệ thống thống nhất
    @app.errorhandler(AppError)
    def handle_app_error(err: AppError):
        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        logger.warning(f"AppError [{err.code}] {err.message} (req={req_id})")
        return make_error_response(
            code=err.code,
            message=err.message,
            status_code=err.status_code,
            details=err.details,
            request_id=req_id,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        code_map = {
            400: "BAD_JSON",
            401: "UNAUTHENTICATED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "INVALID_INPUT",
        }
        code = code_map.get(err.code, "INTERNAL_ERROR")
        return make_error_response(
            code=code,
            message=err.description or "Yêu cầu HTTP không hợp lệ.",
            status_code=err.code or 500,
            request_id=req_id,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(exc: Exception):
        req_id = getattr(g, "request_id", str(uuid.uuid4()))
        logger.exception(f"Lỗi không xác định [req={req_id}]: {exc}")
        # Không để lộ chi tiết câu lệnh SQL, bí mật hoặc stack trace ra bên ngoài
        return make_error_response(
            code="INTERNAL_ERROR",
            message="Đã xảy ra lỗi nội bộ phía máy chủ.",
            status_code=500,
            request_id=req_id,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=Config.BACKEND_HOST, port=Config.BACKEND_PORT, debug=False)

