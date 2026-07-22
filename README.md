# Glass Bottles E-Commerce API

A production-ready Flask backend API for a Glass Bottles e-commerce website with MongoDB integration, JWT authentication, and comprehensive e-commerce features.

## Features

### 1. **Authentication & Authorization**
- Email-based signup with OTP verification
- JWT-based login
- Role-Based Access Control (RBAC) - User vs Admin
- Password hashing with bcrypt

### 2. **User Features**
- Product browsing with filtering and pagination
- Shopping cart management (add, update, remove items)
- Address management (max 3 addresses per user)
- Order placement and history viewing
- Email notifications for verification and orders

### 3. **Admin Features**
- Complete Product CRUD operations
- Featured products management
- Order status management
- User management and viewing

### 4. **Database**
- MongoDB for data persistence
- Automatic index creation
- TTL indexes for OTP expiration
- ObjectId to string conversion for JSON compatibility

---

## Project Structure

```
glass_bottles_backend/
│
├── app/
│   ├── __init__.py              # Flask app factory and setup
│   ├── config.py                # Configuration and environment variables
│   ├── utils/
│   │   ├── auth.py              # JWT tokens, password hashing, RBAC decorators
│   │   └── email.py             # OTP and email sending utilities
│   ├── models/
│   │   ├── validators.py        # Data models and validation functions
│   │   └── __init__.py
│   ├── routes/
│   │   ├── auth_routes.py       # Signup, Login, OTP Verification
│   │   ├── product_routes.py    # Product listing and details
│   │   ├── cart_routes.py       # Cart CRUD operations
│   │   ├── address_routes.py    # Address management (max 3 per user)
│   │   ├── order_routes.py      # Order creation and history
│   │   ├── admin_routes.py      # Admin operations
│   │   └── __init__.py
│   └── models/
│       └── __init__.py
│
├── .env.example                 # Example environment variables
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
```

---

## Installation & Setup

### 1. **Clone or Extract Project**
```bash
cd glass_bottles_backend
```

### 2. **Create Virtual Environment (Optional but Recommended)**
```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Configure Environment Variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - MONGO_URI: MongoDB connection string
# - JWT_SECRET_KEY: Secret key for JWT tokens
# - MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD: Email configuration
```

**Example .env file:**
```
FLASK_ENV=development
FLASK_APP=run.py
FLASK_DEBUG=True

MONGO_URI=mongodb://localhost:27017/glass_bottles

JWT_SECRET_KEY=your-super-secret-key-change-in-production

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=noreply@glassbottles.com

OTP_EXPIRY_MINUTES=10
```

### 5. **Ensure MongoDB is Running**
```bash
# If using local MongoDB:
mongod

# Or use MongoDB Atlas cloud connection in MONGO_URI
```

### 6. **Start the Application**
```bash
python run.py
```

The API will be available at `http://localhost:5000`

---

## API Endpoints

### Authentication Routes (`/api/auth`)

#### POST `/api/auth/signup`
Register a new user with email and password. Triggers OTP verification.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully. Please verify your email.",
  "email": "user@example.com",
  "otp_sent": true
}
```

---

#### POST `/api/auth/verify-otp`
Verify user email using OTP.

**Request:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response (200):**
```json
{
  "message": "Email verified successfully"
}
```

---

#### POST `/api/auth/resend-otp`
Resend OTP to user's email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "OTP resent successfully",
  "otp_sent": true
}
```

---

