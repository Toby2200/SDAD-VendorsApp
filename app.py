from flask import Flask

from auth.routes import auth_bp
from sales.routes import sales_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = "dev-secret-key"

app.register_blueprint(auth_bp)
app.register_blueprint(sales_bp)

if __name__ == "__main__":
    app.run(debug=True)