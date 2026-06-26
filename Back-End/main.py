"""
THD HR Control Center — FastAPI Backend
Technische Hochschule Deggendorf 

Run:
    uvicorn main:app --reload --port 8000

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine
import models

# Import all routers
from routers import auth, jobs, applications, users, stats, notices

# ── Create all DB tables on startup ──────────────────────────────────────────
models.Base.metadata.create_all(bind=engine)

# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="THD HR Control Center API",
    description="""
## Human Resources Control Center — Technische Hochschule Deggendorf

This API powers the THD HR Control Center web application.

### Features
- **JWT Authentication** with role-based access (Admin / Department Head / Faculty)
- **Job Postings** — internal-first workflow with deadline and auto-promote to external
- **Applications** — full lifecycle from submission to hiring
- **Email Notifications** — automatic triggers at key workflow stages
- **Recruitment Pipeline** — 5-stage Kanban (New → Review → Interview → Contract → Hired)
- **Analytics** — dashboard statistics and reporting
    """,
    version="1.0.0",
    contact={"name": "THD HR System", "email": "hr@thd.de"},
)

# ── CORS — allow the frontend (adjust origins in production) ──────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Restrict to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────────
app.include_router(auth.router,         prefix="/api/auth",         tags=["Authentication"])
app.include_router(users.router,        prefix="/api/users",        tags=["Users"])
app.include_router(jobs.router,         prefix="/api/jobs",         tags=["Jobs"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(stats.router,        prefix="/api/stats",        tags=["Statistics"])
app.include_router(notices.router,      prefix="/api/notices",      tags=["Notices"])


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "THD HR Control Center API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
