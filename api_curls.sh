#!/bin/bash
# ============================================================
# Glass Bottle Website - Complete API cURL Reference
# Base URL: http://localhost:5000
# Replace BASE_URL with your ngrok URL when sharing externally
# Replace TOKEN with the JWT from login response
# Replace ADMIN_TOKEN with a JWT from an admin login
# ============================================================

BASE_URL="http://localhost:5000"
TOKEN="your_user_jwt_token_here"
ADMIN_TOKEN="your_admin_jwt_token_here"

# ============================================================
# AUTH ROUTES  (/api/auth)
# ============================================================

# 1. SIGNUP
# POST /api/auth/signup
# Response 201: { "message": "User registered successfully...", "email": "...", "otp_sent": true }
# Response 400: { "error": "Email, password, and full name are required" }
# Response 409: { "error": "Email already registered" }
curl -s -X POST "$BASE_URL/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe"
  }' | python -m json.tool

echo "---"

# 2. VERIFY OTP
# POST /api/auth/verify-otp
# Response 200: { "message": "Email verified successfully" }
# Response 400: { "error": "Invalid OTP" }
curl -s -X POST "$BASE_URL/api/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": "123456"
  }' | python -m json.tool

echo "---"

# 3. RESEND OTP
# POST /api/auth/resend-otp
# Response 200: { "message": "OTP resent successfully", "otp_sent": true }
# Response 404: { "error": "User not found" }
curl -s -X POST "$BASE_URL/api/auth/resend-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }' | python -m json.tool

echo "---"

# 4. LOGIN
# POST /api/auth/login
# Response 200: { "message": "Login successful", "access_token": "eyJ...", "token_type": "Bearer",
#                 "user": { "id": "...", "email": "...", "full_name": "...", "role": "user" } }
# Response 401: { "error": "Invalid email or password" }
curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }' | python -m json.tool

echo "---"

# ============================================================
# PUBLIC PRODUCT ROUTES  (/api)
# ============================================================

# 5. GET HOME (featured products)
# GET /api/home
# Response 200: { "featured_products": [...], "count": 6 }
curl -s -X GET "$BASE_URL/api/home" | python -m json.tool

echo "---"

# 6. GET ALL PRODUCTS (with filters)
# GET /api/products
# Query params: category, min_price, max_price, capacity, search, page, limit
# Response 200: { "products": [...], "pagination": { "current_page": 1, "limit": 12, "total_count": 50, "total_pages": 5 } }
curl -s -X GET "$BASE_URL/api/products?page=1&limit=12&category=drinking&min_price=100&max_price=1000" \
  | python -m json.tool

echo "---"

# 7. GET SINGLE PRODUCT
# GET /api/products/<product_id>
# Response 200: { "id": "...", "title": "...", "price": 599, "stock": 22, ... }
# Response 404: { "error": "Product not found" }
curl -s -X GET "$BASE_URL/api/products/64f1a2b3c4d5e6f7a8b9c0d1" | python -m json.tool

echo "---"

# ============================================================
# PUBLIC CATEGORY / COLLECTION ROUTES  (/api)
# ============================================================

# 8. GET PUBLIC CATEGORIES
# GET /api/categories
# Response 200: { "categories": [ { "id": "...", "name": "Drinking", "is_visible": true } ] }
curl -s -X GET "$BASE_URL/api/categories" | python -m json.tool

echo "---"

# 9. GET PUBLIC COLLECTIONS
# GET /api/collections
# Response 200: { "collections": [ { "id": "...", "name": "Summer Collection", "product_ids": [...] } ] }
curl -s -X GET "$BASE_URL/api/collections" | python -m json.tool

echo "---"

# 10. GET PUBLIC LANDING CONTENT
# GET /api/landing-content
# Response 200: { "landing_content": { "hero_title": "...", "hero_image": "..." } }
curl -s -X GET "$BASE_URL/api/landing-content" | python -m json.tool

echo "---"

# ============================================================
# CART ROUTES  (/api/cart)  — Requires: Authorization: Bearer TOKEN
# ============================================================

