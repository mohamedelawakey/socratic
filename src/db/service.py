import os
from datetime import datetime
from src.db.connection import SessionLocal, init_db
from src.db.models import ErrorEvent

# Ensure tables exist
init_db()


class MetricsService:
    @staticmethod
    def record_error_start(error_type: str, error_message: str, file_path: str) -> str:
        session = SessionLocal()
        try:
            file_name = os.path.basename(file_path) if file_path else "unknown"
            project_name = os.path.basename(os.path.dirname(os.path.abspath(file_path))) if file_path else "unknown"

            event = ErrorEvent(
                error_type=error_type,
                error_message=str(error_message)[:500] if error_message else "",
                file_name=file_name,
                project_name=project_name,
                started_at=datetime.utcnow(),
                status="unsolved",
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            return event.id
        finally:
            session.close()

    @staticmethod
    def record_error_resolved(event_id: str):
        if not event_id:
            return

        session = SessionLocal()
        try:
            event = session.query(ErrorEvent).filter(ErrorEvent.id == event_id).first()
            if event:
                now = datetime.utcnow()
                event.resolved_at = now
                event.duration_seconds = int((now - event.started_at).total_seconds())
                event.status = "solved"
                session.commit()
        finally:
            session.close()

    @staticmethod
    def update_hint_level(event_id: str, hint_level: int):
        if not event_id:
            return

        session = SessionLocal()
        try:
            event = session.query(ErrorEvent).filter(ErrorEvent.id == event_id).first()
            if event and hint_level > event.hints_used:
                event.hints_used = hint_level
                session.commit()
        finally:
            session.close()

    @staticmethod
    def increment_dialogue_turns(event_id: str):
        if not event_id:
            return

        session = SessionLocal()
        try:
            event = session.query(ErrorEvent).filter(ErrorEvent.id == event_id).first()
            if event:
                event.dialogue_turns += 1
                session.commit()
        finally:
            session.close()
