"""
models.py — SQLAlchemy ORM models

Tables:
    users           — HR admins, department heads, faculty
    jobs            — job postings (internal / external)
    applications    — candidate applications
    notices         — activity log / notification feed
"""

from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime,
    Boolean, ForeignKey, Enum as SAEnum, func
)
from sqlalchemy.orm import relationship
from database import Base
import enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin   = "admin"
    dept    = "dept"
    faculty = "faculty"


class JobStatus(str, enum.Enum):
    draft     = "Draft"
    review    = "Review"
    published = "Published"
    closed    = "Closed"


class JobVisibility(str, enum.Enum):
    internal = "internal"
    external = "external"


class ReviewStatus(str, enum.Enum):
    pending  = "pending"
    approved = "approved"
    rejected = "rejected"


class AppStage(str, enum.Enum):
    new       = "new"
    review    = "review"
    interview = "interview"
    contract  = "contract"
    hired     = "hired"
    rejected  = "rejected"


# ── Models ────────────────────────────────────────────────────────────────────

class User(Base):
    """HR staff accounts — Admins, Department Heads, Faculty."""
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(150), nullable=False)
    email         = Column(String(200), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role          = Column(String(20), default="faculty", nullable=False)
    department    = Column(String(100), default="")
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, server_default=func.now())
    last_login    = Column(DateTime, nullable=True)

    # Relationships
    jobs_reviewed = relationship("Job", back_populates="reviewer",
                                  foreign_keys="Job.reviewed_by")


class Job(Base):
    """Job postings — internal first, then optionally promoted to external."""
    __tablename__ = "jobs"

    id            = Column(Integer, primary_key=True, index=True)
    title         = Column(String(200), nullable=False)
    dept          = Column(String(100), nullable=False)
    status        = Column(String(20), default="Draft")
    visibility    = Column(String(20), default="internal")
    description   = Column(Text, default="")
    requirements  = Column(Text, default="")
    hours_per_week = Column(Integer, default=10)
    salary        = Column(String(50), default="")
    deadline      = Column(Date, nullable=True)
    applicants    = Column(Integer, default=0)

    # Review workflow
    rv            = Column(String(20), default="pending")   # pending / approved / rejected
    rv_notes      = Column(Text, default="")
    reviewed_by   = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at   = Column(DateTime, nullable=True)

    # Audit
    created_by    = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at    = Column(DateTime, server_default=func.now())
    updated_at    = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    applications  = relationship("Application", back_populates="job",
                                  cascade="all, delete-orphan")
    reviewer      = relationship("User", back_populates="jobs_reviewed",
                                  foreign_keys=[reviewed_by])


class Application(Base):
    """Candidate applications — tracks the full recruitment lifecycle."""
    __tablename__ = "applications"

    id               = Column(Integer, primary_key=True, index=True)
    job_id           = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"),
                               nullable=False)
    applicant_name   = Column(String(150), nullable=False)
    applicant_email  = Column(String(200), nullable=False, index=True)
    student_id       = Column(String(30), default="")
    university       = Column(String(200), default="Technische Hochschule Deggendorf")
    program          = Column(String(150), default="")
    semester         = Column(Integer, default=1)
    motivation       = Column(Text, default="")
    stage            = Column(String(20), default="new")
    score            = Column(Integer, default=0)
    notes            = Column(Text, default="")

    # Email tracking
    email_confirmation_sent = Column(Boolean, default=False)
    email_interview_sent    = Column(Boolean, default=False)
    email_contract_sent     = Column(Boolean, default=False)

    applied_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    job = relationship("Job", back_populates="applications")


class Notice(Base):
    """Activity log / notification feed entries."""
    __tablename__ = "notices"

    id         = Column(Integer, primary_key=True, index=True)
    title      = Column(String(200), nullable=False)
    description = Column(Text, default="")
    color      = Column(String(10), default="#1B3A6B")
    ref_type   = Column(String(20), default="")  # "job" | "application"
    ref_id     = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
