# StockEase - Inventory Management System

StockEase is a powerful and scalable inventory management system built with Django REST Framework (DRF). It features secure JWT authentication, OTP-based email verification, Redis caching for performance optimization, and comprehensive test coverage.

## Features

- **User Authentication:** Secure JWT-based authentication with token refresh.
- **Email Verification:** OTP-based email verification for new accounts.
- **Inventory Management:** Track products, quantities, and pricing.
- **Redis Caching:** Improved performance with Redis-based caching.
- **Comprehensive Testing:** Unit tests for all major functionalities.
- **Logging:** Detailed logging for monitoring and debugging.

## Project Structure

```
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
|
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
|
├── stockease/                 # Project configuration
│   ├── __init__.py            # Initialization file
│   ├── asgi.py                # ASGI configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL routing
│   └── wsgi.py                # WSGI configuration
|
├── .dockerignore              # Docker ignore file
├── .env                       # Environment variables (not in repo)
├── .gitignore                 # Git ignore file
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker configuration
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```

## Prerequisites

Ensure you have the following installed on your system:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Git](https://git-scm.com/)

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/hamrazhakeem/stockease-api
cd stockease-api
```

### 2. Create Environment File

Create a `.env` file in the project root with the following variables:

```env
# Secret Key
SECRET_KEY=your_secret_key

# Database Configuration
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port

# Email Configuration
EMAIL_BACKEND='your_email_backend'
EMAIL_HOST='your_email_host'
EMAIL_PORT='your_email_port'
EMAIL_USE_TLS='your_email_use_tls'
EMAIL_HOST_USER='your_email@gmail.com'
EMAIL_HOST_PASSWORD='your_email_password'
DEFAULT_FROM_EMAIL='your_email@gmail.com'
```

### 3. Build and Start the Containers

Run the following command to build and start the containers:

```sh
docker-compose up --build -d
```

This will start the following containers:
- `stockease_web`: Django application
- `stockease_db`: PostgreSQL database
- `stockease_redis`: Redis cache

### 4. Run Database Migrations

```sh
docker exec -it stockease_web python manage.py migrate
```

## Running Tests

To run all unit tests:

```sh
docker exec -it stockease_web python manage.py test
```

## Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository.
2. Create a feature branch:
   ```sh
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```sh
   git commit -m 'feat: Add some feature'
   ```
4. Push to your branch:
   ```sh
   git push origin feature-name
   ```
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Django REST Framework](https://www.django-rest-framework.org/) for the powerful API toolkit
- [Redis](https://redis.io/) for high-performance caching
- [PostgreSQL](https://www.postgresql.org/) for a reliable database backend
- [Docker](https://www.docker.com/) for containerization

---