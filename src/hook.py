import sys
from src.extractor import extract_crash_context
from src.config_creator import create_config
from src.events import EventBus


def socratic_excepthook(exception_type, exception_value, exception_traceback):
    """Intercepts uncaught exceptions and delegates to the decoupled EventBus."""
    context = extract_crash_context(exception_traceback, exception_value)
    EventBus.emit_crash(
        context=context,
        exc_type=exception_type,
        exc_val=exception_value,
        exc_tb=exception_traceback,
    )


def install():
    """Installs Socratic as the global system exception hook."""
    create_config()
    sys.excepthook = socratic_excepthook
