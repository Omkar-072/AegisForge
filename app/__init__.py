import os
from flask import Flask, jsonify
from config import config_by_name

def create_app(config_name=None):
    if not config_name:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Register the generator module blueprint
    from app.modules.generator.controllers import generator_bp
    app.register_blueprint(generator_bp)

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "project": "AegisForge Engine Core",
            "environment": config_name
        }), 200

    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify({"error": "Resource not found", "message": str(e)}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred within AegisForge core."}), 500

    return app