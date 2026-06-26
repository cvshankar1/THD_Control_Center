"""
crud.py — Shared database helpers used by multiple routers
"""

from sqlalchemy.orm import Session
import models


def add_notice(
    db:          Session,
    title:       str,
    description: str = "",
    color:       str = "#1B3A6B",
    ref_type:    str = "",
    ref_id:      int = None
) -> models.Notice:
    """Add an entry to the activity / notice log."""
    notice = models.Notice(
        title=title,
        description=description,
        color=color,
        ref_type=ref_type,
        ref_id=ref_id,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return notice
