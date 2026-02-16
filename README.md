# 📚 Library Service API 

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python)
![Django](https://img.shields.io/badge/Django-6.0.1-green?style=flat&logo=django)
![DRF](https://img.shields.io/badge/DRF-Rest_Framework-red?style=flat)
![Celery](https://img.shields.io/badge/Celery-Task_Queue-orange?style=flat&logo=celery)
![Redis](https://img.shields.io/badge/Redis-Broker-red?style=flat&logo=redis)
![Docker](https://img.shields.io/badge/Docker-Container-blue?style=flat&logo=docker)
![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?style=flat&logo=stripe)
![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=flat&logo=swagger&logoColor=white&color=85EA2D)


## About Project

**Library API Service** is a comprehensive RESTful API designed to streamline library operations, from inventory management to automated borrowing flows and payment processing.

Built with **Django REST Framework**, this project focuses on scalability and data integrity, featuring asynchronous background tasks for real-time status updates and notifications.

## ✨ Key Features

* **📖 Book Inventory:** Complete CRUD operations for managing books and tracking stock availability.
* **🔄 Smart Borrowing System:**
    * Automated stock validation.
    * **Debt Control:** Prevents users with pending payments from borrowing new books.
* **💸 Advanced Stripe Payments:**
    * Integration with **Stripe Checkout Sessions**.
    * **Automated Expiration Tracking:** Celery tasks monitor Stripe sessions every minute to mark unpaid transactions as `EXPIRED`.
    * **Payment Renewal:** Dedicated endpoint to regenerate valid payment links for expired sessions.
* **🤖 Asynchronous Tasks (Celery + Redis):**
    * Daily checks for overdue borrowings.
    * Real-time payment status synchronization.
* **📢 Notifications:** Integrated **Telegram Bot** for instant alerts on overdue books.
* **🐳 Containerization:** Fully Dockerized environment for easy deployment (App, DB, Redis, Celery Worker/Beat).


## 🚀 Getting Started

### Prerequisites

* Docker
* Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/Psychox1k/library_service_api
cd library_service_api
```


### 2. Environment Configuration
Create a .env file in the project root directory and add the following variables:

```
# Django
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Stripe
STRIPE_SECRET_KEY=your_stripe_key

# Database
POSTGRES_DB=library_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```
### 3. Build and Run (Docker)
Start the application with Docker Compose:

```Bash
docker compose up --build
```


## ⚙️ Initial Setup
Once the containers are running, open a new terminal window to perform these steps.

### Apply Migrations
(Usually applied automatically via entrypoint, but if needed manually):

```Bash

docker compose exec app python manage.py migrate
```
### Create Superuser (Admin)
To access the Django Admin panel:

```Bash

docker compose exec app python manage.py createsuperuser
```
## Load Demo Data
Populate the database with initial book inventory:

```Bash
docker compose exec app python manage.py loaddata library_data.json
```

## 📚 Documentation
The project includes auto-generated API documentation. Once the server is running, you can access it here:

Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/

Redoc: http://127.0.0.1:8000/api/schema/redoc/

The API root will be available at: http://127.0.0.1:8000/api/


## 🧪 Running Tests
To run the test suite inside the Docker container:

```Bash
docker compose exec app python manage.py test
```

## Developed by:
- [Kyrylo Zhyhariev](https://github.com/Psychox1k)

