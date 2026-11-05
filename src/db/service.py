import os
from datetime import datetime
from src.db.connection import SessionLocal, init_db
from src.db.models import ErrorEvent, AppSession

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

    @staticmethod
    def record_app_launch(project_name: str = "") -> str:
        session = SessionLocal()
        try:
            app_session = AppSession(
                session_start=datetime.utcnow(),
                project_name=project_name or "default",
            )
            session.add(app_session)
            session.commit()
            session.refresh(app_session)
            return app_session.id
        finally:
            session.close()

    @staticmethod
    def get_dashboard_metrics() -> dict:
        session = SessionLocal()
        try:
            events = session.query(ErrorEvent).all()
            sessions = session.query(AppSession).all()

            # Error counts by type
            error_counts = {}
            error_dates = {}
            solved_count = 0
            total_duration = 0
            solved_with_duration = 0

            for ev in events:
                error_counts[ev.error_type] = error_counts.get(ev.error_type, 0) + 1
                dt_str = ev.started_at.strftime("%Y-%m-%d") if ev.started_at else "unknown"
                if ev.error_type not in error_dates:
                    error_dates[ev.error_type] = []
                error_dates[ev.error_type].append(dt_str)

                if ev.status == "solved":
                    solved_count += 1
                    if ev.duration_seconds is not None:
                        total_duration += ev.duration_seconds
                        solved_with_duration += 1

            activity_by_day = {}
            for ev in events:
                day_str = ev.started_at.strftime("%Y-%m-%d") if ev.started_at else "unknown"
                activity_by_day[day_str] = activity_by_day.get(day_str, 0) + 1

            avg_duration = (total_duration // solved_with_duration) if solved_with_duration > 0 else 0
            solve_rate = int((solved_count / len(events)) * 100) if events else 100

            return {
                "total_errors": len(events),
                "solved_count": solved_count,
                "solve_rate": solve_rate,
                "avg_duration": avg_duration,
                "error_counts": error_counts,
                "error_dates": error_dates,
                "activity_by_day": activity_by_day,
                "total_launches": len(sessions),
            }
        finally:
            session.close()
