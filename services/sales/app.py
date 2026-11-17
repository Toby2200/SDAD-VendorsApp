import os
from flask import Flask, redirect, url_for

from database.database import init_database
from database.seed import seed_database
from auth.routes import auth_bp
from sales.routes import sales_bp


def create_app():
    app = Flask(__name__, template_folder="../../ui/templates", static_folder="../../ui/static")

    init_database()
    seed_database()

    app.register_blueprint(auth_bp)
    app.register_blueprint(sales_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8002)),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )