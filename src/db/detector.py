import socket
from typing import List, Dict


class DatabaseDetector:
    KNOWN_SERVICES = [
        {"name": "PostgreSQL", "port": 5432, "default_scheme": "postgresql", "driver": "psycopg2"},
        {"name": "MySQL", "port": 3306, "default_scheme": "mysql+pymysql", "driver": "pymysql"},
        {"name": "MariaDB", "port": 3307, "default_scheme": "mariadb+pymysql", "driver": "pymysql"},
        {"name": "SQL Server", "port": 1433, "default_scheme": "mssql+pyodbc", "driver": "pyodbc"},
        {"name": "Oracle Database", "port": 1521, "default_scheme": "oracle+oracledb", "driver": "oracledb"},
        {"name": "DuckDB", "port": 0, "default_scheme": "duckdb", "driver": "duckdb"},
        {"name": "CockroachDB", "port": 26257, "default_scheme": "cockroachdb+psycopg2", "driver": "psycopg2"},
    ]

    @staticmethod
    def is_port_open(host: str, port: int, timeout: float = 0.4) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                return sock.connect_ex((host, port)) == 0
        except (OSError, socket.error):
            return False

    @classmethod
    def detect_available_databases(cls) -> List[Dict[str, str]]:
        detected = []

        # Always include default SQLite
        detected.append({
            "engine": "sqlite",
            "name": "SQLite (Default Local)",
            "port": 0,
            "is_running": True,
            "url_template": "sqlite:///$HOME/.socratic/socratic.db"
        })

        for s in cls.KNOWN_SERVICES:
            if cls.is_port_open("127.0.0.1", s["port"]):
                detected.append({
                    "engine": s["default_scheme"].split("+")[0],
                    "name": s["name"],
                    "port": s["port"],
                    "is_running": True,
                    "url_template": f"{s['default_scheme']}://user:password@localhost:{s['port']}/socratic"
                })

        return detected

