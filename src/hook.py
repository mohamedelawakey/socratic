import sys
import os
import threading
from src.extractor import extract_crash_context
from src.config_creator import create_config
from src.agent.runner import run_socratic_agent
from ui.views import SocraticUI


def socratic_excepthook(exception_type, exception_value, exception_traceback):
    """Intercepts uncaught exceptions and launches the Socratic GUI Terminal window."""
    context = extract_crash_context(exception_traceback)

    # Check if graphical desktop display is available
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or sys.platform == "win32")

    if has_display:
        try:
            from PyQt6.QtWidgets import QApplication
            from ui.app import SocraticWindow

            os.environ["SOCRATIC_GUI_ACTIVE"] = "1"

            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            # Create and display the centered Socratic Terminal window
            window = SocraticWindow(
                error_type=exception_type.__name__,
                error_message=str(exception_value),
                file_path=context["file_path"],
                line_number=context["line_number"],
                line_content=context["line_content"],
            )
            window.show()

            # Run LangGraph State Machine in background worker thread
            agent_thread = threading.Thread(
                target=run_socratic_agent,
                args=(exception_type, exception_value, exception_traceback),
                daemon=True,
            )
            agent_thread.start()

            # Run Qt GUI event loop
            app.exec()
            return
        except Exception as e:
            # Fallback to terminal mode if GUI setup fails
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
    run_socratic_agent(exception_type, exception_value, exception_traceback)

# use the hook 
def install():
    create_config()
    sys.excepthook = socratic_excepthook
