from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from datetime import datetime
from app.utils.auth import token_required, objectid_to_string

wishlist_bp = Blueprint('wishlist', __name__, url_prefix='/api')


@wishlist_bp.route('/wishlist', methods=['GET'])
@token_required
def get_wishlist(user_id, user_role):
    wishlist = list(request.app.mongo.db.wishlist.find({'user_id': ObjectId(user_id)}))
    return jsonify({'wishlist': [objectid_to_string(w) for w in wishlist]}), 200


@wishlist_bp.route('/wishlist', methods=['POST'])
@token_required
def add_wishlist(user_id, user_role):
    data = request.get_json() or {}
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'product_id is required'}), 400
    doc = {'_id': ObjectId(), 'user_id': ObjectId(user_id), 'product_id': ObjectId(product_id), 'created_at': datetime.utcnow()}
    request.app.mongo.db.wishlist.insert_one(doc)
    return jsonify({'message': 'Added to wishlist', 'item': objectid_to_string(doc)}), 201


@wishlist_bp.route('/wishlist/<item_id>', methods=['DELETE'])
@token_required
def remove_wishlist(item_id, user_id, user_role):
    request.app.mongo.db.wishlist.delete_one({'_id': ObjectId(item_id), 'user_id': ObjectId(user_id)})
    return jsonify({'message': 'Wishlist item removed'}), 200
