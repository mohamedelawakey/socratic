from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base
from src.utils.read_yaml import ReadYaml


def get_default_db_path() -> str:
    # Try user home ~/.socratic, fallback to local workspace .socratic/ if home is read-only
    try:
        socratic_dir = Path.home() / ".socratic"
        socratic_dir.mkdir(parents=True, exist_ok=True)
        return str(socratic_dir / "socratic.db")
    except (OSError, PermissionError):
        local_dir = Path(".socratic")
        local_dir.mkdir(parents=True, exist_ok=True)
        return str(local_dir / "socratic.db")


def get_database_url() -> str:
    try:
        config = ReadYaml.read_yaml()
        db_type = str(config.get("database_type", "sqlite")).lower().strip()
        db_url = config.get("database_url")

        # If explicit full URL provided, use it directly
        if db_url and str(db_url).strip():
            return str(db_url).strip()

        # If user picked a type other than sqlite but didn't write full url, provide smart default localhost URL
        if db_type == "postgresql":
            return "postgresql://postgres:postgres@localhost:5432/socratic"
        elif db_type in ["mysql", "mariadb"]:
            return "mysql+pymysql://root:root@localhost:3306/socratic"
        elif db_type in ["mssql", "sqlserver"]:
            return "mssql+pyodbc://sa:YourPassword123@localhost:1433/socratic?driver=ODBC+Driver+17+for+SQL+Server"
        elif db_type == "oracle":
            return "oracle+oracledb://system:oracle@localhost:1521/socratic"
    except Exception:
        pass

    db_path = get_default_db_path()
    return f"sqlite:///{db_path}"


DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

    # Check if target is not default sqlite, perform auto-migration if needed
    try:
        from src.utils.read_yaml import ReadYaml
        config = ReadYaml.read_yaml()
        target_url = config.get("database_url")
        default_sqlite = f"sqlite:///{get_default_db_path()}"
        if target_url and target_url.strip() != default_sqlite.strip():
            from src.db.migrator import DatabaseMigrator
            DatabaseMigrator.migrate_sqlite_to_target(target_url)
    except Exception:
        pass