# 11. GET CART
# GET /api/cart
# Response 200: { "cart_items": [ { "cart_item_id": "...", "product_id": "...", "product_title": "...",
#                 "product_price": 599, "quantity": 2, "item_total": 1198 } ],
#                 "total_items": 1, "total_amount": 1198.0 }
curl -s -X GET "$BASE_URL/api/cart" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "---"

# 12. ADD TO CART
# POST /api/cart
# Response 201: { "message": "Item added to cart successfully", "product_id": "...", "quantity": 2 }
# Response 400: { "error": "Insufficient stock. Available: 5" }
curl -s -X POST "$BASE_URL/api/cart" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "64f1a2b3c4d5e6f7a8b9c0d1",
    "quantity": 2
  }' | python -m json.tool

echo "---"

# 13. UPDATE CART ITEM QUANTITY
# PUT /api/cart/<item_id>
# Response 200: { "message": "Cart item updated successfully", "item_id": "...", "new_quantity": 3 }
curl -s -X PUT "$BASE_URL/api/cart/64f1a2b3c4d5e6f7a8b9c0d2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 3
  }' | python -m json.tool

echo "---"

# 14. REMOVE CART ITEM
# DELETE /api/cart/<item_id>
# Response 200: { "message": "Item removed from cart successfully" }
curl -s -X DELETE "$BASE_URL/api/cart/64f1a2b3c4d5e6f7a8b9c0d2" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "---"

# 15. CLEAR ENTIRE CART
# DELETE /api/cart
# Response 200: { "message": "Cart cleared successfully" }
curl -s -X DELETE "$BASE_URL/api/cart" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "---"

# 16. APPLY COUPON
# POST /api/cart/apply-coupon
# Response 200: { "message": "Coupon applied", "coupon": { "id": "...", "code": "SAVE10", "discount": 10 } }
# Response 404: { "error": "Coupon not found" }
curl -s -X POST "$BASE_URL/api/cart/apply-coupon" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SAVE10"
  }' | python -m json.tool

echo "---"

# 17. REMOVE COUPON
# DELETE /api/cart/remove-coupon
# Response 200: { "message": "Coupon removed" }
curl -s -X DELETE "$BASE_URL/api/cart/remove-coupon" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "---"

# ============================================================
# ADDRESS ROUTES  (/api/addresses)  — Requires: Authorization: Bearer TOKEN
# ============================================================

# 18. GET ALL ADDRESSES
# GET /api/addresses
# Response 200: { "addresses": [ { "id": "...", "full_name": "John Doe", "phone": "9876543210",
#                 "street": "123 Main St", "city": "Mumbai", "state": "Maharashtra",
#                 "postal_code": "400001", "country": "India" } ], "count": 1 }
curl -s -X GET "$BASE_URL/api/addresses" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "---"

# 19. ADD ADDRESS  (max 3 per user)
# POST /api/addresses
# Response 201: { "message": "Address added successfully", "address": { "id": "...", ... } }
# Response 400: { "error": "Maximum 3 addresses per user allowed", "current_count": 3 }
curl -s -X POST "$BASE_URL/api/addresses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "phone": "9876543210",
    "street": "123 Main Street",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400001",
    "country": "India"
  }' | python -m json.tool

echo "---"

# 20. UPDATE ADDRESS
# PUT /api/addresses/<address_id>
# Response 200: { "message": "Address updated successfully", "address": { ... } }
# Response 404: { "error": "Address not found" }
curl -s -X PUT "$BASE_URL/api/addresses/64f1a2b3c4d5e6f7a8b9c0d3" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Pune",
    "postal_code": "411001"
  }' | python -m json.tool

echo "---"

# 21. DELETE ADDRESS
# DELETE /api/addresses/<address_id>
# Response 200: { "message": "Address deleted successfully" }
# Response 404: { "error": "Address not found" }
curl -s -X DELETE "$BASE_URL/api/addresses/64f1a2b3c4d5e6f7a8b9c0d3" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "---"

# ============================================================
# ORDER ROUTES  (/api/orders)  — Requires: Authorization: Bearer TOKEN
# ============================================================

