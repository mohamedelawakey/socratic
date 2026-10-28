from typing import Callable, Optional, Any, Dict


class EventBus:
    # Callbacks registered by external UI layers (PyQt6, Webview, CLI, etc.)
    _on_mentor_message: Optional[Callable[[str, int], None]] = None
    _on_user_input_requested: Optional[Callable[[], str]] = None
    _on_evaluator_verdict: Optional[Callable[[str], None]] = None
    _on_solution: Optional[Callable[[str], None]] = None
    _on_crash: Optional[Callable[[Dict[str, Any], Any, Any, Any], None]] = None

    @classmethod
    def register_handlers(
        cls,
        on_mentor_message: Optional[Callable[[str, int], None]] = None,
        on_user_input_requested: Optional[Callable[[], str]] = None,
        on_evaluator_verdict: Optional[Callable[[str], None]] = None,
        on_solution: Optional[Callable[[str], None]] = None,
        on_crash: Optional[Callable[[Dict[str, Any], Any, Any, Any], None]] = None,
    ):
        """Registers presentation callbacks into the Core event bus."""
        if on_mentor_message:
            cls._on_mentor_message = on_mentor_message
        if on_user_input_requested:
            cls._on_user_input_requested = on_user_input_requested
        if on_evaluator_verdict:
            cls._on_evaluator_verdict = on_evaluator_verdict
        if on_solution:
            cls._on_solution = on_solution
        if on_crash:
            cls._on_crash = on_crash

    @classmethod
    def emit_mentor_message(cls, content: str, hint_level: int = 1):
        if cls._on_mentor_message:
            cls._on_mentor_message(content, hint_level)
        else:
            # Fallback pure standard output
            print(f"\n[Socratic Mentor (Level {hint_level})]: {content}\n")

    @classmethod
    def request_user_input(cls) -> str:
        if cls._on_user_input_requested:
            return cls._on_user_input_requested()
        return input("❯❯ Your Response: ").strip()

    @classmethod
    def emit_evaluator_verdict(cls, verdict: str):
        if cls._on_evaluator_verdict:
            cls._on_evaluator_verdict(verdict)
        else:
            print(f"  🔍 Verdict: {verdict}")

    @classmethod
    def emit_solution(cls, solution_content: str):
        if cls._on_solution:
            cls._on_solution(solution_content)
        else:
            print(f"\n🏆 Wrap-Up:\n{solution_content}\n")

    @classmethod
    def emit_crash(cls, context: Dict[str, Any], exc_type: Any, exc_val: Any, exc_tb: Any):
        if cls._on_crash:
            cls._on_crash(context, exc_type, exc_val, exc_tb)
        else:
            print(f"\n💥 {exc_type.__name__}: {exc_val}")
            print(f"📍 {context.get('file_path')}:{context.get('line_number')}\n")
