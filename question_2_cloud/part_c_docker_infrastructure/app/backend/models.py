"""
Database Models for AI Case Management System
==============================================
Defines the schema for private case notes and audit logs.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CaseNote(Base):
    """Stores confidential case management notes."""
    __tablename__ = "case_notes"

    id = Column(Integer, primary_key=True, index=True)
    client_pseudonym = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