# 22. CREATE ORDER  (from cart + address)
# POST /api/orders
# Response 201: { "message": "Order created successfully", "order_id": "...",
#                 "total_amount": 1198.0, "status": "Pending" }
# Response 400: { "error": "Cart is empty" }
curl -s -X POST "$BASE_URL/api/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address_id": "64f1a2b3c4d5e6f7a8b9c0d3"
  }' | python -m json.tool

echo "---"

# 23. GET ORDER HISTORY
# GET /api/orders
# Query params: page, limit
# Response 200: { "orders": [...], "pagination": { "current_page": 1, "limit": 10, "total_count": 5, "total_pages": 1 } }
curl -s -X GET "$BASE_URL/api/orders?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "---"

# 24. GET ORDER DETAIL
# GET /api/orders/<order_id>
# Response 200: { "id": "...", "status": "Pending", "total_amount": 1198.0,
#                 "items": [...], "address": { ... }, "created_at": "..." }
# Response 404: { "error": "Order not found" }
curl -s -X GET "$BASE_URL/api/orders/64f1a2b3c4d5e6f7a8b9c0d4" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "---"

# ============================================================
# REVIEW ROUTES  (/api)
# ============================================================

# 25. GET PRODUCT REVIEWS  (public)
# GET /api/products/<product_id>/reviews
# Response 200: { "reviews": [ { "id": "...", "rating": 5, "comment": "Great bottle!", "created_at": "..." } ] }
curl -s -X GET "$BASE_URL/api/products/64f1a2b3c4d5e6f7a8b9c0d1/reviews" | python -m json.tool

echo "---"

# 26. ADD REVIEW  (auth required)
# POST /api/products/<product_id>/reviews
# Response 201: { "message": "Review added", "review": { "id": "...", "rating": 5, "comment": "..." } }
curl -s -X POST "$BASE_URL/api/products/64f1a2b3c4d5e6f7a8b9c0d1/reviews" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Excellent quality glass bottle!"
  }' | python -m json.tool

echo "---"

# ============================================================
# WISHLIST ROUTES  (/api)  — Requires: Authorization: Bearer TOKEN
# ============================================================

# 27. GET WISHLIST
# GET /api/wishlist
# Response 200: { "wishlist": [ { "id": "...", "product_id": "...", "created_at": "..." } ] }
curl -s -X GET "$BASE_URL/api/wishlist" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "---"

# 28. ADD TO WISHLIST
# POST /api/wishlist
# Response 201: { "message": "Added to wishlist", "item": { "id": "...", "product_id": "..." } }
curl -s -X POST "$BASE_URL/api/wishlist" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "64f1a2b3c4d5e6f7a8b9c0d1"
  }' | python -m json.tool

echo "---"

# 29. REMOVE FROM WISHLIST
# DELETE /api/wishlist/<item_id>
# Response 200: { "message": "Wishlist item removed" }
curl -s -X DELETE "$BASE_URL/api/wishlist/64f1a2b3c4d5e6f7a8b9c0d5" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "---"

# 30. TRACK AFFILIATE CLICK  (public)
# POST /api/affiliate/track-click
# Response 200: { "message": "Click tracked", "affiliate_id": "AFF123" }
curl -s -X POST "$BASE_URL/api/affiliate/track-click" \
  -H "Content-Type: application/json" \
  -d '{
    "affiliate_id": "AFF123"
  }' | python -m json.tool

echo "---"

# ============================================================
# ADMIN ROUTES  (/api/admin)  — Requires: Authorization: Bearer ADMIN_TOKEN
# All admin routes require a user with role="admin"
# ============================================================

# ---- DASHBOARD ----

# 31. DASHBOARD STATS
# GET /api/admin/dashboard/stats
# Response 200: { "stats": { "products": 42, "orders": 120, "users": 85 } }
curl -s -X GET "$BASE_URL/api/admin/dashboard/stats" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 32. DASHBOARD LOW STOCK  (products with stock < 10)
# GET /api/admin/dashboard/low-stock
# Response 200: { "low_stock": [ { "id": "...", "title": "...", "stock": 3 } ] }
curl -s -X GET "$BASE_URL/api/admin/dashboard/low-stock" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 33. DASHBOARD TOP PRODUCTS  (sorted by stock desc, limit 5)
# GET /api/admin/dashboard/top-products
# Response 200: { "top_products": [ { "id": "...", "title": "...", "stock": 200 } ] }
curl -s -X GET "$BASE_URL/api/admin/dashboard/top-products" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# ---- PRODUCT MANAGEMENT ----