#### POST `/api/auth/login`
Authenticate user and get JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user"
  }
}
```

---

### Product Routes (`/api`)

#### GET `/api/home`
Get featured products for home page.

**Response (200):**
```json
{
  "featured_products": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "title": "Glass Water Bottle",
      "price": 499,
      "capacity_ml": 500,
      "is_featured": true,
      ...
    }
  ],
  "count": 6
}
```

---

#### GET `/api/products`
List products with filtering and pagination.

**Query Parameters:**
- `category`: Filter by category
- `min_price`: Minimum price
- `max_price`: Maximum price
- `capacity`: Capacity in ml (e.g., 250, 500, 1000)
- `search`: Search by title or description
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 12)

**Example:** `GET /api/products?category=water&min_price=300&max_price=800&page=1&limit=12`

**Response (200):**
```json
{
  "products": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "title": "Glass Water Bottle",
      "description": "Premium glass water bottle",
      "price": 499,
      "category": "water",
      "capacity_ml": 500,
      "stock": 50,
      "images": ["url1", "url2"],
      "is_featured": true,
      "created_at": "2026-01-15T10:30:00",
      "updated_at": "2026-01-15T10:30:00"
    }
  ],
  "pagination": {
    "current_page": 1,
    "limit": 12,
    "total_count": 45,
    "total_pages": 4
  }
}
```

---

#### GET `/api/products/<id>`
Get detailed information for a product.

**Response (200):**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "title": "Glass Water Bottle",
  "description": "Premium glass water bottle",
  "price": 499,
  "category": "water",
  "capacity_ml": 500,
  "stock": 50,
  "images": ["url1", "url2"],
  "is_featured": true,
  "created_at": "2026-01-15T10:30:00",
  "updated_at": "2026-01-15T10:30:00"
}
```

---

### Cart Routes (`/api/cart`)
**Note:** All cart routes require authentication (Bearer token in Authorization header)

#### GET `/api/cart`
View items in user's cart.

**Response (200):**
```json
{
  "cart_items": [
    {
      "cart_item_id": "507f1f77bcf86cd799439011",
      "product_id": "507f1f77bcf86cd799439012",
      "product_title": "Glass Water Bottle",
      "product_price": 499,
      "product_image": "url",
      "quantity": 2,
      "item_total": 998
    }
  ],
  "total_items": 1,
  "total_amount": 998
}
```

---

#### POST `/api/cart`
Add item to cart.

**Request:**
```json
{
  "product_id": "507f1f77bcf86cd799439012",
  "quantity": 2
}
```

**Response (201):**
```json
{
  "message": "Item added to cart successfully",
  "product_id": "507f1f77bcf86cd799439012",
  "quantity": 2
}
```

---

#### PUT `/api/cart/<item_id>`
Update quantity of item in cart.

**Request:**
```json
{
  "quantity": 5
}
```

**Response (200):**
```json
{
  "message": "Cart item updated successfully",
  "item_id": "507f1f77bcf86cd799439011",
  "new_quantity": 5
}
```

---

#### DELETE `/api/cart/<item_id>`
Remove item from cart.

**Response (200):**
```json
{
  "message": "Item removed from cart successfully"
}
```

---

#### DELETE `/api/cart`
Clear entire cart.

**Response (200):**
```json
{
  "message": "Cart cleared successfully"
}
```

---

### Address Routes (`/api/addresses`)
**Note:** All address routes require authentication. Maximum 3 addresses per user (STRICT RULE).

#### GET `/api/addresses`
List all addresses for logged-in user.

**Response (200):**
```json
{
  "addresses": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "user_id": "507f1f77bcf86cd799439010",
      "full_name": "John Doe",
      "phone": "9876543210",
      "street": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "USA",
      "created_at": "2026-01-15T10:30:00",
      "updated_at": "2026-01-15T10:30:00"
    }
  ],
  "count": 1
}
```

---

#### POST `/api/addresses`
Add new address. **STRICT RULE:** Maximum 3 addresses per user.

**Request:**
```json
{
  "full_name": "John Doe",
  "phone": "9876543210",
  "street": "123 Main St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA"
}
```

**Response (201):**
```json
{
  "message": "Address added successfully",
  "address": {
    "_id": "507f1f77bcf86cd799439011",
    "user_id": "507f1f77bcf86cd799439010",
    "full_name": "John Doe",
    ...
  }
}
```

**Response (400) - Max addresses reached:**
```json
{
  "error": "Maximum 3 addresses per user allowed",
  "current_count": 3
}
```

---

#### PUT `/api/addresses/<id>`
Update existing address.

**Request:**
```json
{
  "phone": "9876543210",
  "city": "Los Angeles"
}
```

**Response (200):**
```json
{
  "message": "Address updated successfully",
  "address": { ... }
}
```

