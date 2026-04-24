from flask import Flask

from .config import settings
from .extensions import db
from .routes import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    @app.after_request
    def add_cors_headers(response):
        # 前端开发环境通过 Vite 代理访问这里，但直接请求后端时
        # 仍然需要补齐 CORS 头，避免浏览器拦截。
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    @app.route("/api/health", methods=["GET"])
    def health():
        return {
            "ok": True,
            "data": {
                "service": "programming-assistant-backend",
                "stack": "flask-langchain",
            },
        }

    app.register_blueprint(api_bp)

    with app.app_context():
        # 先用 create_all 保证本地开发和毕设演示可直接启动。
        # 后面如果表结构开始频繁演进，再引入 Flask-Migrate。
        from . import models  # noqa: F401
        from .services.mistake_service import seed_sample_mistakes
        from .services.rag_service import rebuild_rag_index

        db.create_all()
        seed_sample_mistakes()
        rebuild_rag_index()

    return app


__all__ = ["create_app", "settings"]
