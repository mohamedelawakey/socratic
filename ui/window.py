import platform
import shutil
import subprocess
import sys
import os
from typing import List, Optional


class TerminalWindowLauncher:
    """
    Cross-platform Terminal Launcher.
    Spawns dedicated, styled GUI terminal popup windows on:
    - Linux (GNOME Terminal, Kitty, Alacritty, Konsole, XFCE, etc.)
    - macOS (Terminal.app, iTerm2 via AppleScript)
    - Windows (Windows Terminal wt.exe, CMD, PowerShell)
    """

    LINUX_TERMINALS = [
        "gnome-terminal",
        "io.elementary.terminal",
        "x-terminal-emulator",
        "xfce4-terminal",
        "mate-terminal",
        "konsole",
        "kitty",
        "alacritty",
        "xterm",
    ]

    @staticmethod
    def spawn_session_window(command_args: List[str]) -> bool:
        """
        Spawns a new dedicated terminal window based on host OS.
        Returns True on success, or False to fallback to in-process execution.
        """
        # Avoid recursive popup spawning
        if os.environ.get("SOCRATIC_IN_POPUP") == "1":
            return False

        current_os = platform.system().lower()
        env = os.environ.copy()
        env["SOCRATIC_IN_POPUP"] = "1"

        try:
            if "windows" in current_os:
                return TerminalWindowLauncher._spawn_windows(command_args, env)
            elif "darwin" in current_os:
                return TerminalWindowLauncher._spawn_macos(command_args, env)
            elif "linux" in current_os:
                return TerminalWindowLauncher._spawn_linux(command_args, env)
        except Exception:
            return False

        return False

    @staticmethod
    def _spawn_windows(command_args: List[str], env: dict) -> bool:
        cmd_str = " ".join(f'"{arg}"' if " " in arg else arg for arg in command_args)

        # 1. Try modern Windows Terminal (wt.exe)
        if shutil.which("wt.exe") or shutil.which("wt"):
            subprocess.Popen(
                ["wt.exe", "--title", "🧠 Socratic Debug Session", "cmd", "/c", cmd_str],
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            return True

        # 2. Fallback to standard Windows cmd.exe
        subprocess.Popen(
            f'start "🧠 Socratic Debug Session" cmd /c "{cmd_str}"',
            shell=True,
            env=env,
        )
        return True

    @staticmethod
    def _spawn_macos(command_args: List[str], env: dict) -> bool:
        cmd_str = " ".join(f'"{arg}"' if " " in arg else arg for arg in command_args)
        escaped_cmd = cmd_str.replace('\\', '\\\\').replace('"', '\\"')

        # Launch dedicated macOS Terminal.app via osascript
        apple_script = f'''
        tell application "Terminal"
            do script "{escaped_cmd}"
            activate
        end tell
        '''
        subprocess.Popen(["osascript", "-e", apple_script], env=env)
        return True

    @staticmethod
    def _spawn_linux(command_args: List[str], env: dict) -> bool:
        terminal = None
        for term in TerminalWindowLauncher.LINUX_TERMINALS:
            if shutil.which(term):
                terminal = term
                break

        if not terminal:
            return False

        if terminal in ("gnome-terminal", "io.elementary.terminal", "x-terminal-emulator", "mate-terminal", "xfce4-terminal"):
            subprocess.Popen(
                [
                    terminal,
                    "--title=🧠 Socratic Debug Session",
                    "--geometry=84x24",
                    "--",
                    *command_args,
                ],
                env=env,
            )
            return True

        elif terminal == "konsole":
            subprocess.Popen(
                [
                    terminal,
                    "-p", "tabtitle=🧠 Socratic Debug Session",
                    "-e",
                    *command_args,
                ],
                env=env,
            )
            return True

        elif terminal in ("alacritty", "kitty", "xterm"):
            subprocess.Popen(
                [
                    terminal,
                    "-T", "🧠 Socratic Debug Session",
                    "-e",
                    *command_args,
                ],
                env=env,
            )
            return True

        return False
