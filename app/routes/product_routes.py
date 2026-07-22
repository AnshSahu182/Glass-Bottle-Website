from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from app.utils.auth import objectid_to_string

products_bp = Blueprint('products', __name__, url_prefix='/api')


@products_bp.route('/home', methods=['GET'])
def get_home():
    """
    Get featured products for home page
    """
    try:
        db = current_app.mongo.db
        
        # Get featured products
        featured_products = list(db.products.find({'is_featured': True}).limit(6))
        featured_products = [objectid_to_string(p) for p in featured_products]
        
        return jsonify({
            'featured_products': featured_products,
            'count': len(featured_products)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/products', methods=['GET'])
def get_products():
    """
    List products with filtering and pagination
    
    Query Parameters:
        - category: Filter by category
        - min_price: Filter by minimum price
        - max_price: Filter by maximum price
        - capacity: Filter by capacity in ml (e.g., 250, 500, 1000)
        - page: Page number (default 1)
        - limit: Items per page (default 12)
        - search: Search by product title or description
    """
    try:
        db = current_app.mongo.db
        
        # Get query parameters
        category = request.args.get('category', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        capacity = request.args.get('capacity', type=int)
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 12, type=int)
        
        # Validate pagination
        page = max(1, page)
        limit = max(1, min(limit, 100))  # Cap at 100 items
        
        # Build filter
        filter_query = {}
        
        if category:
            filter_query['category'] = {'$regex': category, '$options': 'i'}
        
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter['$gte'] = min_price
            if max_price is not None:
                price_filter['$lte'] = max_price
            filter_query['price'] = price_filter
        
        if capacity:
            filter_query['capacity_ml'] = capacity
        
        if search:
            filter_query['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        
        # Get total count
        total_count = db.products.count_documents(filter_query)
        
        # Get paginated results
        skip = (page - 1) * limit
        products = list(db.products.find(filter_query).skip(skip).limit(limit))
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


@products_bp.route('/products/<product_id>', methods=['GET'])
def get_product_detail(product_id):
    """
    Get detailed information for a single product
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        db = request.app.mongo.db
        product = db.products.find_one({'_id': ObjectId(product_id)})
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        product = objectid_to_string(product)
        return jsonify(product), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
