import os
from flask import Flask

from database.database import init_database
from database.seed import seed_database
from catalog.routes import catalog_bp

def create_app():
    app = Flask(__name__, template_folder="../../ui/templates", static_folder="../../ui/static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    init_database()
    seed_database()

    app.register_blueprint(catalog_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8001)),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )