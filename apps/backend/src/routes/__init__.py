"""Khởi tạo và đăng ký các blueprint định tuyến API."""
from flask import Blueprint
from src.routes.auth_routes import auth_bp
from src.routes.read_routes import read_bp
from src.routes.write_routes import write_bp

api_bp = Blueprint("api_v1", __name__)
api_bp.register_blueprint(auth_bp, url_prefix="/auth")
api_bp.register_blueprint(read_bp)
api_bp.register_blueprint(write_bp)

