from flask import Blueprint, request, jsonify, send_file
from app.modules.generator.services import GeneratorService
from app.core.parser import SchemaValidationError

generator_bp = Blueprint("generator", __name__, url_prefix="/api/generator")

@generator_bp.route("/build", methods=["POST"])
def build_project():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "Bad Request", "message": "Request payload must be valid JSON."}), 400

    try:
        zip_buffer, filename = GeneratorService.build_zip_package(payload)
        
        # Send raw binary stream with proper attachment headers
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=filename
        )
    except SchemaValidationError as e:
        return jsonify({"error": "Schema Validation Error", "details": str(e)}), 422
    except Exception as e:
        return jsonify({"error": "Internal Error", "message": str(e)}), 500