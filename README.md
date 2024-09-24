# Kaal_Panthu_First_Project

## Overview
This is a full-featured e-commerce platform designed to provide a seamless shopping experience for users and comprehensive management tools for admins. The application includes user authentication, product management, order processing, and advanced search functionalities.

## Features

### Admin Side
- **Admin Sign In**: Secure authentication for admin users.
- **User Management**: List, block, and unblock users.
- **Category Management**: Add, edit, and soft delete categories.
- **Product Management**: 
  - Add, edit, and soft delete products.
  - Support for multiple images (minimum of 3).
  - Image cropping and resizing before upload.
- **Order Management**: 
  - List orders, change order status, and cancel orders.
  - Inventory/stock management.
- **Sales Report Generation**: Daily, weekly, and custom date reports with PDF and Excel download options.
- **Admin Dashboard**: Charts displaying sales data, best-selling products, categories, and brands.

### User Side
- **Home Page**: User-friendly layout showcasing products.
- **User Sign Up & Login**: Validation on forms with OTP verification for sign-up.
- **Product Listing**: Sorted and filtered products based on popularity, price, and ratings.
- **Product Details View**: 
  - Breadcrumbs, ratings, discounts, reviews, and stock information.
  - Image zoom functionality.
- **Profile Management**: View and edit user details, addresses, and orders.
- **Cart Management**: 
  - Add/remove products, with quantity controlled by available stock.
  - Out-of-stock products handled appropriately.
- **Checkout Process**: 
  - Cash on Delivery and online payment options.
  - Address selection during order placement.
- **Wishlist & Wallet**: Manage wishlists and handle canceled orders.
- **Error Handling**: Comprehensive error handling for sold-out items and payment failures.

## Technologies Used
- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite / PostgreSQL
- **Image Processing**: Pillow
- **Payment Integration**: Razorpay or PayPal (optional)
- **Version Control**: Git and GitHub


