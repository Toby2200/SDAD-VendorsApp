import logging
import os
import time

from flask import Flask, g, jsonify, request

from database.database import get_connection
from database.migrate import run_migrations
from database.seed import seed_database
from auth.routes import auth_bp
from sales.routes import sales_bp

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "http://localhost:8080")
APP_VERSION = os.getenv("APP_VERSION", "dev")
SERVICE_NAME = "sales"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(SERVICE_NAME)


def create_app():
    app = Flask(__name__)

    run_migrations()
    seed_database()

    app.register_blueprint(auth_bp)
    app.register_blueprint(sales_bp)

    @app.before_request
    def start_timer():
        g.start_time = time.perf_counter()

    @app.after_request
    def log_request(response):
        duration_ms = (time.perf_counter() - g.get("start_time", time.perf_counter())) * 1000
        logger.info("%s %s %s %.1fms", request.method, request.path, response.status_code, duration_ms)
        return response

    @app.after_request
    def add_cors_headers(response):
        if request.headers.get("Origin") == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Vary"] = "Origin"
        return response

    @app.route("/health")
    def health():
        try:
            connection = get_connection(retries=1)
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT 1 AS ok")
                cursor.fetchone()
            finally:
                connection.close()
        except Exception:
            logger.exception("Health check failed: database unreachable")
            return jsonify({"status": "unhealthy", "service": SERVICE_NAME, "database": "unreachable", "version": APP_VERSION}), 503
        return jsonify({"status": "ok", "service": SERVICE_NAME, "database": "ok", "version": APP_VERSION}), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8002)),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )