# Quick Start Guide

Get the Glass Bottles E-Commerce API up and running in minutes!

## Prerequisites

- Python 3.8+
- MongoDB (local or Atlas cloud)
- pip (Python package manager)
- Gmail account (for email verification)

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit .env file with your settings
# Minimum required:
# - MONGO_URI=mongodb://localhost:27017/glass_bottles
# - JWT_SECRET_KEY=your-secret-key-here
```

### Step 3: Prepare MongoDB

**Option A: Local MongoDB**
```bash
# Make sure MongoDB service is running
mongod
```

**Option B: MongoDB Atlas (Cloud)**
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get connection string: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/glass_bottles?retryWrites=true&w=majority`
4. Update `MONGO_URI` in `.env`

### Step 4: Start the API
```bash
python run.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 5: Test the API
```bash
# In another terminal
curl http://localhost:5000/api/home
```

---

## First Steps After Startup

### 1. Create Admin User (Manual Setup via MongoDB)

Connect to MongoDB and insert an admin user:

```javascript
use glass_bottles

db.users.insertOne({
  email: "admin@example.com",
  password: "$2b$12$...", // Use bcrypt hashed password
  full_name: "Admin User",
  role: "admin",
  is_verified: true,
  created_at: new Date(),
  updated_at: new Date()
})
```

**To generate bcrypt hash in Python:**
```python
from app.utils.auth import hash_password
password_hash = hash_password("admin_password_123")
print(password_hash)
```

### 2. Create Sample Products

```javascript
db.products.insertMany([
  {
    title: "Glass Water Bottle 500ml",
    description: "Premium borosilicate glass water bottle",
    price: 499,
    category: "water",
    capacity_ml: 500,
    stock: 100,
    images: ["https://example.com/image1.jpg"],
    is_featured: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    title: "Glass Juice Bottle 250ml",
    description: "For fresh juices",
    price: 299,
    category: "juice",
    capacity_ml: 250,
    stock: 50,
    images: ["https://example.com/image2.jpg"],
    is_featured: true,
    created_at: new Date(),
    updated_at: new Date()
  }
])
```

---

## Common API Workflows

### Workflow 1: User Registration → Login → Shopping → Order

#### 1. Register
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123",
    "full_name": "John Doe"
  }'
```

#### 2. Verify OTP
```bash
curl -X POST http://localhost:5000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "otp": "123456"  # Check email for actual OTP
  }'
```

#### 3. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123"
  }'
```

**Save the `access_token` from response**

#### 4. Browse Products
```bash
curl http://localhost:5000/api/products?category=water&limit=5
```

#### 5. Add to Cart
```bash
curl -X POST http://localhost:5000/api/cart \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "507f1f77bcf86cd799439012",
    "quantity": 2
  }'
```

#### 6. Add Address
```bash
curl -X POST http://localhost:5000/api/addresses \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "phone": "9876543210",
    "street": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001"
  }'
```

**Save the `_id` from response**

#### 7. Place Order
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "address_id": "507f1f77bcf86cd799439013"
  }'
```

#### 8. View Orders
```bash
curl http://localhost:5000/api/orders \
  -H "Authorization: Bearer <access_token>"
```

---

### Workflow 2: Admin Product Management

#### 1. Admin Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin_password_123"
  }'
```

**Save admin `access_token`**

#### 2. Create Product
```bash
curl -X POST http://localhost:5000/api/admin/products \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Premium Glass Bottle",
    "description": "High quality glass bottle",
    "price": 599,
    "category": "water",
    "capacity_ml": 1000,
    "stock": 50,
    "images": ["url1", "url2"],
    "is_featured": true
  }'
```

#### 3. Update Product
```bash
curl -X PUT http://localhost:5000/api/admin/products/507f1f77bcf86cd799439012 \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 699,
    "stock": 30
  }'
