from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from datetime import datetime
from app.utils.auth import token_required, objectid_to_string

review_bp = Blueprint('reviews', __name__, url_prefix='/api')


@review_bp.route('/products/<product_id>/reviews', methods=['GET'])
def get_reviews(product_id):
    reviews = list(request.app.mongo.db.reviews.find({'product_id': ObjectId(product_id)}))
    return jsonify({'reviews': [objectid_to_string(r) for r in reviews]}), 200


@review_bp.route('/products/<product_id>/reviews', methods=['POST'])
@token_required
def add_review(product_id, user_id, user_role):
    data = request.get_json() or {}
    review = {
        '_id': ObjectId(),
        'product_id': ObjectId(product_id),
        'user_id': ObjectId(user_id),
        'rating': data.get('rating', 5),
        'comment': data.get('comment', ''),
        'created_at': datetime.utcnow(),
    }
    request.app.mongo.db.reviews.insert_one(review)
    return jsonify({'message': 'Review added', 'review': objectid_to_string(review)}), 201
