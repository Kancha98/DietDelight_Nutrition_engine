from flask import Flask
from config import Config
from models import init_db
from auth import auth_bp
from dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialise DB
    init_db()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)