import os
import time
import threading
from src.utils.read_yaml import ReadYaml


class ConfigFileWatcher(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.config_path = ReadYaml.get_config_path()
        self.last_mtime = os.path.getmtime(self.config_path) if self.config_path.exists() else 0

    def run(self):
        while True:
            time.sleep(1)
            try:
                if self.config_path.exists():
                    current_mtime = os.path.getmtime(self.config_path)
                    if current_mtime != self.last_mtime:
                        self.last_mtime = current_mtime
            except OSError:
                pass
