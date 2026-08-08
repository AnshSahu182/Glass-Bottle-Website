"""
Admin Routes
Product CRUD, Featured Products, Order Status Management, User Management
All routes require admin role
"""
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from datetime import datetime
from app.utils.auth import admin_required, objectid_to_string
from app.models.validators import ProductModel

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ==================== PRODUCT MANAGEMENT ====================

@admin_bp.route('/products', methods=['GET'])
@admin_required
def admin_get_products(user_id, user_role):
    """
    Admin: Get all products
    """
    try:
        db = current_app.mongo.db
        
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        page = max(1, page)
        limit = max(1, min(limit, 100))
        
        total_count = db.products.count_documents({})
        skip = (page - 1) * limit
        
        products = list(db.products.find().skip(skip).limit(limit))
        products = [objectid_to_string(p) for p in products]
        
        return jsonify({
            'products': products,
            'pagination': {
                'current_page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': (total_count + limit - 1) // limit
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/products', methods=['POST'])
@admin_required
def admin_create_product(user_id, user_role):
    """
    Admin: Create new product
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        # Required fields
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        price = float(data['price']) if 'price' in data else None
        category = data.get('category', '').strip()
        capacity_ml = int(data['capacity_ml']) if 'capacity_ml' in data else None
        stock = int(data['stock']) if 'stock' in data else None
        images = data.get('images', [])
        is_featured = data.get('is_featured', False)
        
        # Validation
        if not all([title, description, price, category, capacity_ml is not None, stock is not None]):
            return jsonify({'error': 'All fields (title, description, price, category, capacity_ml, stock) are required'}), 400
        
        if price <= 0 or stock < 0 or capacity_ml <= 0:
            return jsonify({'error': 'Price and capacity must be positive, stock must be non-negative'}), 400
        
        db = current_app.mongo.db
        
        # Create product
        product = ProductModel.create(
            title, description, price, category, capacity_ml, stock, images, is_featured
        )
        result = db.products.insert_one(product)
        product['_id'] = result.inserted_id
        
        return jsonify({
            'message': 'Product created successfully',
            'product': objectid_to_string(product)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/products/<product_id>', methods=['PUT'])
@admin_required
def admin_update_product(product_id, user_id, user_role):
    """
    Admin: Update existing product
    """
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        db = current_app.mongo.db
        product_oid = ObjectId(product_id)
        
        # Check if product exists
        product = db.products.find_one({'_id': product_oid})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Prepare update fields
        update_fields = {}
        
        if 'title' in data and data['title'].strip():
            update_fields['title'] = data['title'].strip()
        
        if 'description' in data and data['description'].strip():
            update_fields['description'] = data['description'].strip()
        
        if 'price' in data:
            price = float(data['price'])
            if price <= 0:
                return jsonify({'error': 'Price must be positive'}), 400
            update_fields['price'] = price
        
        if 'category' in data and data['category'].strip():
            update_fields['category'] = data['category'].strip()
        
        if 'capacity_ml' in data:
            capacity = int(data['capacity_ml'])
            if capacity <= 0:
                return jsonify({'error': 'Capacity must be positive'}), 400
            update_fields['capacity_ml'] = capacity
        
        if 'stock' in data:
            stock = int(data['stock'])
            if stock < 0:
                return jsonify({'error': 'Stock cannot be negative'}), 400
            update_fields['stock'] = stock
        
        if 'images' in data:
            update_fields['images'] = data['images']
        
        if 'is_featured' in data:
            update_fields['is_featured'] = bool(data['is_featured'])
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        update_fields['updated_at'] = datetime.utcnow()
        
        # Update product
        db.products.update_one({'_id': product_oid}, {'$set': update_fields})
        
        # Return updated product
        updated_product = db.products.find_one({'_id': product_oid})
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': objectid_to_string(updated_product)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/products/<product_id>', methods=['DELETE'])
@admin_required
def admin_delete_product(product_id, user_id, user_role):
    """
    Admin: Delete product
    """
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        db = current_app.mongo.db
        product_oid = ObjectId(product_id)
        
        result = db.products.delete_one({'_id': product_oid})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({'message': 'Product deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/products/<product_id>/featured', methods=['PATCH'])
@admin_required
def admin_toggle_featured(product_id, user_id, user_role):
    """
    Admin: Toggle product featured status
    """
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        data = request.get_json()
        if not data or 'is_featured' not in data:
            return jsonify({'error': 'is_featured field required'}), 400
        
        db = current_app.mongo.db
        product_oid = ObjectId(product_id)
        
        is_featured = bool(data['is_featured'])
        
        # Update featured status
        result = db.products.update_one(
            {'_id': product_oid},
            {'$set': {'is_featured': is_featured, 'updated_at': datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        product = db.products.find_one({'_id': product_oid})
        
        return jsonify({
            'message': 'Featured status updated',
            'product': objectid_to_string(product)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ORDER MANAGEMENT ====================

@admin_bp.route('/orders', methods=['GET'])
@admin_required
def admin_get_orders(user_id, user_role):
    """
    Admin: Get all user orders with full details
    """
    try:
        db = current_app.mongo.db
        
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        status = request.args.get('status', '').strip()
        
        page = max(1, page)
        limit = max(1, min(limit, 100))
        
        # Build filter
        filter_query = {}
        if status:
            filter_query['status'] = status
        
        total_count = db.orders.count_documents(filter_query)
        skip = (page - 1) * limit
        
        orders = list(db.orders.find(filter_query).sort('created_at', -1).skip(skip).limit(limit))
        
        # Populate with user and address details
        for order in orders:
            if 'user_id' in order:
                user = db.users.find_one({'_id': order['user_id']})
                if user:
                    order['user'] = {
                        'id': str(user['_id']),
                        'email': user['email'],
                        'full_name': user.get('full_name')
                    }
            
            if 'address_id' in order:
                address = db.addresses.find_one({'_id': order['address_id']})
                if address:
                    order['address'] = objectid_to_string(address)
        
        orders = [objectid_to_string(o) for o in orders]
        
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


@admin_bp.route('/orders/<order_id>/status', methods=['PATCH'])
@admin_required
def admin_update_order_status(order_id, user_id, user_role):
    """
    Admin: Update order status
    Valid statuses: Pending, Processing, Shipped, Delivered, Cancelled
    """
    try:
        if not ObjectId.is_valid(order_id):
            return jsonify({'error': 'Invalid order ID'}), 400
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'status field required'}), 400
        
        valid_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
        new_status = data['status'].strip()
        
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        db = current_app.mongo.db
        order_oid = ObjectId(order_id)
        
        # Update order status
        result = db.orders.update_one(
            {'_id': order_oid},
            {'$set': {'status': new_status, 'updated_at': datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Order not found'}), 404
        
        order = db.orders.find_one({'_id': order_oid})
        
        return jsonify({
            'message': 'Order status updated',
            'order': objectid_to_string(order)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== USER MANAGEMENT ====================

@admin_bp.route('/users', methods=['GET'])
@admin_required
def admin_get_users(user_id, user_role):
    """
    Admin: Get all registered users with their details
    """
    try:
        db = current_app.mongo.db
        
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        page = max(1, page)
        limit = max(1, min(limit, 100))
        
        total_count = db.users.count_documents({})
        skip = (page - 1) * limit
        
        users = list(db.users.find({}, {'password': 0}).skip(skip).limit(limit))
        users = [objectid_to_string(u) for u in users]
        
        # Add address count for each user
        for user in users:
            user_oid_str = user.get('_id') or user.get('id')
            try:
                address_count = db.addresses.count_documents({'user_id': ObjectId(user_oid_str)})
            except Exception:
                address_count = 0
            user['address_count'] = address_count
        
        return jsonify({
            'users': users,
            'pagination': {
                'current_page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': (total_count + limit - 1) // limit
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<user_id>', methods=['GET'])
@admin_required
def admin_get_user_detail(user_id, user_role):
    """
    Admin: Get detailed user information including addresses
    """
    try:
        if not ObjectId.is_valid(user_id):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        db = current_app.mongo.db
        user_oid = ObjectId(user_id)
        
        user = db.users.find_one({'_id': user_oid}, {'password': 0})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's addresses
        addresses = list(db.addresses.find({'user_id': user_oid}))
        addresses = [objectid_to_string(addr) for addr in addresses]
        
        user = objectid_to_string(user)
        user['addresses'] = addresses
        
        return jsonify(user), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
