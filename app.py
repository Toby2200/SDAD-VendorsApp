from flask import Flask

from auth.routes import auth_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = "dev-secret-key"

app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run()