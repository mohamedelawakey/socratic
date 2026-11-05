import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ErrorEvent(Base):
    __tablename__ = "error_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    error_type = Column(String(100), nullable=False)
    error_message = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    project_name = Column(String(255), nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    hints_used = Column(Integer, default=1, nullable=False)
    dialogue_turns = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="unsolved", nullable=False)

    def __repr__(self):
        return f"<ErrorEvent(id='{self.id}', type='{self.error_type}', status='{self.status}')>"


class AppSession(Base):
    __tablename__ = "app_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    session_end = Column(DateTime, nullable=True)
    project_name = Column(String(255), nullable=True)
