# Circle (InnerCircle) — v1.0

Minimal scaffold for the InnerCircle Django project (Bootstrap, PostgreSQL-ready).

Quick setup

1. Create a virtual env and activate it (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set PostgreSQL env vars or use SQLite for quick testing. Example env vars:

```powershell
$env:DB_NAME='innercircle_db'
$env:DB_USER='youruser'
$env:DB_PASSWORD='yourpass'
$env:DB_HOST='localhost'
$env:DB_PORT='5432'
```

3. Make migrations and runserver:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Project layout

- `config/` Django project settings
- `innercircle/` core app (models, views, templates)
- `README_PROJECT_DOC.md` Project documentation scaffold (Normas)

Notes

- This is a starter scaffold: expand views, templates, static assets and tests.
