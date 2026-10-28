import os
import sys
import threading
from ui.app import bridge, wait_for_gui_user_input
from ui.console import console
from rich.panel import Panel
from rich.markdown import Markdown


class SocraticUI:
    """Unified UI layer: seamlessly routes to PyQt6 Desktop Terminal or CLI Fallback."""

    @staticmethod
    def is_gui_active() -> bool:
        return os.environ.get("SOCRATIC_GUI_ACTIVE") == "1"

    @staticmethod
    def launch(context: dict, exception_type, exception_value, exception_traceback, agent_runner_func):
        """Encapsulates GUI initialization, file monitor, background agent thread, or headless fallback."""
        has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or sys.platform == "win32")

        if has_display:
            try:
                from PyQt6.QtWidgets import QApplication
                from ui.app import SocraticWindow

                os.environ["SOCRATIC_GUI_ACTIVE"] = "1"

                app = QApplication.instance()
                if app is None:
                    app = QApplication(sys.argv)

                window = SocraticWindow(
                    error_type=exception_type.__name__,
                    error_message=str(exception_value),
                    file_path=context["file_path"],
                    line_number=context["line_number"],
                    line_content=context["line_content"],
                )
                window.show()

                # Launch LangGraph agent in background worker thread
                agent_thread = threading.Thread(
                    target=agent_runner_func,
                    args=(exception_type, exception_value, exception_traceback),
                    daemon=True,
                )
                agent_thread.start()

                # Launch real-time file monitor if target file exists
                if os.path.exists(context["file_path"]):
                    from src.watcher import FileMonitor
                    file_monitor = FileMonitor(
                        file_path=context["file_path"],
                        target_error=exception_type.__name__,
                        on_solved_callback=lambda: bridge.live_solution_detected.emit(),
                        on_failed_callback=lambda err: bridge.live_error_detected.emit(err),
                    )
                    file_monitor.start()

                app.exec()
                return
            except Exception:
                # Fallback gracefully to terminal mode if GUI setup fails
                pass

        # Headless / Terminal Fallback Mode
        os.environ["SOCRATIC_GUI_ACTIVE"] = "0"
        SocraticUI.display_crash_banner(
            error_type=exception_type.__name__,
            error_message=str(exception_value),
            file_path=context["file_path"],
            line_number=context["line_number"],
            line_content=context["line_content"],
        )
        agent_runner_func(exception_type, exception_value, exception_traceback)

    @staticmethod
    def display_crash_banner(error_type: str, error_message: str, file_path: str, line_number: int, line_content: str):
        # In CLI fallback mode, print Rich banner
        if not SocraticUI.is_gui_active():
            console.print(f"\n[bold red]💥 {error_type}: {error_message}[/bold red]")
            console.print(f"[dim]📍 {file_path}:{line_number}[/dim]\n")

    @staticmethod
    def display_mentor_message(content: str, hint_level: int = 1):
        if SocraticUI.is_gui_active():
            bridge.mentor_message_received.emit(content, hint_level)
        else:
            md = Markdown(content)
            panel = Panel(md, title=f"Socratic Mentor (Level {hint_level}/3)", border_style="cyan")
            console.print(panel)

    @staticmethod
    def prompt_user_input() -> str:
        if SocraticUI.is_gui_active():
            return wait_for_gui_user_input()
        else:
            return console.input("[bold yellow]❯❯ Your Response: [/bold yellow]").strip()

    @staticmethod
    def display_evaluator_verdict(verdict: str):
        if SocraticUI.is_gui_active():
            bridge.evaluator_verdict_received.emit(verdict)
        else:
            console.print(f"  [bold yellow]🔍 {verdict}[/bold yellow]\n")

    @staticmethod
    def display_solution(solution_content: str):
        if SocraticUI.is_gui_active():
            bridge.solution_received.emit(solution_content)
        else:
            md = Markdown(solution_content)
            panel = Panel(md, title="🏆 Socratic Wrap-Up", border_style="green")
            console.print(panel)
