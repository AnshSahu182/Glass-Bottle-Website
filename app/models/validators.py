"""
Data Models and Validators
Schema helpers and validation functions for MongoDB documents
"""
from datetime import datetime
from bson.objectid import ObjectId


class UserModel:
    """User data model"""
    @staticmethod
    def create(email: str, password_hash: str, full_name: str = ""):
        """Create new user document"""
        return {
            '_id': ObjectId(),
            'email': email,
            'password': password_hash,
            'full_name': full_name,
            'role': 'user',
            'is_verified': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }


class OTPModel:
    """OTP data model"""
    @staticmethod
    def create(email: str, otp: str, expiry_minutes: int = 10):
        """Create OTP document"""
        return {
            '_id': ObjectId(),
            'email': email,
            'otp': otp,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + __import__('datetime').timedelta(minutes=expiry_minutes),
            'is_used': False
        }


class ProductModel:
    """Product data model"""
    @staticmethod
    def create(title: str, description: str, price: float, category: str,
               capacity_ml: int, stock: int, images: list = None, is_featured: bool = False):
        """Create product document"""
        return {
            '_id': ObjectId(),
            'title': title,
            'description': description,
            'price': price,
            'category': category,
            'capacity_ml': capacity_ml,
            'stock': stock,
            'images': images or [],
            'is_featured': is_featured,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }


class CartModel:
    """Cart data model"""
    @staticmethod
    def create(user_id):
        """Create cart document"""
        return {
            '_id': ObjectId(),
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'items': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    
    @staticmethod
    def add_item(product_id, quantity: int):
        """Create cart item"""
        return {
            '_id': ObjectId(),
            'product_id': ObjectId(product_id) if isinstance(product_id, str) else product_id,
            'quantity': quantity,
            'added_at': datetime.utcnow()
        }


class AddressModel:
    """Address data model"""
    @staticmethod
    def create(user_id, full_name: str, phone: str, street: str, city: str,
               state: str, postal_code: str, country: str = "India"):
        """Create address document"""
        return {
            '_id': ObjectId(),
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'full_name': full_name,
            'phone': phone,
            'street': street,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'country': country,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }


class OrderModel:
    """Order data model"""
    @staticmethod
    def create(user_id, address_id, items: list, total_amount: float, status: str = "Pending"):
        """Create order document"""
        return {
            '_id': ObjectId(),
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'address_id': ObjectId(address_id) if isinstance(address_id, str) else address_id,
            'items': items,
            'total_amount': total_amount,
            'status': status,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }


# Validation functions
def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Validate password (min 6 characters)"""
    return len(password) >= 6


def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    import re
    # Simple validation: 10 digits
    pattern = r'^\d{10}$'
    return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None
