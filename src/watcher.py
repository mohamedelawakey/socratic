import os
import time
import ast
import subprocess
import sys
import threading


class FileMonitor(threading.Thread):
    def __init__(
        self,
        file_path: str,
        target_error: str,
        on_solved_callback,
        on_failed_callback,
    ):
        super().__init__(daemon=True)
        self.file_path = file_path
        self.target_error = target_error.strip()
        self.on_solved_callback = on_solved_callback
        self.on_failed_callback = on_failed_callback
        self.last_mtime = os.path.getmtime(file_path)
        self.running = True
        self._last_reported_err = ""

    def run(self):
        while self.running:
            time.sleep(0.5)

            try:
                current_mtime = os.path.getmtime(self.file_path)
            except OSError:
                continue

            if current_mtime != self.last_mtime:
                self.last_mtime = current_mtime
                time.sleep(1.8)

                # Skip if user is actively typing and mtime kept updating
                try:
                    if os.path.getmtime(self.file_path) != current_mtime:
                        continue
                except OSError:
                    continue

                # Quick AST syntax validation (ignore incomplete statements while typing)
                try:
                    with open(self.file_path, "r", encoding="utf-8") as file:
                        ast.parse(file.read())
                except (SyntaxError, OSError):
                    continue

                # Execute script in silent background subprocess
                try:
                    res = subprocess.run(
                        [sys.executable, self.file_path],
                        capture_output=True,
                        text=True,
                        timeout=7,
                    )

                    # Scenario A: Clean execution with zero errors
                    if res.returncode == 0:
                        self.on_solved_callback()
                        self.running = False
                        break

                    # If the script has a SyntaxError, the user is still writing or broke the syntax
                    if "SyntaxError" in res.stderr:
                        continue

                    # Scenario B: Target error is resolved and code progresses past it
                    if self.target_error and self.target_error not in res.stderr:
                        # Ensure it's not a generic failure before the target error
                        self.on_solved_callback()
                        self.running = False
                        break

                    # Scenario C: Target error still occurs
                    current_err = res.stderr.strip()
                    if current_err != self._last_reported_err:
                        self._last_reported_err = current_err
                        self.on_failed_callback(res.stderr)

                except subprocess.TimeoutExpired:
                    continue
                except Exception:
                    continue
