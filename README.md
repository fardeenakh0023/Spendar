# Spendar – Smart Expense Tracker

A personal expense tracker. Users register, log in, manage expenses and categories, and review spending through summaries and charts.

- **Frontend:** HTML, CSS, vanilla JavaScript (ES modules), Chart.js, Fetch API
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, Alembic
- **Database:** MySQL
- **Auth:** server-side sessions in an HttpOnly cookie, bcrypt password hashing, CSRF token on every write request

## Project structure

```
smart-expense-tracker/
├── frontend/            static pages, css/, js/ (api.js is the only file that calls the backend)
└── backend/
    ├── app/
    │   ├── main.py            app creation, CORS, routers
    │   ├── core/              config (env vars), database engine/session, security helpers, error handling
    │   ├── models/            SQLAlchemy tables: User, UserSession, Category, Expense
    │   ├── schemas/           Pydantic request/response models (validation)
    │   ├── api/               dependencies.py (current user, CSRF) and routes/
    │   ├── services/          business rules (ownership, period boundaries, totals)
    │   └── repositories/      database queries only
    ├── migrations/            Alembic (0001_initial.py creates all tables)
    └── tests/                 pytest suite (uses an in-memory SQLite database, not your MySQL data)
```

Request flow: route -> service -> repository -> database. Routes handle HTTP, services hold rules, repositories hold queries.

## 1. Prerequisites (Windows)

- Python 3.11 or newer
- MySQL Server 8 (and MySQL Workbench or the `mysql` command line)
- Git (optional)
- A way to serve the frontend on port 5500: VS Code "Live Server" extension, or Python's built-in server (shown below)

## 2. Create the database

Open MySQL Workbench or run `mysql -u root -p`, then:

```sql
CREATE DATABASE spendar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'spendar_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON spendar.* TO 'spendar_user'@'localhost';
FLUSH PRIVILEGES;
```

## 3. Set up the backend

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend\.env` and set `DB_USER`, `DB_PASSWORD` and `DB_NAME` to match step 2. Then create the tables and start the API:

```
alembic upgrade head
uvicorn app.main:app --reload
```

Check http://localhost:8000/health (returns `{"status":"ok"}`) and http://localhost:8000/docs (interactive API docs).

## 4. Run the frontend

In a second terminal:

```
cd frontend
python -m http.server 5500
```

Open http://localhost:5500 . Use `localhost` (or `127.0.0.1`) consistently; the frontend automatically talks to the same host on port 8000 so the session cookie is sent. Opening the HTML files directly with `file://` will not work because browsers block ES modules and cookies there.

## 5. Run the tests

```
cd backend
venv\Scripts\activate
pytest
```

Tests cover registration, login, invalid credentials, logout, expired sessions, protected endpoints, CSRF, expense and category CRUD, validation, week/month/year/custom boundaries, summary totals, and user data isolation (including attempts to read or change another user's data).

## 6. API reference (prefix `/api/v1`)

All endpoints except register and login need the session cookie. POST, PATCH and DELETE also need the header `X-CSRF-Token` (returned by `/auth/login` and `/auth/me`).

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/register` | Create account (username, email, password) |
| POST | `/auth/login` | Log in with `identifier` (username or email) and `password`; sets cookie |
| POST | `/auth/logout` | End the session |
| GET | `/auth/me` | Current user and CSRF token |
| POST | `/expenses` | Create (`description`, `amount`, `category_id`, `expense_date`) |
| GET | `/expenses` | List; query: `page`, `page_size`, `start_date`, `end_date`, `category_id` |
| GET | `/expenses/{id}` | One expense |
| PATCH | `/expenses/{id}` | Update any of the fields |
| DELETE | `/expenses/{id}` | Delete |
| POST | `/categories` | Create |
| GET | `/categories` | List |
| PATCH | `/categories/{id}` | Rename |
| DELETE | `/categories/{id}` | Delete (409 if expenses still use it) |
| GET | `/dashboard/summary` | Total, count, daily average, top category |
| GET | `/dashboard/category-breakdown` | Per-category totals and percentages |
| GET | `/dashboard/history` | Period totals plus paginated expenses |

Dashboard query parameters: `period` = `week` \| `month` \| `year` \| `custom`; `ref_date` (any date inside the wanted period, default today); `start_date` and `end_date` (required for `custom`).

**Date boundaries** (all inclusive, based on the stored `expense_date`): a week runs Monday to Sunday, a month from the 1st to the last day, a year from 1 Jan to 31 Dec. Totals are always calculated by the database for the whole period, never from the rows shown on one page. Amounts are returned as strings (for example `"12.50"`) to avoid floating-point errors.

Errors always look like `{"detail": "message"}`. Other users' records return 404, so their existence is not revealed.

To try the API by hand, open `/docs`, call `POST /auth/login`, then use the returned `csrf_token` in the `X-CSRF-Token` header for write requests.

## 7. Security notes

- Passwords are hashed with bcrypt; plain text is never stored. Password max length is 72 bytes (a bcrypt limit).
- The browser only holds an HttpOnly session cookie. The database stores a SHA-256 hash of the session token, so a leaked table cannot be used to log in. Sessions expire after `SESSION_EXPIRE_MINUTES` (default 24 hours) and are deleted on logout.
- The CSRF token is kept in JavaScript memory only and re-fetched from `/auth/me` on each page load. Nothing sensitive is in localStorage (only the light/dark theme choice).
- The user ID always comes from the validated session, never from the request. Every query filters by it.
- CORS only allows the origins in `CORS_ORIGINS`.
- **Production:** serve everything over HTTPS, set `COOKIE_SECURE=true`, set `CORS_ORIGINS` to your real frontend origin, use a strong database password, and prefer serving the frontend and API under the same site. Consider rate-limiting login attempts and periodically deleting expired rows from `user_sessions`.

## 8. Troubleshooting

- **`Can't connect to MySQL server` / `Access denied`:** make sure MySQL is running, then check the `DB_*` values in `backend\.env` and that the user from step 2 exists.
- **`Unknown database 'spendar'`:** run the `CREATE DATABASE` statement from step 2.
- **`'cryptography' package is required`:** run `pip install -r requirements.txt` again (MySQL 8 password auth needs it).
- **`alembic` not found:** activate the virtual environment first (`venv\Scripts\activate`).
- **Page redirects to login immediately or "Cannot reach the server":** the backend must run on port 8000 and the frontend must be opened via `http://localhost:5500` (or `127.0.0.1`), not `file://`.
- **CORS error in the browser console:** your frontend origin must be listed in `CORS_ORIGINS` exactly (scheme, host and port), then restart uvicorn.
- **403 "Invalid or missing CSRF token":** reload the page; the token is fetched on load. Make sure write requests send `X-CSRF-Token`.
- **Logged out unexpectedly:** the session expired, or you switched between `localhost` and `127.0.0.1` (cookies are per host).
- **Port already in use:** use another port, e.g. `uvicorn app.main:app --reload --port 8001`, and update the `API_BASE` port in `frontend/js/api.js`.

## 9. Preparing for machine learning later

No ML code is included. When you are ready, add a separate `backend/app/ml/` package (`data_preprocessing.py`, `feature_engineering.py`, `train_model.py`, `predictor.py`) that reads data through `expense_repository`, plus a new route and service such as `/dashboard/forecast`. No existing CRUD code needs to change. Only add pandas, scikit-learn and joblib at that point, and only show forecasts once you have enough history and have evaluated the model.
