# Ecommerce Django Project

This is a full-featured ecommerce website built using Django, Docker, postgresql and Celery. The project supports user authentication, shopping cart functionality, coupon management, orders, and PayPal integration and more .

## Features

- **User Authentication and OTP Verification**: 
  - User registration, login, logout, and password reset functionality.
  - OTP (One-Time Password) verification for email confirmation.

- **Basket Management**: 
  - Users can add, remove, and update products in their shopping cart.

- **Session-Based Shopping Cart**: 
  - Users can browse and add products to the cart without logging in, with items stored in the session.

- **Coupon System**: 
  - Apply discount codes during checkout for order discounts.
  - Validate coupon expiration dates and usage limits.

- **Product Management**: 
  - Display a catalog of products with details like price, category, and specifications.
  - Filter and sort products based on price (high to low, low to high), newest, oldest, and most viewed.
  - Product categories and subcategories allow users to easily browse products.

- **Order and Payment Management**: 
  - Users can place orders and choose from different payment methods.
  - PayPal payment integration for secure online transactions.
  - Manage order status and track payment confirmation.

- **Order History and Receipts**: 
  - Users can view their past orders and download order receipts.
  - Receipts contain details about purchased items, discounts applied, and payment status.

- **Review and Rating System**: 
  - Users can leave reviews and ratings for products.

- **Shipping and Address Management**: 
  - Users can provide multiple shipping addresses and select the preferred one at checkout.
  - Shipping options (e.g., express, standard) can be selected during checkout.

- **Celery for Background Tasks**: 
  - Asynchronous task handling for sending emails (e.g., order confirmations, OTP codes).
  - Scheduled tasks (via Celery Beat) for periodic actions, like cleaning up expired coupons.

- **Admin Panel Customization**: 
  - Manage users, products, orders, coupons, and reviews via Django’s admin interface.
  - Admin control over distribution.
  
- **Dockerized Setup**: 
  - The entire project is Dockerized for easy setup and deployment, ensuring consistent development environments.
  
- **Analytics**: 
  - Track product views and sort products by popularity (most viewed).

## Setup Instructions

### Prerequisites

    - **Docker** and **Docker Compose** (for containerization)
    - **Python 3.12.x** (for running the Django project)
    - **Django 5.x**
    - **PostgreSQL** (as the database for the project)
    - **Celery** (for background task processing)
    - **RabbitMQ** (as the message broker for Celery)

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Roozbeho/django-ecommerce.git
    ```

2. **Set up environment variables**: Create a .env file with the required settings. An example .env file:
    ```bash
    EMAIL_HOST_USER=your_email_host_user
    EMAIL_HOST_PASSWORD=your_email_host_password
    DEFAULT_EMAIL_FROM=your_default_email
    PAYPAL_CLIENT_ID=your_paypal_client_id
    PAYPAL_CLIENT_SECRET=your_paypal_client_secret
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=your_db_host
    DB_PORT=your_db_port
    CELERY_BROKER_URL=your_celery_broker_url
    ```
3. **Build and run the Docker containers**:
    ```bash
    docker-compose up --build
    ```
4. **Access the application at http://localhost:8000**


## Contributions

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull request. 