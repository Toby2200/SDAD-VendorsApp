import os
from flask import Flask, redirect, url_for

from database.database import init_database
from database.seed import seed_database
from auth.routes import auth_bp
from catalog.routes import catalog_bp
from sales.routes import sales_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    init_database()
    seed_database()

    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(sales_bp)

    @app.route("/")
    def home():
        return redirect(url_for("auth.login"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )