# KanMind Backend

## Überblick
Backend-Service für eine Kanban-Anwendung auf Basis von Django REST Framework.

## Tech-Stack
- Python 3.12+
- Django 6.1.1
- Django REST Framework 3.18.1
- drf-nested-routers 0.95.3
- SQLite (Standard in der lokalen Entwicklung)

## Voraussetzungen
- Python 3.12 oder höher
- `pip`
- Virtuelle Umgebung (empfohlen)

## Installation
```bash
git clone <repo-url>
cd KanMind-Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Konfiguration
Aktuelle Entwicklungs-Defaults:
- Datenbank: SQLite (`db.sqlite3`)
- Authentifizierung: TokenAuth (`rest_framework.authentication.TokenAuthentication`)
- Standard-Permissions: `IsAuthenticated`

Hinweis: `core/settings.py` enthält eine hartkodierte Development-`SECRET_KEY` und `DEBUG=True`.
Für Produktion eigene Umgebungsvariablen und sichere Settings verwenden.

## Datenbank initialisieren
```bash
python manage.py migrate
```

## Entwicklungsserver starten
```bash
python manage.py runserver
```

API-Basis-URL lokal: `http://127.0.0.1:8000/api/`

## Authentifizierung
Nach erfolgreicher Registrierung oder Anmeldung liefert die API ein Token.
Dieses Token in Requests setzen:

```http
Authorization: Token <dein_token>
```

## API-Endpunkte
### Auth (`/api/`)
- `POST /registration/` – Benutzer registrieren
- `POST /login/` – Benutzer anmelden
- `POST /logout/` – Benutzer abmelden (Token wird gelöscht)

### Kanban (`/api/`)
- `GET|POST /boards/`
- `GET|PATCH|DELETE /boards/{id}/`
- `GET|POST /tasks/`
- `GET|PATCH|DELETE /tasks/{id}/`
- `GET /tasks/assigned-to-me/`
- `GET /tasks/reviewing/`
- `GET /email-check/?email=<adresse>`
- `GET|POST /tasks/{task_id}/comments/`
- `GET|PATCH|DELETE /tasks/{task_id}/comments/{id}/`

## Tests
```bash
python manage.py test
```

## Projektstruktur
```text
.
├── auth_app/        # Registrierung, Login, Logout
├── kanban_app/      # Boards, Tasks, Kommentare, Berechtigungen
├── core/            # Django-Projektkonfiguration (Settings/URLs)
├── manage.py
└── requirements.txt
```

## Lizenz
Siehe `LICENSE`.
