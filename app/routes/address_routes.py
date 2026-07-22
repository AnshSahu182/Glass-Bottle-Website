"""
Address Routes
GET /api/addresses - List user's addresses
POST /api/addresses - Add new address (max 3 per user)
PUT /api/addresses/<id> - Update address
DELETE /api/addresses/<id> - Delete address
"""
import os
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from app.utils.auth import token_required, objectid_to_string
from app.models.validators import AddressModel, validate_phone

addresses_bp = Blueprint('addresses', __name__, url_prefix='/api/addresses')


@addresses_bp.route('', methods=['GET'])
@token_required
def get_addresses(user_id, user_role):
    """
    Get all addresses for logged-in user
    """
    try:
        db = request.app.mongo.db
        user_oid = ObjectId(user_id)
        
        addresses = list(db.addresses.find({'user_id': user_oid}).sort('created_at', -1))
        addresses = [objectid_to_string(addr) for addr in addresses]
        
        return jsonify({
            'addresses': addresses,
            'count': len(addresses)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@addresses_bp.route('', methods=['POST'])
@token_required
def add_address(user_id, user_role):
    """
    Add new address for user
    STRICT RULE: Maximum 3 addresses per user
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        # Get required fields
        full_name = data.get('full_name', '').strip()
        phone = data.get('phone', '').strip()
        street = data.get('street', '').strip()
        city = data.get('city', '').strip()
        state = data.get('state', '').strip()
        postal_code = data.get('postal_code', '').strip()
        country = data.get('country', 'India').strip()
        
        # Validation
        if not all([full_name, phone, street, city, state, postal_code]):
            return jsonify({'error': 'All fields (full_name, phone, street, city, state, postal_code) are required'}), 400
        
        if not validate_phone(phone):
            return jsonify({'error': 'Invalid phone number. Must be 10 digits.'}), 400
        
        db = request.app.mongo.db
        user_oid = ObjectId(user_id)
        
        # Check address count - STRICT RULE
        max_addresses = int(os.getenv("MAX_ADDRESSES_PER_USER", 3))
        address_count = db.addresses.count_documents({'user_id': user_oid})
        if address_count >= max_addresses:
            return jsonify({
                'error': f'Maximum {max_addresses} addresses per user allowed',
                'current_count': address_count
            }), 400
        
        # Create and insert address
        new_address = AddressModel.create(
            user_oid, full_name, phone, street, city, state, postal_code, country
        )
        result = db.addresses.insert_one(new_address)
        new_address['_id'] = result.inserted_id
        
        return jsonify({
            'message': 'Address added successfully',
            'address': objectid_to_string(new_address)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@addresses_bp.route('/<address_id>', methods=['PUT'])
@token_required
def update_address(address_id, user_id, user_role):
    """
    Update existing address
    """
    try:
        if not ObjectId.is_valid(address_id):
            return jsonify({'error': 'Invalid address ID'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        db = request.app.mongo.db
        user_oid = ObjectId(user_id)
        address_oid = ObjectId(address_id)
        
        # Check if address belongs to user
        address = db.addresses.find_one({'_id': address_oid, 'user_id': user_oid})
        if not address:
            return jsonify({'error': 'Address not found'}), 404
        
        # Prepare update data
        update_fields = {}
        
        if 'full_name' in data:
            full_name = data['full_name'].strip()
            if full_name:
                update_fields['full_name'] = full_name
        
        if 'phone' in data:
            phone = data['phone'].strip()
            if phone:
                if not validate_phone(phone):
                    return jsonify({'error': 'Invalid phone number'}), 400
                update_fields['phone'] = phone
        
        if 'street' in data and data['street'].strip():
            update_fields['street'] = data['street'].strip()
        
        if 'city' in data and data['city'].strip():
            update_fields['city'] = data['city'].strip()
        
        if 'state' in data and data['state'].strip():
            update_fields['state'] = data['state'].strip()
        
        if 'postal_code' in data and data['postal_code'].strip():
            update_fields['postal_code'] = data['postal_code'].strip()
        
        if 'country' in data and data['country'].strip():
            update_fields['country'] = data['country'].strip()
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        update_fields['updated_at'] = __import__('datetime').datetime.utcnow()
        
        # Update address
        db.addresses.update_one({'_id': address_oid}, {'$set': update_fields})
        
        # Return updated address
        updated_address = db.addresses.find_one({'_id': address_oid})
        
        return jsonify({
            'message': 'Address updated successfully',
            'address': objectid_to_string(updated_address)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@addresses_bp.route('/<address_id>', methods=['DELETE'])
@token_required
def delete_address(address_id, user_id, user_role):
    """
    Delete address
    """
    try:
        if not ObjectId.is_valid(address_id):
            return jsonify({'error': 'Invalid address ID'}), 400
        
        db = request.app.mongo.db
        user_oid = ObjectId(user_id)
        address_oid = ObjectId(address_id)
        
        # Delete address (ensure it belongs to user)
        result = db.addresses.delete_one({'_id': address_oid, 'user_id': user_oid})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Address not found'}), 404
        
        return jsonify({'message': 'Address deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
