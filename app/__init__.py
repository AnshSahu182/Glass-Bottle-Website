"""
Flask Application Factory
Initializes Flask app, MongoDB, and registers blueprints
"""
import os
from datetime import timedelta
from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize PyMongo
mongo = PyMongo()


def create_app(config_name=None):
    """
    Create and configure Flask application
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Configured Flask application instance
    """


    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Create Flask app
    app = Flask(__name__)

    # Load configuration directly from environment variables
    app.config.update({
        "TESTING": False,
        "DEBUG": os.getenv("FLASK_DEBUG", "False").lower() == "true",
        "MONGO_URI": os.getenv("MONGO_URI"),
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
        "JWT_ACCESS_TOKEN_EXPIRES": timedelta(hours=24),
        "MAIL_SERVER": os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        "MAIL_PORT": int(os.getenv("MAIL_PORT", 587)),
        "MAIL_USE_TLS": os.getenv("MAIL_USE_TLS", "True").lower() == "true",
        "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
        "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
        "MAIL_DEFAULT_SENDER": os.getenv("MAIL_DEFAULT_SENDER", "noreply@glassbottles.com"),
        "OTP_EXPIRY_MINUTES": int(os.getenv("OTP_EXPIRY_MINUTES", 10)),
        "MAX_ADDRESSES_PER_USER": int(os.getenv("MAX_ADDRESSES_PER_USER", 3)),
        "PRODUCTS_PER_PAGE": int(os.getenv("PRODUCTS_PER_PAGE", 12)),
    })

    # Initialize MongoDB
    mongo.init_app(app)
    print("MONGO URI:", app.config["MONGO_URI"])
    print("mongo.db:", mongo.db)

    # Store mongo instance in app for access in routes
    app.mongo = mongo
    print("app.mongo:", app.mongo)
    # Register blueprints
    register_blueprints(app)
    
    # Setup database indexes
    setup_database_indexes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_blueprints(app):
    """Register all route blueprints"""
    from app.routes.auth_routes import auth_bp
    from app.routes.product_routes import products_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.address_routes import addresses_bp
    from app.routes.order_routes import orders_bp
    from app.routes.admin_routes import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(addresses_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)


def setup_database_indexes(app):
    """Create necessary database indexes"""
    with app.app_context():
        db = mongo.db
        
        try:
            # User indexes
            db.users.create_index('email', unique=True)
            
            # Product indexes
            db.products.create_index('category')
            db.products.create_index('is_featured')
            db.products.create_index('price')
            db.products.create_index('capacity_ml')
            
            # Cart indexes
            db.carts.create_index('user_id', unique=True)
            
            # Address indexes
            db.addresses.create_index('user_id')
            
            # Order indexes
            db.orders.create_index('user_id')
            db.orders.create_index('status')
            db.orders.create_index('created_at')
            
            # OTP indexes
            db.otps.create_index('expires_at', expireAfterSeconds=0)  # Auto-delete expired OTPs
            db.otps.create_index('email')
            
            print("Database indexes created successfully")
        except Exception as e:
            print(f"Error creating indexes: {str(e)}")


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {'error': 'Method not allowed'}, 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request'}, 400
