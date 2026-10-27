try:
    from src.config_template import ConfigTemplate
except ImportError:
    from config_template import ConfigTemplate
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# make the socratic.config file
def create_config():
    config_path = PROJECT_ROOT / ".socratic.yaml"

    if config_path.exists():
        return

    with open(config_path, "w") as f:
        f.write(ConfigTemplate.DEFAULT_CONFIG_TEMPLATE)

# read the socratic.config file and return the values
def read_config() -> dict:
    config_path = PROJECT_ROOT / ".socratic.yaml"

    if not config_path.exists():
        return {}

    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}

if __name__ == "__main__":
    create_config()
    print("Config created!")
