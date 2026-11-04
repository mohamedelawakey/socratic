from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, ErrorEvent
from src.db.connection import get_default_db_path


class DatabaseMigrator:
    @staticmethod
    def migrate_sqlite_to_target(target_db_url: str) -> int:
        sqlite_path = get_default_db_path()
        sqlite_url = f"sqlite:///{sqlite_path}"

        if target_db_url.strip() == sqlite_url.strip():
            return 0

        # Source SQLite session
        src_engine = create_engine(sqlite_url, echo=False)
        SrcSession = sessionmaker(bind=src_engine)
        src_session = SrcSession()

        # Target DB session & table initialization
        target_engine = create_engine(target_db_url, echo=False)
        Base.metadata.create_all(bind=target_engine)
        TargetSession = sessionmaker(bind=target_engine)
        target_session = TargetSession()

        migrated_count = 0
        try:
            records = src_session.query(ErrorEvent).all()
            for r in records:
                # Check if already present in target DB
                existing = target_session.query(ErrorEvent).filter(ErrorEvent.id == r.id).first()
                if not existing:
                    new_item = ErrorEvent(
                        id=r.id,
                        error_type=r.error_type,
                        error_message=r.error_message,
                        file_name=r.file_name,
                        project_name=r.project_name,
                        started_at=r.started_at,
                        resolved_at=r.resolved_at,
                        duration_seconds=r.duration_seconds,
                        hints_used=r.hints_used,
                        dialogue_turns=r.dialogue_turns,
                        status=r.status,
                    )
                    target_session.add(new_item)
                    migrated_count += 1

            if migrated_count > 0:
                target_session.commit()
            return migrated_count
        finally:
            src_session.close()
            target_session.close()

