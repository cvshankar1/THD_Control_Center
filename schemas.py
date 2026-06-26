"""
schemas.py — Pydantic request/response models for all endpoints
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email:    str
    password: str
    role:     str    # "admin" | "dept" | "faculty"

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         "UserOut"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role:    Optional[str] = None


# ── Users ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name:       str
    email:      str
    password:   str
    role:       str = "faculty"
    department: str = ""

class UserOut(BaseModel):
    id:         int
    name:       str
    email:      str
    role:       str
    department: str
    is_active:  bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name:       Optional[str] = None
    department: Optional[str] = None
    role:       Optional[str] = None
    is_active:  Optional[bool] = None


# ── Jobs ──────────────────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    title:          str
    dept:           str
    status:         Optional[str] = "Draft"
    visibility:     Optional[str] = "internal"
    description:    Optional[str] = ""
    requirements:   Optional[str] = ""
    hours_per_week: Optional[int] = 10
    salary:         Optional[str] = ""
    deadline:       Optional[date] = None

class JobOut(BaseModel):
    id:             int
    title:          str
    dept:           str
    status:         str
    visibility:     str
    description:    str
    requirements:   str
    hours_per_week: int
    salary:         str
    deadline:       Optional[date] = None
    applicants:     int
    rv:             str
    rv_notes:       str
    created_at:     Optional[datetime] = None

    class Config:
        from_attributes = True

class JobUpdate(JobCreate):
    pass

class JobReview(BaseModel):
    decision: str    # "approved" | "rejected"
    notes:    Optional[str] = ""


# ── Applications ──────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    job_id:          int
    applicant_name:  str
    applicant_email: str
    student_id:      Optional[str] = ""
    university:      Optional[str] = "Technische Hochschule Deggendorf"
    program:         Optional[str] = ""
    semester:        Optional[int] = 1
    motivation:      Optional[str] = ""

class ApplicationOut(BaseModel):
    id:              int
    job_id:          int
    applicant_name:  str
    applicant_email: str
    student_id:      str
    university:      str
    program:         str
    semester:        int
    motivation:      str
    stage:           str
    score:           int
    notes:           str
    email_confirmation_sent: bool
    email_interview_sent:    bool
    email_contract_sent:     bool
    applied_at:      Optional[datetime] = None

    class Config:
        from_attributes = True

class StageUpdate(BaseModel):
    stage: str
    notes: Optional[str] = None

class ScoreUpdate(BaseModel):
    score: int


# ── Notices ───────────────────────────────────────────────────────────────────

class NoticeOut(BaseModel):
    id:          int
    title:       str
    description: str
    color:       str
    ref_type:    str
    ref_id:      Optional[int] = None
    created_at:  Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Stats ─────────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    open_positions:    int
    total_applications: int
    interviews:        int
    hired:             int
    internal_jobs:     int
    external_jobs:     int
    pending_reviews:   int


# ── Rebuild forward references ────────────────────────────────────────────────
TokenResponse.model_rebuild()
