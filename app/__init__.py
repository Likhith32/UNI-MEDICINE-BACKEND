from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.database.db import db
from app.socket import init_socket


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Enable CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True,
    )

    # Initialize Socket.IO
    init_socket(app)

    # Register blueprints (IMPORT INSIDE FUNCTION to avoid circular imports)
    from app.routes.auth_routes import auth_bp
    from app.routes.ai_routes import ai_bp
    from app.routes.image_routes import image_bp
    from app.routes.places_routes import places_bp
    from app.routes.doctor_routes import doctor_bp
    from app.routes.doctors_list_routes import doctors_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(image_bp, url_prefix="/api/image")
    app.register_blueprint(places_bp, url_prefix="/api/places")
    app.register_blueprint(doctor_bp, url_prefix="/api/doctor")
    app.register_blueprint(doctors_bp, url_prefix="/api")  # /api/doctors

    # Cleanup DB session
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app
