# Spendar backend

FastAPI + SQLAlchemy + Alembic + MySQL. See the root `README.md` for full setup, run, test and troubleshooting steps.

Quick start (Windows, from this folder):

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Interactive API docs: http://localhost:8000/docs
