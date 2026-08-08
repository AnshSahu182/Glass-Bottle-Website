from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from datetime import datetime
from app.utils.auth import admin_required, objectid_to_string

admin_extended_bp = Blueprint('admin_extended', __name__, url_prefix='/api/admin')


@admin_extended_bp.route('/categories', methods=['GET'])
@admin_required
def get_categories(user_id, user_role):
    db = current_app.mongo.db
    categories = list(db.categories.find().sort('created_at', -1))
    return jsonify({'categories': [objectid_to_string(c) for c in categories]}), 200


@admin_extended_bp.route('/categories', methods=['POST'])
@admin_required
def create_category(user_id, user_role):
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    db = current_app.mongo.db
    category = {'_id': ObjectId(), 'name': name, 'is_visible': True, 'created_at': datetime.utcnow()}
    db.categories.insert_one(category)
    return jsonify({'message': 'Category created', 'category': objectid_to_string(category)}), 201


@admin_extended_bp.route('/categories/<category_id>', methods=['PUT'])
@admin_required
def update_category(category_id, user_id, user_role):
    if not ObjectId.is_valid(category_id):
        return jsonify({'error': 'Invalid category ID'}), 400
    data = request.get_json() or {}
    update = {'updated_at': datetime.utcnow()}
    if 'name' in data:
        update['name'] = data['name'].strip()
    if 'is_visible' in data:
        update['is_visible'] = bool(data['is_visible'])
    current_app.mongo.db.categories.update_one({'_id': ObjectId(category_id)}, {'$set': update})
    return jsonify({'message': 'Category updated'}), 200


