from flask import Flask, jsonify
from flask_cors import CORS
from app.database.db import db
from app.config import Config
from app.socket import init_socket

from app.routes.auth_routes import auth_bp
from app.routes.ai_routes import ai_bp
from app.routes.doctor_routes import doctor_bp
from app.routes.image_routes import image_bp
from app.routes.places_routes import places_bp


def create_app():
    """
    Factory function to create and configure the Flask app.
    Initializes DB, CORS, Socket.IO and registers blueprints.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for the frontend dev server
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True
    )

    # Init DB
    db.init_app(app)

    # Init Socket.IO for realtime messaging
    init_socket(app)

    # Register blueprints with API prefixes
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(doctor_bp, url_prefix="/api/doctor")
    app.register_blueprint(image_bp, url_prefix="/api/image")
    app.register_blueprint(places_bp, url_prefix="/api/places")

    # Simple health check
    @app.route("/")
    def home():
        return jsonify({
            "message": "University Telemedicine API is running ✅"
        })

    # Ensure tables exist during development
    with app.app_context():
        db.create_all()

    return app


# Allow running directly for development (like python app/main.py)
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

