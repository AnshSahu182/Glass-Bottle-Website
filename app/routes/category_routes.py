from flask import Blueprint, jsonify, request, current_app
from bson.objectid import ObjectId
from app.utils.auth import objectid_to_string

category_bp = Blueprint('categories', __name__, url_prefix='/api')


@category_bp.route('/categories', methods=['GET'])
def public_categories():
    db = current_app.mongo.db
    categories = list(db.categories.find({'is_visible': True}).sort('created_at', -1))
    return jsonify({'categories': [objectid_to_string(c) for c in categories]}), 200


@category_bp.route('/collections', methods=['GET'])
def public_collections():
    db = current_app.mongo.db
    collections = list(db.collections.find().sort('created_at', -1))
    return jsonify({'collections': [objectid_to_string(c) for c in collections]}), 200