# 34. ADMIN GET ALL PRODUCTS
# GET /api/admin/products
# Query params: page, limit
# Response 200: { "products": [...], "pagination": { "current_page": 1, "limit": 20, "total_count": 42, "total_pages": 3 } }
curl -s -X GET "$BASE_URL/api/admin/products?page=1&limit=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 35. ADMIN CREATE PRODUCT
# POST /api/admin/products
# Response 201: { "message": "Product created successfully", "product": { "id": "...", "title": "...", ... } }
# Response 400: { "error": "All fields (title, description, price, category, capacity_ml, stock) are required" }
curl -s -X POST "$BASE_URL/api/admin/products" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Premium Glass Bottle 500ml",
    "description": "High quality borosilicate glass bottle for daily use",
    "price": 599,
    "category": "drinking",
    "capacity_ml": 500,
    "stock": 100,
    "images": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
    "is_featured": true
  }' | python -m json.tool

echo "---"

# 36. ADMIN UPDATE PRODUCT
# PUT /api/admin/products/<product_id>
# Response 200: { "message": "Product updated successfully", "product": { ... } }
# Response 404: { "error": "Product not found" }
curl -s -X PUT "$BASE_URL/api/admin/products/64f1a2b3c4d5e6f7a8b9c0d1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 649,
    "stock": 85,
    "is_featured": false
  }' | python -m json.tool

echo "---"

# 37. ADMIN DELETE PRODUCT
# DELETE /api/admin/products/<product_id>
# Response 200: { "message": "Product deleted successfully" }
# Response 404: { "error": "Product not found" }
curl -s -X DELETE "$BASE_URL/api/admin/products/64f1a2b3c4d5e6f7a8b9c0d1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 38. ADMIN TOGGLE FEATURED
# PATCH /api/admin/products/<product_id>/featured
# Response 200: { "message": "Featured status updated", "product": { ... } }
curl -s -X PATCH "$BASE_URL/api/admin/products/64f1a2b3c4d5e6f7a8b9c0d1/featured" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_featured": true
  }' | python -m json.tool

echo "---"

# ---- ORDER MANAGEMENT (ADMIN) ----

# 39. ADMIN GET ALL ORDERS
# GET /api/admin/orders
# Query params: page, limit, status (Pending|Processing|Shipped|Delivered|Cancelled)
# Response 200: { "orders": [ { "id": "...", "status": "Pending", "total_amount": 1198,
#                 "user": { "email": "...", "full_name": "..." }, "address": {...} } ],
#                 "pagination": {...} }
curl -s -X GET "$BASE_URL/api/admin/orders?page=1&limit=20&status=Pending" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 40. ADMIN UPDATE ORDER STATUS
# PATCH /api/admin/orders/<order_id>/status
# Valid statuses: Pending, Processing, Shipped, Delivered, Cancelled
# Response 200: { "message": "Order status updated", "order": { "id": "...", "status": "Shipped", ... } }
# Response 400: { "error": "Invalid status. Must be one of: Pending, Processing, Shipped, Delivered, Cancelled" }
curl -s -X PATCH "$BASE_URL/api/admin/orders/64f1a2b3c4d5e6f7a8b9c0d4/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Shipped"
  }' | python -m json.tool

echo "---"

# 41. ADMIN UPDATE ORDER SHIPMENT (tracking)
# PATCH /api/admin/orders/<order_id>/shipment
# Response 200: { "message": "Shipment updated", "tracking_number": "TRK123456" }
curl -s -X PATCH "$BASE_URL/api/admin/orders/64f1a2b3c4d5e6f7a8b9c0d4/shipment" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tracking_number": "TRK123456",
    "carrier": "FedEx"
  }' | python -m json.tool

echo "---"

