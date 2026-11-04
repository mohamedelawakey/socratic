from src.extractor import extract_crash_context
from src.agent.graph.graph import SocraticGraph
from src.db.service import MetricsService

def run_socratic_agent(exception_type, exception_value, exception_traceback):
    context = extract_crash_context(exception_traceback, exception_value)

    # 1. Record error crash event in local database (metrics tracking)
    event_id = MetricsService.record_error_start(
        error_type=exception_type.__name__,
        error_message=str(exception_value),
        file_path=context["file_path"],
    )
    from src.events import EventBus
    EventBus.set_active_event_id(event_id)

    initial_state = {
        "file_path": context["file_path"],
        "function_name": context["function_name"],
        "line_number": context["line_number"],
        "line_content": context["line_content"],
        "code_snippet": context["code_snippet"],
        "error_type": exception_type.__name__,
        "error_name": str(exception_value),
        "event_id": event_id,
        "root_cause": "",
        "dialogue_history": [],
        "is_solved": False,
    }
    
    app = SocraticGraph.build_graph()
    app.invoke(initial_state)
