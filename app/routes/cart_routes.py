"""
Cart Routes
GET /api/cart - View cart items
POST /api/cart - Add item to cart
PUT /api/cart/<item_id> - Update item quantity
DELETE /api/cart/<item_id> - Remove item from cart
DELETE /api/cart - Clear entire cart
"""
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from app.utils.auth import token_required, objectid_to_string
from app.models.validators import CartModel

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


@cart_bp.route('', methods=['GET'])
@token_required
def get_cart(user_id, user_role):
    """
    View items in user's cart with product details and subtotal
    """
    try:
        db = current_app.mongo.db
        user_oid = ObjectId(user_id)
        
        # Get or create cart
        cart = db.carts.find_one({'user_id': user_oid})
        if not cart:
            return jsonify({
                'cart_items': [],
                'total_items': 0,
                'total_amount': 0
            }), 200
        
        # Populate cart items with product details
        cart_items = []
        total_amount = 0
        
        for item in cart.get('items', []):
            product = db.products.find_one({'_id': item['product_id']})
            if product:
                item_total = product['price'] * item['quantity']
                total_amount += item_total
                
                cart_items.append({
                    'cart_item_id': str(item['_id']),
                    'product_id': str(item['product_id']),
                    'product_title': product['title'],
                    'product_price': product['price'],
                    'product_image': product['images'][0] if product.get('images') else None,
                    'quantity': item['quantity'],
                    'item_total': item_total
                })
        
        return jsonify({
            'cart_items': cart_items,
            'total_items': len(cart_items),
            'total_amount': round(total_amount, 2)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('', methods=['POST'])
@token_required
def add_to_cart(user_id, user_role):
    """
    Add item (product_id, quantity) to cart
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        product_id = data.get('product_id', '').strip()
        quantity = int(data.get('quantity', 1))
        
        # Validation
        if not product_id or not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400
        
        db = current_app.mongo.db
        user_oid = ObjectId(user_id)
        product_oid = ObjectId(product_id)
        
        # Check if product exists and has stock
        product = db.products.find_one({'_id': product_oid})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if product['stock'] < quantity:
            return jsonify({'error': f'Insufficient stock. Available: {product["stock"]}'}), 400
        
        # Get or create cart
        cart = db.carts.find_one({'user_id': user_oid})
        if not cart:
            cart = CartModel.create(user_oid)
            db.carts.insert_one(cart)
        
        # Check if product already in cart
        existing_item = next((item for item in cart.get('items', []) 
                            if item['product_id'] == product_oid), None)
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item['quantity'] + quantity
            if product['stock'] < new_quantity:
                return jsonify({'error': f'Insufficient stock. Available: {product["stock"]}'}), 400
            
            db.carts.update_one(
                {'_id': cart['_id'], 'items._id': existing_item['_id']},
                {'$set': {'items.$.quantity': new_quantity, 'updated_at': __import__('datetime').datetime.utcnow()}}
            )
        else:
            # Add new item
            new_item = CartModel.add_item(product_oid, quantity)
            db.carts.update_one(
                {'_id': cart['_id']},
                {'$push': {'items': new_item}, '$set': {'updated_at': __import__('datetime').datetime.utcnow()}}
            )
        
        return jsonify({
            'message': 'Item added to cart successfully',
            'product_id': product_id,
            'quantity': quantity
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/<item_id>', methods=['PUT'])
@token_required
def update_cart_item(item_id, user_id, user_role):
    """
    Update quantity of item in cart
    """
    try:
        if not ObjectId.is_valid(item_id):
            return jsonify({'error': 'Invalid item ID'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        new_quantity = int(data['quantity']) if 'quantity' in data else None
        
        if not new_quantity or new_quantity <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400
        
        db = current_app.mongo.db
        user_oid = ObjectId(user_id)
        item_oid = ObjectId(item_id)
        
        # Find cart and item
        cart = db.carts.find_one({'user_id': user_oid})
        if not cart:
            return jsonify({'error': 'Cart not found'}), 404
        
        item = next((i for i in cart.get('items', []) if i['_id'] == item_oid), None)
        if not item:
            return jsonify({'error': 'Item not found in cart'}), 404
        
        # Check product stock
        product = db.products.find_one({'_id': item['product_id']})
        if not product or product['stock'] < new_quantity:
            return jsonify({'error': f'Insufficient stock. Available: {product["stock"] if product else 0}'}), 400
        
        # Update quantity
        db.carts.update_one(
            {'_id': cart['_id'], 'items._id': item_oid},
            {'$set': {'items.$.quantity': new_quantity, 'updated_at': __import__('datetime').datetime.utcnow()}}
        )
        
        return jsonify({
            'message': 'Cart item updated successfully',
            'item_id': item_id,
            'new_quantity': new_quantity
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/<item_id>', methods=['DELETE'])
@token_required
def remove_cart_item(item_id, user_id, user_role):
    """
    Remove specific item from cart
    """
    try:
        if not ObjectId.is_valid(item_id):
            return jsonify({'error': 'Invalid item ID'}), 400
        
        db = current_app.mongo.db
        user_oid = ObjectId(user_id)
        item_oid = ObjectId(item_id)
        
        # Find and update cart
        cart = db.carts.find_one({'user_id': user_oid})
        if not cart:
            return jsonify({'error': 'Cart not found'}), 404
        
        result = db.carts.update_one(
            {'_id': cart['_id']},
            {'$pull': {'items': {'_id': item_oid}}, '$set': {'updated_at': __import__('datetime').datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Item not found in cart'}), 404
        
        return jsonify({'message': 'Item removed from cart successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('', methods=['DELETE'])
@token_required
def clear_cart(user_id, user_role):
    """
    Clear entire cart for user
    """
    try:
        db = current_app.mongo.db
        user_oid = ObjectId(user_id)
        
        # Delete or clear cart
        db.carts.update_one(
            {'user_id': user_oid},
            {'$set': {'items': [], 'updated_at': __import__('datetime').datetime.utcnow()}}
        )
        
        return jsonify({'message': 'Cart cleared successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