# 42. ADMIN REFUND ORDER
# POST /api/admin/orders/<order_id>/refund
# Response 200: { "message": "Refund processed" }
curl -s -X POST "$BASE_URL/api/admin/orders/64f1a2b3c4d5e6f7a8b9c0d4/refund" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 43. ADMIN SYNC TRACKING
# POST /api/admin/orders/<order_id>/sync-tracking
# Response 200: { "message": "Tracking synced" }
curl -s -X POST "$BASE_URL/api/admin/orders/64f1a2b3c4d5e6f7a8b9c0d4/sync-tracking" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 44. ADMIN GET ORDER INVOICE
# GET /api/admin/orders/<order_id>/invoice
# Response 200: { "message": "Invoice generated" }
curl -s -X GET "$BASE_URL/api/admin/orders/64f1a2b3c4d5e6f7a8b9c0d4/invoice" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 45. ADMIN EXPORT ORDERS
# GET /api/admin/orders/export
# Response 200: { "message": "Orders export ready" }
curl -s -X GET "$BASE_URL/api/admin/orders/export" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# ---- USER MANAGEMENT (ADMIN) ----

# 46. ADMIN GET ALL USERS
# GET /api/admin/users
# Query params: page, limit
# Response 200: { "users": [ { "id": "...", "email": "...", "full_name": "...", "role": "user",
#                 "is_verified": true, "address_count": 2 } ], "pagination": {...} }
curl -s -X GET "$BASE_URL/api/admin/users?page=1&limit=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 47. ADMIN GET USER DETAIL
# GET /api/admin/users/<user_id>
# Response 200: { "id": "...", "email": "...", "full_name": "...", "addresses": [...] }
# Response 404: { "error": "User not found" }
curl -s -X GET "$BASE_URL/api/admin/users/64f1a2b3c4d5e6f7a8b9c0d6" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 48. ADMIN UPDATE USER TAGS
# PATCH /api/admin/users/<user_id>/tags
# Response 200: { "message": "Tags updated" }
curl -s -X PATCH "$BASE_URL/api/admin/users/64f1a2b3c4d5e6f7a8b9c0d6/tags" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tags": ["vip", "wholesale"]
  }' | python -m json.tool

echo "---"

# ---- CATEGORY MANAGEMENT (ADMIN) ----

# 49. ADMIN GET ALL CATEGORIES  (includes hidden ones)
# GET /api/admin/categories
# Response 200: { "categories": [ { "id": "...", "name": "Drinking", "is_visible": true } ] }
curl -s -X GET "$BASE_URL/api/admin/categories" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 50. ADMIN CREATE CATEGORY
# POST /api/admin/categories
# Response 201: { "message": "Category created", "category": { "id": "...", "name": "...", "is_visible": true } }
# Response 400: { "error": "Name is required" }
curl -s -X POST "$BASE_URL/api/admin/categories" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Storage Bottles"
  }' | python -m json.tool

echo "---"

# 51. ADMIN UPDATE CATEGORY
# PUT /api/admin/categories/<category_id>
# Response 200: { "message": "Category updated" }
curl -s -X PUT "$BASE_URL/api/admin/categories/64f1a2b3c4d5e6f7a8b9c0d7" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Storage & Preservation",
    "is_visible": false
  }' | python -m json.tool

echo "---"

# 52. ADMIN DELETE CATEGORY
# DELETE /api/admin/categories/<category_id>
# Response 200: { "message": "Category deleted" }
# Response 404: { "error": "Category not found" }
curl -s -X DELETE "$BASE_URL/api/admin/categories/64f1a2b3c4d5e6f7a8b9c0d7" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# ---- COLLECTION MANAGEMENT (ADMIN) ----

# 53. ADMIN GET ALL COLLECTIONS
# GET /api/admin/collections
# Response 200: { "collections": [ { "id": "...", "name": "Summer Sale", "product_ids": [...] } ] }
curl -s -X GET "$BASE_URL/api/admin/collections" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 54. ADMIN CREATE COLLECTION
# POST /api/admin/collections
# Response 201: { "message": "Collection created", "collection": { "id": "...", "name": "...", "product_ids": [] } }
curl -s -X POST "$BASE_URL/api/admin/collections" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Summer Sale 2026"
  }' | python -m json.tool

