# Django Wallet

A simple wallet application built with Django, SQLAlchemy, and PostgreSQL, featuring REST API endpoints for wallet operations. Includes functional tests with pytest and load testing with Locust.

## Features
- Create wallets with an initial balance.
- Get wallet balance (`GET /api/v1/wallets/<wallet_id>/`).
- Perform deposit/withdrawal operations (`POST /api/v1/wallets/<wallet_id>/operation`).
- Functional tests covering success and error cases.
- Load testing with Locust.

## Prerequisites
- Docker
- Docker Compose
- Git

## Setup and Installation

### 1. Clone the Repository

git clone https://github.com/<username>/<repository>.git
cd <repository>

### 2. Build and Run with Docker Compose

docker-compose up --build --force-recreate -d
db: PostgreSQL database (walletdb).
web: Django application on http://localhost:8000.
locust: Load testing tool on http://localhost:8089.

### 3. Verify Services
docker-compose ps  # Check all services are "Up"
docker-compose logs web  # Uvicorn should be running on 0.0.0.0:8000
docker-compose logs locust  # Web interface at http://localhost:8089
Running Functional Tests

docker-compose exec web pytest wallet/tests.py -v
Expected output: 8 passed.

Running Load Tests with Locust
Open http://localhost:8089 in your browser.
Configure:
Number of users: 250
Spawn rate: 50 users/second
Host: http://web:8000 (preconfigured)
Click "Start swarming" to begin load testing.

## Project Structure
<repository>/
├── wallet/              # Django app with models, views, and tests
│   ├── database.py      # SQLAlchemy table definition
│   ├── tests.py         # Functional tests
│   └── ...
├── locustfile.py        # Locust load testing script
├── Dockerfile           # Dockerfile for web service
├── Dockerfile.locust    # Dockerfile for Locust service
├── docker-compose.yml   # Docker Compose configuration
├── requirements.txt     # Python dependencies
└── README.md            # This file

## Notes

Ensure Docker is running before executing commands.
The PostgreSQL database is persisted in the postgres_data volume.
Load tests simulate wallet balance checks, deposits, and withdrawals.
Contributing
Feel free to fork this repository, submit issues, or create pull requests!