---

#### DELETE `/api/addresses/<id>`
Delete address.

**Response (200):**
```json
{
  "message": "Address deleted successfully"
}
```

---

### Order Routes (`/api/orders`)
**Note:** All order routes require authentication. Orders are immutable after creation (STRICT RULE).

#### POST `/api/orders`
Create new order from cart items using selected address.

**Request:**
```json
{
  "address_id": "507f1f77bcf86cd799439011"
}
```

**Response (201):**
```json
{
  "message": "Order created successfully",
  "order_id": "507f1f77bcf86cd799439012",
  "total_amount": 1498,
  "status": "Pending"
}
```

---

#### GET `/api/orders`
Get order history for logged-in user.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)

**Response (200):**
```json
{
  "orders": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "user_id": "507f1f77bcf86cd799439010",
      "address_id": "507f1f77bcf86cd799439011",
      "items": [
        {
          "product_id": "507f1f77bcf86cd799439013",
          "product_title": "Glass Water Bottle",
          "product_price": 499,
          "quantity": 2,
          "item_total": 998
        }
      ],
      "total_amount": 998,
      "status": "Pending",
      "created_at": "2026-01-15T10:30:00",
      "updated_at": "2026-01-15T10:30:00"
    }
  ],
  "pagination": { ... }
}
```

---

#### GET `/api/orders/<id>`
Get specific order details.

**Response (200):**
```json
{
  "_id": "507f1f77bcf86cd799439012",
  "user_id": "507f1f77bcf86cd799439010",
  "address_id": "507f1f77bcf86cd799439011",
  "address": { ... },
  "items": [ ... ],
  "total_amount": 998,
  "status": "Pending",
  "created_at": "2026-01-15T10:30:00",
  "updated_at": "2026-01-15T10:30:00"
}
```

---

### Admin Routes (`/api/admin`)
**Note:** All admin routes require authentication with admin role.

#### GET `/api/admin/products`
Get all products.

**Query Parameters:**
- `page`: Page number
- `limit`: Items per page

---

#### POST `/api/admin/products`
Create new product.

**Request:**
```json
{
  "title": "Glass Water Bottle",
  "description": "Premium glass bottle",
  "price": 499,
  "category": "water",
  "capacity_ml": 500,
  "stock": 100,
  "images": ["url1", "url2"],
  "is_featured": true
}
```

---

#### PUT `/api/admin/products/<id>`
Update product.

**Request:** (Any subset of fields)
```json
{
  "price": 599,
  "stock": 50,
  "is_featured": false
}
```

---

#### DELETE `/api/admin/products/<id>`
Delete product.

---

#### PATCH `/api/admin/products/<id>/featured`
Toggle featured status.

**Request:**
```json
{
  "is_featured": true
}
```

---

#### GET `/api/admin/orders`
Get all user orders with filters.

**Query Parameters:**
- `page`: Page number
- `limit`: Items per page
- `status`: Filter by status (Pending, Processing, Shipped, Delivered, Cancelled)

---

#### PATCH `/api/admin/orders/<id>/status`
Update order status.

**Request:**
```json
{
  "status": "Shipped"
}
```

**Valid statuses:** `Pending`, `Processing`, `Shipped`, `Delivered`, `Cancelled`

---

#### GET `/api/admin/users`
Get all registered users.

**Query Parameters:**
- `page`: Page number
- `limit`: Items per page

**Response includes:** User details and address count for each user

---

#### GET `/api/admin/users/<id>`
Get detailed user information including all addresses.

---

## Authentication

All protected routes require a JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

### Example Request:
```bash
curl -X GET http://localhost:5000/api/cart \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Email and password are required"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid or expired token"
}
```

### 403 Forbidden (Admin only)
```json
{
  "error": "Admin access required"
}
```

### 404 Not Found
```json
{
  "error": "Product not found"
}
```

