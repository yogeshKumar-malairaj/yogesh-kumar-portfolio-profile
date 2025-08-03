from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('backend.config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Static folder configuration (for uploads)
    app.static_folder = 'static'
    app.static_url_path = '/static'

    # Register blueprints
    from backend.Admin import admin_bp
    from backend.api import api_bp
    from backend.routes import admin_routes, public_routes

    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(public_routes.bp)

    return app

# ✅ This is required for Gunicorn: exposes `app` variable
app = create_app()