```

#### 4. View All Orders
```bash
curl http://localhost:5000/api/admin/orders \
  -H "Authorization: Bearer <admin_token>"
```

#### 5. Update Order Status
```bash
curl -X PATCH http://localhost:5000/api/admin/orders/507f1f77bcf86cd799439014/status \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Shipped"
  }'
```

---

## Configuration Tips

### Email Sending (Gmail)

1. **Generate App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password

2. **Update `.env`:**
```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
MAIL_DEFAULT_SENDER=noreply@glassbottles.com
```

### JWT Secret Key

Generate a strong secret key:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Use in `.env`:
```
JWT_SECRET_KEY=your_generated_key_here
```

### MongoDB Connection Strings

**Local MongoDB:**
```
MONGO_URI=mongodb://localhost:27017/glass_bottles
```

**MongoDB Atlas:**
```
MONGO_URI=mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/glass_bottles?retryWrites=true&w=majority
```

---

## Troubleshooting

### "Connection refused" for MongoDB
```bash
# Make sure MongoDB is running
# On Windows (if installed as service):
net start MongoDB

# Or start mongod manually:
mongod
```

### "Port 5000 already in use"
```bash
# Change port in .env:
FLASK_PORT=5001

# Then start:
python run.py
```

### Email not sending
1. Check `.env` email configuration
2. Verify Gmail App Password (not regular password)
3. Ensure "Less secure apps" is enabled if using regular password
4. Check email logs: `print()` statements in `app/utils/email.py`

### JWT Token errors
- Token might have expired (24 hours validity)
- Ensure token is passed in Authorization header correctly
- Format: `Authorization: Bearer <token>`

---

## Testing Endpoints with Postman

1. **Import Collection:**
   - Create a new Postman collection
   - Add the following requests:

2. **Authentication:**
   - `POST http://localhost:5000/api/auth/signup`
   - `POST http://localhost:5000/api/auth/verify-otp`
   - `POST http://localhost:5000/api/auth/login`

3. **Products:**
   - `GET http://localhost:5000/api/home`
   - `GET http://localhost:5000/api/products`
   - `GET http://localhost:5000/api/products/{id}`

4. **Cart (Set Authorization header with Bearer token):**
   - `GET http://localhost:5000/api/cart`
   - `POST http://localhost:5000/api/cart`
   - `PUT http://localhost:5000/api/cart/{item_id}`
   - `DELETE http://localhost:5000/api/cart/{item_id}`

5. **Admin (Use admin token):**
   - `GET http://localhost:5000/api/admin/products`
   - `POST http://localhost:5000/api/admin/products`
   - `GET http://localhost:5000/api/admin/orders`

---

## Next Steps

1. **Customize Business Logic:**
   - Modify price calculations
   - Update validation rules
   - Add additional fields to models

2. **Integrate Frontend:**
   - Use the API endpoints in your React/Vue.js frontend
   - Handle authentication tokens
   - Implement proper error handling

3. **Deploy:**
   - Deploy to Heroku, AWS, or DigitalOcean
   - Use production WSGI server (Gunicorn)
   - Enable CORS if frontend is on different domain

4. **Add Features:**
   - Payment gateway integration
   - Advanced search
   - Reviews and ratings
   - Wishlist functionality

---

## Useful Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py

# Run with specific environment
FLASK_ENV=production python run.py

# Access Python shell with app context
flask shell

# Create database indexes manually
python -c "from app import create_app; app = create_app(); app.app_context().push()"

# Reset database (WARNING: deletes all data)
python -c "from app import create_app; app = create_app(); app.mongo.db.drop_all()"
```

---

## Performance Tips

1. **Enable caching** for product listing
2. **Use pagination** for large datasets
3. **Add indexes** on frequently filtered fields (already done in code)
4. **Optimize MongoDB queries** by selecting only needed fields
5. **Use connection pooling** for database connections

---

Happy coding! 🚀

For detailed API documentation, refer to [README.md](README.md)