echo "---"

# 55. ADMIN UPDATE COLLECTION
# PUT /api/admin/collections/<collection_id>
# Response 200: { "message": "Collection updated" }
curl -s -X PUT "$BASE_URL/api/admin/collections/64f1a2b3c4d5e6f7a8b9c0d8" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "End of Season Sale"
  }' | python -m json.tool

echo "---"

# 56. ADMIN DELETE COLLECTION
# DELETE /api/admin/collections/<collection_id>
# Response 200: { "message": "Collection deleted" }
curl -s -X DELETE "$BASE_URL/api/admin/collections/64f1a2b3c4d5e6f7a8b9c0d8" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 57. ADMIN ADD PRODUCTS TO COLLECTION
# POST /api/admin/collections/<collection_id>/products
# Response 200: { "message": "Products linked" }
curl -s -X POST "$BASE_URL/api/admin/collections/64f1a2b3c4d5e6f7a8b9c0d8/products" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_ids": [
      "64f1a2b3c4d5e6f7a8b9c0d1",
      "64f1a2b3c4d5e6f7a8b9c0d2"
    ]
  }' | python -m json.tool

echo "---"

# ---- COUPON MANAGEMENT (ADMIN) ----

# 58. ADMIN GET ALL COUPONS
# GET /api/admin/coupons
# Response 200: { "coupons": [ { "id": "...", "code": "SAVE10", "discount": 10 } ] }
curl -s -X GET "$BASE_URL/api/admin/coupons" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 59. ADMIN CREATE COUPON
# POST /api/admin/coupons
# Response 201: { "message": "Coupon created", "coupon": { "id": "...", "code": "SAVE10", "discount": 10 } }
curl -s -X POST "$BASE_URL/api/admin/coupons" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SAVE10",
    "discount": 10
  }' | python -m json.tool

echo "---"

# 60. ADMIN UPDATE COUPON
# PUT /api/admin/coupons/<coupon_id>
# Response 200: { "message": "Coupon updated" }
curl -s -X PUT "$BASE_URL/api/admin/coupons/64f1a2b3c4d5e6f7a8b9c0d9" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "discount": 15
  }' | python -m json.tool

echo "---"

# 61. ADMIN DELETE COUPON
# DELETE /api/admin/coupons/<coupon_id>
# Response 200: { "message": "Coupon deleted" }
curl -s -X DELETE "$BASE_URL/api/admin/coupons/64f1a2b3c4d5e6f7a8b9c0d9" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# ---- AFFILIATE MANAGEMENT (ADMIN) ----

# 62. ADMIN GET ALL AFFILIATES
# GET /api/admin/affiliates
# Response 200: { "affiliates": [ { "id": "...", "name": "Jane Smith", "email": "jane@example.com" } ] }
curl -s -X GET "$BASE_URL/api/admin/affiliates" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 63. ADMIN CREATE AFFILIATE
# POST /api/admin/affiliates
# Response 201: { "message": "Affiliate created", "affiliate": { "id": "...", "name": "...", "email": "..." } }
curl -s -X POST "$BASE_URL/api/admin/affiliates" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com"
  }' | python -m json.tool

echo "---"

# 64. ADMIN GET AFFILIATE DETAIL
# GET /api/admin/affiliates/<affiliate_id>
# Response 200: { "affiliate": { "id": "...", "name": "...", "email": "...", "payout_status": "..." } }
# Response 404: { "error": "Affiliate not found" }
curl -s -X GET "$BASE_URL/api/admin/affiliates/64f1a2b3c4d5e6f7a8b9c0e0" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 65. ADMIN MARK AFFILIATE PAYOUT
# PATCH /api/admin/affiliates/<affiliate_id>/payout
# Response 200: { "message": "Payout marked" }
curl -s -X PATCH "$BASE_URL/api/admin/affiliates/64f1a2b3c4d5e6f7a8b9c0e0/payout" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# ---- MEDIA MANAGEMENT (ADMIN) ----

