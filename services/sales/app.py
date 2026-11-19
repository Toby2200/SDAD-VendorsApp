import os
from flask import Flask, request

from database.migrate import run_migrations
from database.seed import seed_database
from auth.routes import auth_bp
from sales.routes import sales_bp

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080")

def create_app():
    app = Flask(__name__)

    run_migrations()
    seed_database()

    app.register_blueprint(auth_bp)
    app.register_blueprint(sales_bp)

    @app.after_request
    def add_cors_headers(response):
        if request.headers.get("Origin") == ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGINS
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Vary"] = "Origin"
        return response

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8002)),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )