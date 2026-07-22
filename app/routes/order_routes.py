"""
Order Routes
POST /api/orders - Place new order from cart
GET /api/orders - Get order history for user
GET /api/orders/<id> - Get order details
STRICT RULE: Orders cannot be edited or cancelled after creation
"""
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from app.utils.auth import token_required, objectid_to_string
from app.utils.email import send_order_confirmation_email
from app.models.validators import OrderModel

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


@orders_bp.route('', methods=['POST'])
@token_required
def create_order(user_id, user_role):
    """
    Create new order from current cart items and selected address
    STRICT RULE: Order cannot be modified or cancelled after creation
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        address_id = data.get('address_id', '').strip()
        
        if not address_id or not ObjectId.is_valid(address_id):
            return jsonify({'error': 'Valid address_id is required'}), 400
        
        db = request.app.mongo.db
        user_oid = ObjectId(user_id)
        address_oid = ObjectId(address_id)
        
        # Verify address belongs to user
        address = db.addresses.find_one({'_id': address_oid, 'user_id': user_oid})
        if not address:
            return jsonify({'error': 'Address not found or does not belong to user'}), 404
        
        # Get user's cart
        cart = db.carts.find_one({'user_id': user_oid})
        if not cart or not cart.get('items'):
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Process cart items and verify stock
        order_items = []
        total_amount = 0
        
        for item in cart['items']:
            product = db.products.find_one({'_id': item['product_id']})
            if not product:
                return jsonify({'error': f'Product not found in cart'}), 400
            
            if product['stock'] < item['quantity']:
                return jsonify({
                    'error': f'Insufficient stock for {product["title"]}. Available: {product["stock"]}'
                }), 400
            
            item_total = product['price'] * item['quantity']
            total_amount += item_total
            
            # Store order item with snapshot of product data
            order_items.append({
                'product_id': item['product_id'],
                'product_title': product['title'],
                'product_price': product['price'],
                'quantity': item['quantity'],
                'item_total': item_total
            })
        
        # Create order
        order = OrderModel.create(user_oid, address_oid, order_items, round(total_amount, 2), status='Pending')
        result = db.orders.insert_one(order)
        order_id = str(result.inserted_id)
        
        # Reduce product stock for each item
        for item in order_items:
            db.products.update_one(
                {'_id': item['product_id']},
                {'$inc': {'stock': -item['quantity']}}
            )
        
        # Clear user's cart
        db.carts.update_one(
            {'user_id': user_oid},
            {'$set': {'items': [], 'updated_at': datetime.utcnow()}}
        )
        
        # Send order confirmation email
        user = db.users.find_one({'_id': user_oid})
        if user:
            send_order_confirmation_email(user['email'], order_id, user.get('full_name', 'User'))
        
        return jsonify({
            'message': 'Order created successfully',
            'order_id': order_id,
            'total_amount': total_amount,
            'status': 'Pending'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('', methods=['GET'])
@token_required
def get_orders(user_id, user_role):
    """
    Get order history for logged-in user
    """
    try:
        db = request.app.mongo.db
        user_oid = ObjectId(user_id)
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        page = max(1, page)
        limit = max(1, min(limit, 50))
        
        # Get total count
        total_count = db.orders.count_documents({'user_id': user_oid})
        
        # Get paginated orders
        skip = (page - 1) * limit
        orders = list(db.orders.find({'user_id': user_oid}).sort('created_at', -1).skip(skip).limit(limit))
        orders = [objectid_to_string(order) for order in orders]
        
        return jsonify({
            'orders': orders,
            'pagination': {
                'current_page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': (total_count + limit - 1) // limit
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>', methods=['GET'])
@token_required
def get_order_detail(order_id, user_id, user_role):
    """
    Get detailed information for specific order
    Users can only view their own orders
    """
    try:
        if not ObjectId.is_valid(order_id):
            return jsonify({'error': 'Invalid order ID'}), 400
        
        db = request.app.mongo.db
        user_oid = ObjectId(user_id)
        order_oid = ObjectId(order_id)
        
        # Get order (verify it belongs to user unless admin)
        if user_role != 'admin':
            order = db.orders.find_one({'_id': order_oid, 'user_id': user_oid})
        else:
            order = db.orders.find_one({'_id': order_oid})
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Populate with additional details
        order = objectid_to_string(order)
        
        # Get address details
        if 'address_id' in order:
            address = db.addresses.find_one({'_id': ObjectId(order['address_id'])})
            if address:
                order['address'] = objectid_to_string(address)
        
        return jsonify(order), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
