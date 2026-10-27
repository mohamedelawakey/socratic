from src.config_creator import create_config
from pathlib import Path
import yaml
import os


class ReadYaml:
    @staticmethod
    def get_config_path() -> Path:
        # 1. First check in current working directory
        cwd_file = Path.cwd() / ".socratic.yaml"
        if cwd_file.exists():
            return cwd_file

        # 2. Check in project root
        project_root = Path(__file__).resolve().parent.parent.parent
        root_file = project_root / ".socratic.yaml"
        if root_file.exists():
            return root_file

        # 3. Fallback: auto-create in project root and return
        create_config()
        return root_file if root_file.exists() else cwd_file

    @staticmethod
    def read_yaml() -> dict:
        config_path = ReadYaml.get_config_path()
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}
                for key in ["LANGSMITH_TRACING", "LANGSMITH_API_KEY", "LANGSMITH_PROJECT"]:
                    if data.get(key):
                        os.environ[key] = str(data[key])
                return data
        except Exception:
            return {}
