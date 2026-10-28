"""Socratic Debug — Autonomous pedagogical debugging mentor."""

from src.hook import install as _core_install
from src.agent.runner import run_socratic_agent


def _wire_ui():
    try:
        from ui.adapter import register_ui_adapter
        register_ui_adapter()
    except Exception:
        pass


def install():
    """Binds UI presentation adapter and installs system exception hook."""
    _wire_ui()
    _core_install()


def main():
    """Primary CLI composition root: connects UI adapter to core and executes CLI."""
    _wire_ui()
    from src.cli import main as _cli_main
    _cli_main()


__all__ = ["install", "run_socratic_agent", "main"]