# 66. ADMIN LIST MEDIA
# GET /api/admin/media
# Response 200: { "media": [ { "id": "...", "name": "img1.jpg", "url": "https://s3.../img1.jpg" } ] }
curl -s -X GET "$BASE_URL/api/admin/media" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 67. ADMIN UPLOAD MEDIA  (multipart/form-data)
# POST /api/admin/media/upload
# Response 201: { "message": "Upload successful", "media": { "id": "...", "name": "...", "url": "..." } }
curl -s -X POST "$BASE_URL/api/admin/media/upload" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@/path/to/your/image.jpg" | python -m json.tool

echo "---"

# 68. ADMIN DELETE MEDIA
# DELETE /api/admin/media/<media_id>
# Response 200: { "message": "Media deleted" }
curl -s -X DELETE "$BASE_URL/api/admin/media/64f1a2b3c4d5e6f7a8b9c0e1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# ---- LANDING CONTENT (ADMIN) ----

# 69. ADMIN GET LANDING CONTENT
# GET /api/admin/landing-content
# Response 200: { "landing_content": { "hero_title": "...", "hero_image": "...", "tagline": "..." } }
curl -s -X GET "$BASE_URL/api/admin/landing-content" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 70. ADMIN UPDATE LANDING CONTENT
# PUT /api/admin/landing-content
# Response 200: { "message": "Landing content updated" }
curl -s -X PUT "$BASE_URL/api/admin/landing-content" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hero_title": "Premium Glass Bottles",
    "hero_image": "https://example.com/hero.jpg",
    "tagline": "Pure. Sustainable. Beautiful."
  }' | python -m json.tool

echo "---"

# ---- REVIEWS / MARKETING / PAYMENTS (ADMIN) ----

# 71. ADMIN DELETE REVIEW
# DELETE /api/admin/reviews/<review_id>
# Response 200: { "message": "Review deleted" }
curl -s -X DELETE "$BASE_URL/api/admin/reviews/64f1a2b3c4d5e6f7a8b9c0e2" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 72. ADMIN ABANDONED CARTS
# GET /api/admin/marketing/abandoned-carts
# Response 200: { "abandoned_carts": [] }
curl -s -X GET "$BASE_URL/api/admin/marketing/abandoned-carts" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 73. ADMIN PAYMENT TRANSACTIONS
# GET /api/admin/payments/transactions
# Response 200: { "transactions": [] }
curl -s -X GET "$BASE_URL/api/admin/payments/transactions" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 74. ADMIN PAYMENT SETTLEMENTS
# GET /api/admin/payments/settlements
# Response 200: { "settlements": [] }
curl -s -X GET "$BASE_URL/api/admin/payments/settlements" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 75. ADMIN GET ALL SHIPMENTS
# GET /api/admin/shipments
# Response 200: { "shipments": [] }
curl -s -X GET "$BASE_URL/api/admin/shipments" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

echo "All API calls complete."


# ============================================================
# UPLOAD / MEDIA ROUTES  (/api/admin/upload & /api/admin/media)
# All require: Authorization: Bearer ADMIN_TOKEN
# ============================================================

# 76. UPLOAD SINGLE FILE (image or video)
# POST /api/admin/upload
# Form fields: file (required), folder (optional: products|homepage|media|reviews|categories)
# Response 201:
# {
#   "message": "File uploaded successfully",
#   "media": {
#     "id": "64f1a2b3...",
#     "name": "bottle.jpg",
#     "url": "https://res.cloudinary.com/your-cloud/image/upload/.../bottle.jpg",
#     "public_id": "glass-bottle/products/abc123",
#     "type": "image",
#     "format": "jpg",
#     "width": 1200,
#     "height": 800,
#     "bytes": 204800,
#     "folder": "products",
#     "uploaded_by": "...",
#     "created_at": "2026-08-08T..."
#   }
# }
curl -s -X POST "$BASE_URL/api/admin/upload" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "folder=products" | python -m json.tool

echo "---"

# Upload for homepage
curl -s -X POST "$BASE_URL/api/admin/upload" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@/path/to/hero-banner.jpg" \
  -F "folder=homepage" | python -m json.tool

echo "---"

