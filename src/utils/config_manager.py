import os
import stat
import tempfile
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

            # Atomic Write via tempfile in the same directory
            dir_path = config_path.parent
            with tempfile.NamedTemporaryFile("w", dir=dir_path, delete=False, encoding="utf-8") as tf:
                yaml.dump(data, tf, default_flow_style=False, allow_unicode=True, sort_keys=False)
                temp_name = tf.name

            # Restrict permissions to owner-only (0o600 / rw-------)
            try:
                os.chmod(temp_name, stat.S_IRUSR | stat.S_IWUSR)
            except OSError:
                pass

            # Atomic replace
            os.replace(temp_name, config_path)
            return True
        except Exception:
            return False
