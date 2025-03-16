StockEase - Inventory Management System
StockEase is a robust inventory management system built with Django REST Framework, featuring JWT authentication, Redis caching, and comprehensive test coverage.
Features
User Authentication: Secure JWT-based authentication with token refresh
Email Verification: OTP-based email verification for new accounts
Inventory Management: Track products, quantities, and pricing
Redis Caching: Performance optimization with Redis-based caching
Comprehensive Testing: Unit tests for all major functionality
Logging: Detailed logging for monitoring and debugging

Project Structure

stockease/
├── accounts/                  # User authentication and management
│   ├── migrations/            # Database migrations for accounts
│   ├── utils/                 # Utility functions
│   │   ├── email_utils.py     # Email sending utilities
│   │   └── redis_utils.py     # Redis operations for OTP
│   ├── __init__.py            # Initialization file
│   ├── admin.py               # Admin configuration
│   ├── apps.py                # App configuration
│   ├── models.py              # User model definition
│   ├── permissions.py         # Custom permission classes
│   ├── serializers.py         # API serializers
│   ├── tests.py               # Unit tests for accounts
│   ├── urls.py                # URL routing for auth endpoints
│   ├── user_urls.py           # URL routing for user management
│   └── views.py               # API views for authentication
├── inventory/                 # Inventory management
│   ├── migrations/            # Database migrations for inventory
│   ├── utils/                 # Utility functions
│   │   └── cache_utils.py     # Caching utilities
│   ├── __init__.py            # Initialization file
│   ├── admin.py               # Admin configuration
│   ├── apps.py                # App configuration
│   ├── models.py              # Product model definition
│   ├── permissions.py         # Custom permission classes
│   ├── serializers.py         # API serializers
│   ├── tests.py               # Unit tests for inventory
│   ├── urls.py                # URL routing
│   └── views.py               # API views for inventory
├── stockease/                 # Project configuration
│   ├── __init__.py            # Initialization file
│   ├── asgi.py                # ASGI configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL routing
│   └── wsgi.py                # WSGI configuration
├── .dockerignore              # Docker ignore file
├── .env                       # Environment variables (not in repo)
├── .gitignore                 # Git ignore file
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker configuration
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies

Prerequisites
Docker and Docker Compose
Git

Setup Instructions
1. Clone the Repository
git clone https://github.com/hamrazhakeem/stockease-api
cd stockease-api

2. Create Environment File
Create a .env file in the project root with the following variables:

# Secret Key
SECRET_KEY=your_secret_key

# Database Configuration
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port

# Email Configuration
EMAIL_BACKEND = 'your_email_backend'
EMAIL_HOST = 'your_email_host' 
EMAIL_PORT = 'your_email_port'
EMAIL_USE_TLS = 'your_email_use_tls'
EMAIL_HOST_USER = 'your_email@gmail.com'  
EMAIL_HOST_PASSWORD = 'your_email_password' 
DEFAULT_FROM_EMAIL = 'your_email@gmail.com'

3. Build and Start the Containers
docker-compose up --build -d

This will start three containers:
stockease_web: Django application
stockease_db: PostgreSQL database
stockease_redis: Redis cache

4. Run Migrations
docker exec -it stockease_web python manage.py migrate

Contributing
Fork the repository
Create a feature branch: git checkout -b feature-name
Commit your changes: git commit -m 'Add some feature'
Push to the branch: git push origin feature-name
Submit a pull request
License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgements
Django REST Framework for the powerful API toolkit
Redis for the high-performance caching
PostgreSQL for the reliable database backend
Docker for the containerization