### 409 Conflict
```json
{
  "error": "Email already registered"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Business Rules

1. **User Addresses:** Maximum 3 addresses per user (enforced at API level)
2. **Order Immutability:** Users cannot edit, modify, or cancel orders after creation
3. **Stock Management:** Product stock is automatically decreased when orders are placed
4. **Cart Clearing:** Cart is automatically cleared after successful order placement
5. **OTP Expiry:** OTPs expire after 10 minutes and are automatically deleted
6. **Email Verification:** Users must verify email before they can login

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | development, production |
| `FLASK_DEBUG` | Enable debug mode | True |
| `MONGO_URI` | MongoDB connection string | mongodb://localhost:27017/glass_bottles |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | your-secret-key |
| `MAIL_SERVER` | SMTP server address | smtp.gmail.com |
| `MAIL_PORT` | SMTP server port | 587 |
| `MAIL_USERNAME` | Email account for sending | your-email@gmail.com |
| `MAIL_PASSWORD` | Email account password | app-specific-password |
| `MAIL_DEFAULT_SENDER` | Default sender email | noreply@glassbottles.com |
| `OTP_EXPIRY_MINUTES` | OTP validity period | 10 |

---

## Gmail Setup for Email Sending

To use Gmail for sending OTPs and order confirmations:

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the generated App Password in `MAIL_PASSWORD` environment variable
4. Example configuration:
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx  (16-character app password)
   ```

---

## Testing the API

### Using Postman

1. Import endpoints as shown in API documentation
2. For protected routes, add Authorization header with Bearer token
3. Use the token received from login endpoint

### Using cURL

**Example Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

**Example Protected Route:**
```bash
curl -X GET http://localhost:5000/api/cart \
  -H "Authorization: Bearer <your_token>"
```

---

## Database Schema

### Collections

**users**
```javascript
{
  _id: ObjectId,
  email: String (unique),
  password: String (hashed),
  full_name: String,
  role: String ("user" or "admin"),
  is_verified: Boolean,
  created_at: Date,
  updated_at: Date
}
```

**products**
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  price: Number,
  category: String,
  capacity_ml: Number,
  stock: Number,
  images: [String],
  is_featured: Boolean,
  created_at: Date,
  updated_at: Date
}
```

**carts**
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  items: [
    {
      _id: ObjectId,
      product_id: ObjectId,
      quantity: Number,
      added_at: Date
    }
  ],
  created_at: Date,
  updated_at: Date
}
```

**addresses**
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  full_name: String,
  phone: String,
  street: String,
  city: String,
  state: String,
  postal_code: String,
  country: String,
  created_at: Date,
  updated_at: Date
}
```

**orders**
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  address_id: ObjectId,
  items: [
    {
      product_id: ObjectId,
      product_title: String,
      product_price: Number,
      quantity: Number,
      item_total: Number
    }
  ],
  total_amount: Number,
  status: String,
  created_at: Date,
  updated_at: Date
}
```

**otps**
```javascript
{
  _id: ObjectId,
  email: String,
  otp: String,
  created_at: Date,
  expires_at: Date (with TTL index),
  is_used: Boolean
}
```

---

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running
- Check `MONGO_URI` in `.env` file
- Verify network connectivity to MongoDB server

### JWT Token Errors
- Verify token is passed correctly in Authorization header
- Check if token has expired (24-hour expiry)
- Ensure `JWT_SECRET_KEY` matches the one used to generate the token

### Email Sending Issues
- Verify Gmail App Password is correct
- Check email configuration in `.env`
- Ensure "Less secure apps" is allowed if using regular Gmail password
- Check SMTP server and port settings

### Port Already in Use
```bash
# Change port in .env:
FLASK_PORT=5001

# Or kill process using port 5000:
# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -i :5000
kill -9 <PID>
```

---

## Future Enhancements

- Payment gateway integration (Stripe, Razorpay)
- Product reviews and ratings
- Wishlist functionality
- Discount codes and coupons
- Email notifications for order updates
- Advanced search with Elasticsearch
- Analytics and reporting
- Two-factor authentication (2FA)
- OAuth integration (Google, Facebook)
- Product inventory management dashboard

---

## License

This project is provided as-is for educational and commercial use.

---

## Support

For issues or questions, please refer to the API documentation above or check the error messages in the response payloads.

---

**Happy Coding! 🎉**
