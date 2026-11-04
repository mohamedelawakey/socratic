from pathlib import Path
import yaml
from src.utils.read_yaml import ReadYaml


class ConfigManager:
    @staticmethod
    def get_config_path() -> Path:
        return ReadYaml.get_config_path()

    @staticmethod
    def load_config() -> dict:
        return ReadYaml.read_yaml()

    @staticmethod
    def save_config(new_values: dict) -> bool:
        config_path = ConfigManager.get_config_path()
        try:
            data = {}
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

            data.update(new_values)

            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

            return True
        except Exception:
            return False
