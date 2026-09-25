# KanMind Backend

## Overview
Backend service for a Kanban application built with Django REST Framework.

## Tech Stack
- Python 3.12+
- Django 6.1.1
- Django REST Framework 3.18.1
- drf-nested-routers 0.95.3
- SQLite (default for local development)

## Prerequisites
- Python 3.12 or higher
- `pip`
- Virtual environment (recommended)

## Installation
```bash
git clone YOUR_REPO_URL
cd KanMind-Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration
Current development defaults:
- Database: SQLite (`db.sqlite3`)
- Authentication: TokenAuth (`rest_framework.authentication.TokenAuthentication`)
- Default permissions: `IsAuthenticated`

Note: `core/settings.py` currently contains a hardcoded development `SECRET_KEY` and `DEBUG=True`.
For production, use environment variables and secure settings.

## Initialize the Database
```bash
python manage.py migrate
```

## Start the Development Server
```bash
python manage.py runserver
```

Local API base URL: `http://127.0.0.1:8000/api/`

## Authentication
After successful registration or login, the API returns a token.
Use this token in request headers:

```http
Authorization: Token YOUR_TOKEN
```

## API Endpoints
### Auth (`/api/`)
- `POST /registration/` – Register a user
- `POST /login/` – Log in a user
- `POST /logout/` – Log out a user (token is deleted)

### Kanban (`/api/`)
- `GET|POST /boards/`
- `GET|PATCH|DELETE /boards/{id}/`
- `GET|POST /tasks/`
- `GET|PATCH|DELETE /tasks/{id}/`
- `GET /tasks/assigned-to-me/`
- `GET /tasks/reviewing/`
- `GET /email-check/?email=user@example.com`
- `GET|POST /tasks/{task_id}/comments/`
- `GET|PATCH|DELETE /tasks/{task_id}/comments/{id}/`

## Tests
```bash
python manage.py test
```

## Project Structure
```text
.
├── auth_app/        # Registration, login, logout
├── kanban_app/      # Boards, tasks, comments, permissions
├── core/            # Django project configuration (settings/URLs)
├── manage.py
└── requirements.txt
```

## License
See `LICENSE`.