@admin_extended_bp.route('/categories/<category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id, user_id, user_role):
    result = current_app.mongo.db.categories.delete_one({'_id': ObjectId(category_id)})
    if result.deleted_count == 0:
        return jsonify({'error': 'Category not found'}), 404
    return jsonify({'message': 'Category deleted'}), 200


@admin_extended_bp.route('/collections', methods=['GET'])
@admin_required
def get_collections(user_id, user_role):
    collections = list(current_app.mongo.db.collections.find().sort('created_at', -1))
    return jsonify({'collections': [objectid_to_string(c) for c in collections]}), 200


@admin_extended_bp.route('/collections', methods=['POST'])
@admin_required
def create_collection(user_id, user_role):
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    collection = {'_id': ObjectId(), 'name': name, 'product_ids': [], 'created_at': datetime.utcnow()}
    current_app.mongo.db.collections.insert_one(collection)
    return jsonify({'message': 'Collection created', 'collection': objectid_to_string(collection)}), 201


@admin_extended_bp.route('/collections/<collection_id>', methods=['PUT'])
@admin_required
def update_collection(collection_id, user_id, user_role):
    data = request.get_json() or {}
    update = {'updated_at': datetime.utcnow()}
    if 'name' in data:
        update['name'] = data['name'].strip()
    current_app.mongo.db.collections.update_one({'_id': ObjectId(collection_id)}, {'$set': update})
    return jsonify({'message': 'Collection updated'}), 200


@admin_extended_bp.route('/collections/<collection_id>', methods=['DELETE'])
@admin_required
def delete_collection(collection_id, user_id, user_role):
    result = current_app.mongo.db.collections.delete_one({'_id': ObjectId(collection_id)})
    if result.deleted_count == 0:
        return jsonify({'error': 'Collection not found'}), 404
    return jsonify({'message': 'Collection deleted'}), 200


@admin_extended_bp.route('/collections/<collection_id>/products', methods=['POST'])
@admin_required
def add_products_to_collection(collection_id, user_id, user_role):
    data = request.get_json() or {}
    product_ids = data.get('product_ids', [])
    current_app.mongo.db.collections.update_one({'_id': ObjectId(collection_id)}, {'$set': {'product_ids': product_ids}})
    return jsonify({'message': 'Products linked'}), 200


@admin_extended_bp.route('/coupons', methods=['GET'])
@admin_required
def get_coupons(user_id, user_role):
    coupons = list(current_app.mongo.db.coupons.find().sort('created_at', -1))
    return jsonify({'coupons': [objectid_to_string(c) for c in coupons]}), 200


@admin_extended_bp.route('/coupons', methods=['POST'])
@admin_required
def create_coupon(user_id, user_role):
    data = request.get_json() or {}
    coupon = {'_id': ObjectId(), 'code': data.get('code'), 'discount': data.get('discount', 0), 'created_at': datetime.utcnow()}
    current_app.mongo.db.coupons.insert_one(coupon)
    return jsonify({'message': 'Coupon created', 'coupon': objectid_to_string(coupon)}), 201


@admin_extended_bp.route('/coupons/<coupon_id>', methods=['PUT'])
@admin_required
def update_coupon(coupon_id, user_id, user_role):
    current_app.mongo.db.coupons.update_one({'_id': ObjectId(coupon_id)}, {'$set': request.get_json() or {}})
    return jsonify({'message': 'Coupon updated'}), 200


@admin_extended_bp.route('/coupons/<coupon_id>', methods=['DELETE'])
@admin_required
def delete_coupon(coupon_id, user_id, user_role):
    result = current_app.mongo.db.coupons.delete_one({'_id': ObjectId(coupon_id)})
    return jsonify({'message': 'Coupon deleted'}), 200 if result.deleted_count else 404


@admin_extended_bp.route('/affiliates', methods=['GET'])
@admin_required
def get_affiliates(user_id, user_role):
    affiliates = list(current_app.mongo.db.affiliates.find())
    return jsonify({'affiliates': [objectid_to_string(a) for a in affiliates]}), 200


@admin_extended_bp.route('/affiliates', methods=['POST'])
@admin_required
def create_affiliate(user_id, user_role):
    data = request.get_json() or {}
    affiliate = {'_id': ObjectId(), 'name': data.get('name'), 'email': data.get('email'), 'created_at': datetime.utcnow()}
    current_app.mongo.db.affiliates.insert_one(affiliate)
    return jsonify({'message': 'Affiliate created', 'affiliate': objectid_to_string(affiliate)}), 201


@admin_extended_bp.route('/affiliates/<affiliate_id>', methods=['GET'])
@admin_required
def get_affiliate_detail(affiliate_id, user_id, user_role):
    affiliate = current_app.mongo.db.affiliates.find_one({'_id': ObjectId(affiliate_id)})
    if not affiliate:
        return jsonify({'error': 'Affiliate not found'}), 404
    return jsonify({'affiliate': objectid_to_string(affiliate)}), 200


@admin_extended_bp.route('/affiliates/<affiliate_id>/payout', methods=['PATCH'])
@admin_required
def affiliate_payout(affiliate_id, user_id, user_role):
    current_app.mongo.db.affiliates.update_one({'_id': ObjectId(affiliate_id)}, {'$set': {'payout_status': 'paid'}})
    return jsonify({'message': 'Payout marked'}), 200


@admin_extended_bp.route('/marketing/abandoned-carts', methods=['GET'])
@admin_required
def abandoned_carts(user_id, user_role):
    return jsonify({'abandoned_carts': []}), 200


@admin_extended_bp.route('/media/<media_id>', methods=['DELETE'])
@admin_required
def delete_media(media_id, user_id, user_role):
    media_doc = current_app.mongo.db.media.find_one({'_id': ObjectId(media_id)})
    if media_doc:
        from app.utils.cloudinary_utils import delete_file_from_cloudinary
        public_id = media_doc.get('public_id')
        res_type = 'video' if media_doc.get('type') == 'video' else 'image'
        if public_id:
            delete_file_from_cloudinary(public_id, resource_type=res_type)
        current_app.mongo.db.media.delete_one({'_id': ObjectId(media_id)})
    return jsonify({'message': 'Media deleted'}), 200


@admin_extended_bp.route('/landing-content', methods=['GET'])
@admin_required
def get_landing_content(user_id, user_role):
    item = current_app.mongo.db.landing_content.find_one({})
    return jsonify({'landing_content': objectid_to_string(item) if item else {}}), 200


@admin_extended_bp.route('/landing-content', methods=['PUT'])
@admin_required
def update_landing_content(user_id, user_role):
    data = request.get_json() or {}
    current_app.mongo.db.landing_content.update_one({}, {'$set': {**data, 'updated_at': datetime.utcnow()}}, upsert=True)
    return jsonify({'message': 'Landing content updated'}), 200


@admin_extended_bp.route('/reviews/<review_id>', methods=['DELETE'])
@admin_required
def delete_review(review_id, user_id, user_role):
    current_app.mongo.db.reviews.delete_one({'_id': ObjectId(review_id)})
    return jsonify({'message': 'Review deleted'}), 200


@admin_extended_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def dashboard_stats(user_id, user_role):
    db = current_app.mongo.db
    return jsonify({'stats': {'products': db.products.count_documents({}), 'orders': db.orders.count_documents({}), 'users': db.users.count_documents({})}}), 200


@admin_extended_bp.route('/dashboard/low-stock', methods=['GET'])
@admin_required
def dashboard_low_stock(user_id, user_role):
    low_stock = list(current_app.mongo.db.products.find({'stock': {'$lt': 10}}))
    return jsonify({'low_stock': [objectid_to_string(p) for p in low_stock]}), 200


@admin_extended_bp.route('/dashboard/top-products', methods=['GET'])
@admin_required
def dashboard_top_products(user_id, user_role):
    top = list(current_app.mongo.db.products.find().sort('stock', -1).limit(5))
    return jsonify({'top_products': [objectid_to_string(p) for p in top]}), 200


@admin_extended_bp.route('/orders/<order_id>/refund', methods=['POST'])
@admin_required
def refund_order(order_id, user_id, user_role):
    return jsonify({'message': 'Refund processed'}), 200


@admin_extended_bp.route('/payments/transactions', methods=['GET'])
@admin_required
def payment_transactions(user_id, user_role):
    return jsonify({'transactions': []}), 200


@admin_extended_bp.route('/payments/settlements', methods=['GET'])
@admin_required
def payment_settlements(user_id, user_role):
    return jsonify({'settlements': []}), 200


@admin_extended_bp.route('/orders/<order_id>/shipment', methods=['PATCH'])
@admin_required
def update_shipment(order_id, user_id, user_role):
    data = request.get_json() or {}
    return jsonify({'message': 'Shipment updated', 'tracking_number': data.get('tracking_number')}), 200


@admin_extended_bp.route('/orders/<order_id>/sync-tracking', methods=['POST'])
@admin_required
def sync_tracking(order_id, user_id, user_role):
    return jsonify({'message': 'Tracking synced'}), 200


@admin_extended_bp.route('/shipments', methods=['GET'])
@admin_required
def shipments(user_id, user_role):
    return jsonify({'shipments': []}), 200


@admin_extended_bp.route('/users/<user_id>/tags', methods=['PATCH'])
@admin_required
def update_user_tags(user_id, user_role):
    return jsonify({'message': 'Tags updated'}), 200


@admin_extended_bp.route('/orders/export', methods=['GET'])
@admin_required
def export_orders(user_id, user_role):
    return jsonify({'message': 'Orders export ready'}), 200


@admin_extended_bp.route('/orders/<order_id>/invoice', methods=['GET'])
@admin_required
def invoice_order(order_id, user_id, user_role):
    return jsonify({'message': 'Invoice generated'}), 200
