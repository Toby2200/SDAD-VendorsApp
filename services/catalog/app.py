import os
from flask import Flask, request

from database.database import init_database
from database.seed import seed_database
from catalog.routes import catalog_bp

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080")

def create_app():
    app = Flask(__name__)

    init_database()
    seed_database()

    app.register_blueprint(catalog_bp)

    @app.after_request
    def add_cors_headers(response):
        if request.headers.get("Origin") == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Vary"] = "Origin"
        return response

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8001)),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )