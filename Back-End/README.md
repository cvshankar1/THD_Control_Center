# THD HR Control Center — Backend

**FastAPI + PostgreSQL backend for the THD HR Control Center**
Student Project · Challenge 6 · Applied AI for Digital Production Management · SS 2025

---

## Quick Start (5 minutes)

### 1. PostgreSQL — create the database

```sql
-- Run in psql as superuser
CREATE DATABASE thd_hr;
CREATE USER thd_user WITH PASSWORD 'thd_password';
GRANT ALL PRIVILEGES ON DATABASE thd_hr TO thd_user;
```

### 2. Install dependencies

```bash
cd thd_hr_backend
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your database URL and SMTP credentials
```

### 4. Create tables and seed demo data

```bash
python seed.py
```

### 5. Start the server

```bash
uvicorn main:app --reload --port 8000
```

The API is now live at **http://localhost:8000**

| Page | URL |
|------|-----|
| Swagger UI (interactive docs) | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health check | http://localhost:8000/health |

---

## Connect the Frontend

Open `THD_HR_Control_Center_v3.html` in a browser, go to **Settings → API Base URL** and enter:

```
http://localhost:8000
```

Click **Test Connection** — it should turn green. The frontend will now use real data from PostgreSQL instead of demo data.

---

## API Overview

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Sign in, get JWT token |
| `GET`  | `/api/auth/me` | Get current user profile |
| `POST` | `/api/auth/logout` | Sign out (client discards token) |

### Users (Admin only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`    | `/api/users/` | List all users |
| `POST`   | `/api/users/` | Create user |
| `PATCH`  | `/api/users/{id}` | Update user |
| `DELETE` | `/api/users/{id}` | Delete user |

### Jobs
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET`    | `/api/jobs/` | List jobs (filtered by role) | All |
| `GET`    | `/api/jobs/public` | External + published jobs | Public |
| `POST`   | `/api/jobs/` | Create job | Admin |
| `PUT`    | `/api/jobs/{id}` | Update job | Admin / Dept Head |
| `PATCH`  | `/api/jobs/{id}/review` | Approve or reject | Dept Head / Admin |
| `PATCH`  | `/api/jobs/{id}/promote` | Promote to external | Admin |
| `PATCH`  | `/api/jobs/{id}/close` | Close job | Admin |
| `DELETE` | `/api/jobs/{id}` | Delete job | Admin |

### Applications
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET`    | `/api/applications/` | List applications | Auth |
| `POST`   | `/api/applications/submit` | Submit application (public portal) | Public |
| `POST`   | `/api/applications/` | Add application (internal) | Auth |
| `PATCH`  | `/api/applications/{id}/stage` | Update stage + trigger email | Auth |
| `PATCH`  | `/api/applications/{id}/score` | Update score | Auth |
| `DELETE` | `/api/applications/{id}` | Delete | Admin |

### Statistics & Notices
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/stats/dashboard` | Dashboard KPI counts |
| `GET` | `/api/notices/` | Activity log |
| `DELETE` | `/api/notices/` | Clear log (Admin) |

---

## Automatic Email Triggers

| Event | Recipient | Triggered by |
|-------|-----------|--------------|
| Application submitted | Applicant | `POST /api/applications/submit` |
| Stage → Interview | Applicant | `PATCH /stage` with `stage=interview` |
| Stage → Contract | Applicant | `PATCH /stage` with `stage=contract` |
| Job created | Dept Head(s) | `POST /api/jobs/` |

Set `EMAIL_ENABLED=true` in `.env` to activate real SMTP sending.
During development, emails are logged to the console instead.

---

## Role Permissions Summary

| Permission | Admin | Dept Head | Faculty |
|-----------|-------|-----------|---------|
| Create jobs | ✅ | ❌ | ❌ |
| Edit jobs (own dept) | ✅ | ✅ | ❌ |
| Delete jobs | ✅ | ❌ | ❌ |
| Approve / reject jobs | ✅ | ✅ (own dept) | ❌ |
| Promote job to external | ✅ | ❌ | ❌ |
| View all applications | ✅ | Dept only | Dept only |
| Update candidate stages | ✅ | ✅ (dept) | ✅ (dept) |
| View analytics | ✅ | ❌ | ❌ |
| Manage users | ✅ | ❌ | ❌ |

---

## Project Structure

```
thd_hr_backend/
├── main.py            ← FastAPI app, CORS, router registration
├── database.py        ← PostgreSQL connection (SQLAlchemy)
├── models.py          ← ORM models: User, Job, Application, Notice
├── schemas.py         ← Pydantic request/response schemas
├── security.py        ← JWT, bcrypt, role guards
├── email_service.py   ← SMTP email templates
├── crud.py            ← Shared database helpers
├── seed.py            ← Demo data seeder
├── requirements.txt
├── .env.example       ← Environment variable template
└── routers/
    ├── auth.py        ← Login / token endpoints
    ├── users.py       ← User CRUD
    ├── jobs.py        ← Job management + review workflow
    ├── applications.py← Application lifecycle + email triggers
    ├── stats.py       ← Dashboard statistics
    └── notices.py     ← Activity log
```

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| HR Administrator | admin@thd.de | admin123 |
| Department Head (CS) | dept@thd.de | dept123 |
| Department Head (Marketing) | dept2@thd.de | dept123 |
| Faculty (AI Research) | prof@thd.de | prof123 |
| Faculty (IT Services) | faculty2@thd.de | prof123 |

---

## Production Deployment

```bash
# Use gunicorn with uvicorn workers
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or with Docker
docker build -t thd-hr-backend .
docker run -e DATABASE_URL=... -e SECRET_KEY=... -p 8000:8000 thd-hr-backend
```

**Security checklist for production:**
- Change `SECRET_KEY` to a random 32-byte hex string
- Set `CORS_ORIGINS` to your frontend domain (not `*`)
- Set `EMAIL_ENABLED=true` with real SMTP credentials
- Use HTTPS (reverse proxy with nginx or Caddy)
- Set a strong PostgreSQL password