# Upload a video
curl -s -X POST "$BASE_URL/api/admin/upload" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@/path/to/promo.mp4" \
  -F "folder=homepage" | python -m json.tool

echo "---"

# 77. UPLOAD MULTIPLE FILES (up to 10)
# POST /api/admin/upload/multiple
# Form fields: files[] (required, multiple), folder (optional)
# Response 201:
# {
#   "message": "3 file(s) uploaded and saved successfully",
#   "media": [
#     { "id": "...", "url": "...", "public_id": "...", "type": "image", ... },
#     { "id": "...", "url": "...", "public_id": "...", "type": "image", ... }
#   ],
#   "folder": "products"
# }
curl -s -X POST "$BASE_URL/api/admin/upload/multiple" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "files[]=@/path/to/img1.jpg" \
  -F "files[]=@/path/to/img2.png" \
  -F "files[]=@/path/to/img3.webp" \
  -F "folder=products" | python -m json.tool

echo "---"

# 78. DELETE FILE (removes from Cloudinary + DB)
# DELETE /api/admin/upload
# Body: { "public_id": "...", "resource_type": "image" }
# resource_type: "image" (default) | "video"
# Response 200: { "message": "File deleted successfully" }
# Response 404: { "error": "File not found or already deleted from Cloudinary" }
curl -s -X DELETE "$BASE_URL/api/admin/upload" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "public_id": "glass-bottle/products/abc123def456",
    "resource_type": "image"
  }' | python -m json.tool

echo "---"

# Delete a video
curl -s -X DELETE "$BASE_URL/api/admin/upload" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "public_id": "glass-bottle/homepage/promo_video_xyz",
    "resource_type": "video"
  }' | python -m json.tool

echo "---"

# 79. LIST ALL MEDIA (paginated)
# GET /api/admin/media
# Query params: page, limit, folder, type
# Response 200:
# {
#   "media": [
#     {
#       "id": "64f1a2b3...",
#       "name": "bottle.jpg",
#       "url": "https://res.cloudinary.com/...",
#       "public_id": "glass-bottle/products/abc123",
#       "type": "image",
#       "format": "jpg",
#       "bytes": 204800,
#       "width": 1200,
#       "height": 800,
#       "folder": "products",
#       "uploaded_by": "...",
#       "created_at": "2026-08-08T..."
#     }
#   ],
#   "pagination": {
#     "current_page": 1,
#     "limit": 20,
#     "total_count": 45,
#     "total_pages": 3
#   }
# }

# All media, newest first
curl -s -X GET "$BASE_URL/api/admin/media" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# Filter by folder: products
curl -s -X GET "$BASE_URL/api/admin/media?folder=products" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# Filter by folder: homepage
curl -s -X GET "$BASE_URL/api/admin/media?folder=homepage" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# Filter by type: images only
curl -s -X GET "$BASE_URL/api/admin/media?type=image" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# Filter by type: videos only
curl -s -X GET "$BASE_URL/api/admin/media?type=video" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# Paginate
curl -s -X GET "$BASE_URL/api/admin/media?page=2&limit=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# Combined filter: product images, page 1
curl -s -X GET "$BASE_URL/api/admin/media?folder=products&type=image&page=1&limit=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 80. GET SINGLE MEDIA RECORD
# GET /api/admin/media/<media_id>
# Response 200: { "id": "...", "url": "...", "public_id": "...", ... }
# Response 404: { "error": "Media not found" }
curl -s -X GET "$BASE_URL/api/admin/media/64f1a2b3c4d5e6f7a8b9c0d1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"

# 81. GET ALLOWED FILE TYPES & SIZE LIMITS
# GET /api/admin/upload/allowed-types
# Response 200:
# {
#   "images": { "mime_types": ["image/gif","image/jpeg","image/png","image/webp"], "max_size_mb": 10 },
#   "videos": { "mime_types": ["video/mp4","video/quicktime","video/webm"], "max_size_mb": 100 },
#   "folders": ["categories","homepage","media","products","reviews"]
# }
curl -s -X GET "$BASE_URL/api/admin/upload/allowed-types" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool

echo "---"
echo "Upload/Media API calls complete."
