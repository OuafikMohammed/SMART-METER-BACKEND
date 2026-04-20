# SmartMeter Frontend Developer Guide 1

## 1. Purpose of This Guide

This guide helps a frontend developer understand how to use the current SmartMeter backend during Sprint 1.

It covers:

- project structure
- backend setup
- database configuration
- environment variables
- migrations
- run commands
- API usage basics
- authentication flow
- Sprint 1 summary from project creation until now

## 2. Current Project Context

SmartMeter is a backend-first project built with Django and Django REST Framework.

At the current stage, Sprint 1 focuses on:

- creating the Django project
- defining the database schema
- building the first REST API structure
- setting up JWT authentication
- separating access by user role
- preparing the project for frontend integration

The frontend developer can already consume backend endpoints for login, token refresh, and energy-related resources.

## 3. Main Project Structure

From the repository root:

```text
SMARTMETER/
├── backend/
│   ├── manage.py
│   ├── settings.py
│   ├── urls.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── users/
│   │   ├── models.py
│   │   ├── admin.py
│   │   └── migrations/
│   ├── energy/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   └── utils_logging.py
├── guide_frontenddev1.md
└── .gitignore
```

Important files:

- `backend/manage.py`: Django command entrypoint
- `backend/settings.py`: main application configuration
- `backend/urls.py`: global API routes
- `backend/users/models.py`: custom user model
- `backend/energy/models.py`: core business models
- `backend/energy/views.py`: API viewsets

## 4. Backend Stack

Current backend technologies:

- Python 3.12
- Django 5.0
- Django REST Framework 3.14
- Simple JWT 5.3.1
- MySQL
- PyMySQL

Why this matters for frontend:

- authentication is token-based
- backend responses are JSON
- permissions depend on user roles
- database content drives the dashboard and energy features

## 5. Business Concepts Already Implemented

### 5.1 User Roles

The project currently uses a custom user model with two roles:

- `ADMIN`
- `RESIDENT`

Frontend impact:

- an admin can access all households and records
- a resident should only access their own household data
- the UI should conditionally show features based on the authenticated role

### 5.2 Core Models

The main entities already implemented are:

1. `User`
2. `Foyer`
3. `Consommation`
4. `Anomalie`
5. `Alerte`
6. `ConversationIA`
7. `ActionLog`

Short explanation:

- `User`: authenticated person using the app
- `Foyer`: a household/home
- `Consommation`: electricity consumption measurement
- `Anomalie`: detected abnormal usage
- `Alerte`: alert generated from an anomaly
- `ConversationIA`: AI discussion history
- `ActionLog`: audit trail of important actions

## 6. Database Configuration

### 6.1 Recommended Local Database User

Use this local database account for development:

- database name: `smartmeter_db`
- database user: `smartmeteruser`
- recommended local password: `12345`

Important:

- do not hardcode the password in source code
- store the password only in local environment variables
- `.env` is ignored by Git through the project `.gitignore`

### 6.2 MySQL Commands to Create the Database

Open MySQL as root:

```powershell
mysql -u root -p
```

Then run:

```sql
CREATE DATABASE smartmeter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'smartmeteruser'@'localhost' IDENTIFIED BY '12345';
GRANT ALL PRIVILEGES ON smartmeter_db.* TO 'smartmeteruser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 7. Environment Variables

### 7.1 Local Backend Environment File

Create this file:

- `backend/.env`

Recommended content:

```env
DEBUG=True
SECRET_KEY=dev-key-change-in-prod
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=smartmeter_db
DB_USER=smartmeteruser
DB_PASSWORD=12345
DB_HOST=localhost
DB_PORT=3306

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
DJANGO_LOG_LEVEL=INFO
```

Notes:

- `DB_PASSWORD` is intentionally stored in the environment file, not in Python code
- `.env` must stay local and must not be committed
- `CORS_ALLOWED_ORIGINS` should include the frontend URL

### 7.2 Why Environment Variables Matter

Basic idea:

- code should be the same for every developer
- secrets and machine-specific values should stay outside the code
- this avoids exposing passwords in Git history

## 8. Installation and Setup Commands

From the repository root:

```powershell
cd D:\COURS_EMSI_3ANNEE_IIR\SMARTMETER
```

Install backend dependencies:

```powershell
.\venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
```

Move into the backend folder:

```powershell
cd .\backend
```

## 9. Exact Commands for Migrations

These are the correct commands to use for this project.

### 9.1 Generate Migration Files

```powershell
..\venv\Scripts\python.exe manage.py makemigrations users energy
```

### 9.2 Apply Migrations

```powershell
..\venv\Scripts\python.exe manage.py migrate
```

### 9.3 Verify Migration Status

```powershell
..\venv\Scripts\python.exe manage.py showmigrations
```

### 9.4 Run a General Health Check

```powershell
..\venv\Scripts\python.exe manage.py check
```

Recommended order:

```powershell
..\venv\Scripts\python.exe manage.py check
..\venv\Scripts\python.exe manage.py makemigrations users energy
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py showmigrations
```

## 10. Run the Backend

From `backend/`:

```powershell
..\venv\Scripts\python.exe manage.py runserver
```

Default local server:

- [http://127.0.0.1:8000](http://127.0.0.1:8000)

Useful URLs:

- admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- login token: [http://127.0.0.1:8000/api/token/](http://127.0.0.1:8000/api/token/)
- refresh token: [http://127.0.0.1:8000/api/token/refresh/](http://127.0.0.1:8000/api/token/refresh/)

## 11. Authentication Flow for Frontend

### 11.1 Login

Endpoint:

- `POST /api/token/`

Example request body:

```json
{
  "username": "admin",
  "password": "your-password"
}
```

Example response:

```json
{
  "refresh": "jwt-refresh-token",
  "access": "jwt-access-token"
}
```

### 11.2 Use the Access Token

Send the token in the header:

```http
Authorization: Bearer <access_token>
```

### 11.3 Refresh the Token

Endpoint:

- `POST /api/token/refresh/`

Request body:

```json
{
  "refresh": "jwt-refresh-token"
}
```

## 12. Main API Endpoints for Frontend

Base API prefix:

- `/api/`

Available resource groups:

- `GET /api/foyers/`
- `GET /api/consommations/`
- `GET /api/anomalies/`
- `GET /api/alertes/`
- `POST /api/alertes/{id}/acquitter/`
- `GET /api/conversations-ia/`
- `POST /api/conversations-ia/ask/`

Frontend usage examples:

- dashboard household list: `/api/foyers/`
- charts and usage history: `/api/consommations/`
- anomaly cards: `/api/anomalies/`
- alerts panel: `/api/alertes/`

## 13. Suggested Frontend Integration Workflow

Recommended steps for the frontend developer:

1. Run the backend locally.
2. Confirm `/api/token/` works.
3. Log in with a test user and save the JWT.
4. Test protected endpoints with the `Authorization` header.
5. Build API service functions in the frontend.
6. Separate screens by role when needed.
7. Handle loading, empty, and unauthorized states correctly.

## 14. Basic Concepts the Frontend Should Keep in Mind

### 14.1 JWT

JWT is the token returned after login.

Frontend responsibility:

- store it safely for the session
- attach it to protected requests
- refresh it when needed

### 14.2 Role-Based Access

Not every user sees the same data.

Frontend responsibility:

- show admin-only views only to admins
- avoid assuming all endpoints return the same scope for all users

### 14.3 Migrations

A migration is the Django way of evolving database structure safely.

Frontend impact:

- when new fields are added, frontend payloads and screens may need updates
- backend and database must be migrated before testing new API features

### 14.4 Audit Logging

Some actions are logged in `ActionLog`.

Why it matters:

- sensitive operations may be tracked
- this supports traceability and admin monitoring

## 15. Sprint 1 Summary

### 15.1 What Was Done From Project Creation Until Now

Sprint 1 delivered the backend foundation of SmartMeter.

Completed work:

1. A Django project was initialized.
2. The backend configuration was separated into a working SmartMeter settings file.
3. Django apps were structured correctly into `users` and `energy`.
4. A custom user model was added with role management.
5. Core business entities were modeled for households, consumption, anomalies, alerts, AI conversations, and audit logs.
6. REST serializers were created to expose model data as JSON.
7. API viewsets and routing were added for the first functional endpoints.
8. JWT authentication endpoints were connected.
9. Role-based access behavior was prepared for `ADMIN` and `RESIDENT`.
10. MySQL-compatible configuration was set up through environment variables.
11. Initial migrations were generated successfully.
12. Migrations were applied successfully.
13. Repository hygiene was improved with a project `.gitignore`.

### 15.2 What Sprint 1 Means in Simple Terms

By the end of Sprint 1:

- the project has a usable backend skeleton
- the data model exists
- the database can be created and migrated
- the frontend has endpoints to start integrating against
- authentication is in place
- the project is ready for UI and API consumption work in the next sprint

## 16. What the Frontend Developer Can Do Next

Good next steps:

1. Build the login page using `/api/token/`.
2. Create a shared API client with JWT support.
3. Create dashboard screens for foyers, consommations, anomalies, and alertes.
4. Add role-aware navigation and route protection.
5. Align UI field names with API response fields.

## 17. Final Reminder

For local development:

- keep `backend/.env` private
- use `smartmeteruser` for the local DB connection
- remember the recommended local dev password is `12345`
- always run migrations before testing new backend changes
