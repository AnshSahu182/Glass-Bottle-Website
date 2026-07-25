# API Reference

## Public APIs

### 1) Signup
- **POST** `/api/auth/signup`
- **Payload**
  ```json
  {
    "email": "user@example.com",
    "password": "123456",
    "full_name": "John Doe"
  }
  ```
- **Response**
  ```json
  {
    "message": "User registered successfully. Please verify your email.",
    "email": "user@example.com",
    "otp_sent": true
  }
  ```

### 2) Verify OTP
- **POST** `/api/auth/verify-otp`
- **Payload**
  ```json
  {
    "email": "user@example.com",
    "otp": "123456"
  }
  ```
- **Response**
  ```json
  {
    "message": "Email verified successfully"
  }
  ```

### 3) Login
- **POST** `/api/auth/login`
- **Payload**
  ```json
  {
    "email": "user@example.com",
    "password": "123456"
  }
  ```
- **Response**
  ```json
  {
    "access_token": "<jwt_token>",
    "token_type": "Bearer",
    "user": {
      "email": "user@example.com",
      "role": "user"
    }
  }
  ```

### 4) Home products
- **GET** `/api/home`
- **Response**
  ```json
  {
    "featured_products": []
  }
  ```

### 5) List products
- **GET** `/api/products`
- **Query Params**: `category`, `min_price`, `max_price`, `capacity`, `page`, `limit`
- **Response**
  ```json
  {
    "products": [],
    "pagination": {
      "current_page": 1,
      "total_pages": 1
    }
  }
  ```

### 6) Product details
- **GET** `/api/products/<id>`
- **Response**
  ```json
  {
    "_id": "<product_id>",
    "title": "Glass Bottle",
    "price": 299
  }
  ```

---

## Protected APIs

> Use `Authorization: Bearer <token>` header.

### 1) Get cart
- **GET** `/api/cart`
- **Response**
  ```json
  {
    "cart_items": [],
    "total_items": 0,
    "total_amount": 0
  }
  ```

### 2) Add to cart
- **POST** `/api/cart`
- **Payload**
  ```json
  {
    "product_id": "<product_id>",
    "quantity": 2
  }
  ```
- **Response**
  ```json
  {
    "message": "Item added to cart successfully"
  }
  ```

### 3) Update cart item
- **PUT** `/api/cart/<item_id>`
- **Payload**
  ```json
  {
    "quantity": 3
  }
  ```
- **Response**
  ```json
  {
    "message": "Cart item updated successfully"
  }
  ```

### 4) Delete cart item
- **DELETE** `/api/cart/<item_id>`
- **Response**
  ```json
  {
    "message": "Item removed from cart successfully"
  }
  ```

### 5) Get addresses
- **GET** `/api/addresses`
- **Response**
  ```json
  {
    "addresses": []
  }
  ```

### 6) Add address
- **POST** `/api/addresses`
- **Payload**
  ```json
  {
    "full_name": "John Doe",
    "phone": "9876543210",
    "street": "123 Main St",
    "city": "Delhi",
    "state": "DL",
    "postal_code": "110001"
  }
  ```
- **Response**
  ```json
  {
    "message": "Address added successfully"
  }
  ```

### 7) Create order
- **POST** `/api/orders`
- **Payload**
  ```json
  {
    "address_id": "<address_id>"
  }
  ```
- **Response**
  ```json
  {
    "message": "Order created successfully",
    "order_id": "<order_id>",
    "status": "Pending"
  }
  ```

### 8) Get orders
- **GET** `/api/orders`
- **Response**
  ```json
  {
    "orders": []
  }
  ```

### 9) Wishlist
- **GET** `/api/wishlist`
- **POST** `/api/wishlist`
- **DELETE** `/api/wishlist/<item_id>`

### 10) Reviews
- **GET** `/api/products/<product_id>/reviews`
- **POST** `/api/products/<product_id>/reviews`

### 11) Payments and tracking
- **POST** `/api/orders/<order_id>/razorpay-order`
- **POST** `/api/orders/<order_id>/verify-payment`
- **GET** `/api/orders/<order_id>/tracking`

---

## Admin APIs

> Use admin token in `Authorization` header.

### 1) Create product
- **POST** `/api/admin/products`
- **Payload**
  ```json
  {
    "title": "New Bottle",
    "description": "Premium bottle",
    "price": 399,
    "category": "water",
    "capacity_ml": 500,
    "stock": 50,
    "images": ["image1.jpg"],
    "is_featured": true
  }
  ```
- **Response**
  ```json
  {
    "message": "Product created successfully"
  }
  ```

### 2) Update order status
- **PATCH** `/api/admin/orders/<id>/status`
- **Payload**
  ```json
  {
    "status": "Shipped"
  }
  ```
- **Response**
  ```json
  {
    "message": "Order status updated"
  }
  ```

### 3) Categories and collections
- **GET** `/api/categories`
- **GET** `/api/collections`
- **POST** `/api/admin/categories`
- **POST** `/api/admin/collections`
- **POST** `/api/admin/collections/<collection_id>/products`

### 4) Coupons, affiliates, and media
- **GET** `/api/admin/coupons`
- **POST** `/api/admin/coupons`
- **GET** `/api/admin/affiliates`
- **POST** `/api/admin/media/upload`
- **GET** `/api/admin/media`

### 5) Dashboard and exports
- **GET** `/api/admin/dashboard/stats`
- **GET** `/api/admin/dashboard/low-stock`
- **GET** `/api/admin/dashboard/top-products`
- **GET** `/api/admin/orders/export`
- **GET** `/api/admin/orders/<order_id>/invoice`
