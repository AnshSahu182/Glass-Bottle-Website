from flask import Blueprint, jsonify, request, current_app
from app.utils.auth import token_required, objectid_to_string

marketing_bp = Blueprint('marketing', __name__, url_prefix='/api')


@marketing_bp.route('/cart/apply-coupon', methods=['POST'])
@token_required
def apply_coupon(user_id, user_role):
    data = request.get_json() or {}
    code = data.get('code', '').strip()
    db = current_app.mongo.db
    coupon = db.coupons.find_one({'code': code})
    if not coupon:
        return jsonify({'error': 'Coupon not found'}), 404
    return jsonify({'message': 'Coupon applied', 'coupon': objectid_to_string(coupon)}), 200


@marketing_bp.route('/cart/remove-coupon', methods=['DELETE'])
@token_required
def remove_coupon(user_id, user_role):
    return jsonify({'message': 'Coupon removed'}), 200


@marketing_bp.route('/affiliate/track-click', methods=['POST'])
def track_click():
    data = request.get_json() or {}
    return jsonify({'message': 'Click tracked', 'affiliate_id': data.get('affiliate_id')}), 200
