from flask import Blueprint, jsonify, request, current_app
from app.utils.auth import objectid_to_string

media_bp = Blueprint('media', __name__, url_prefix='/api')


@media_bp.route('/landing-content', methods=['GET'])
def public_landing_content():
    item = current_app.mongo.db.landing_content.find_one({})
    return jsonify({'landing_content': objectid_to_string(item) if item else {}}), 200
