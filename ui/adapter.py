from src.events import EventBus
from src.agent.runner import run_socratic_agent
from ui.views import SocraticUI


def register_ui_adapter():
    """Binds the SocraticUI presentation layer to the Core EventBus.

    This ensures complete decoupling: Core never imports UI.
    """
    EventBus.register_handlers(
        on_mentor_message=SocraticUI.display_mentor_message,
        on_user_input_requested=SocraticUI.prompt_user_input,
        on_evaluator_verdict=SocraticUI.display_evaluator_verdict,
        on_solution=SocraticUI.display_solution,
        on_crash=lambda ctx, etype, evalue, tb: SocraticUI.launch(
            context=ctx,
            exception_type=etype,
            exception_value=evalue,
            exception_traceback=tb,
            agent_runner_func=run_socratic_agent,
        ),
    )
