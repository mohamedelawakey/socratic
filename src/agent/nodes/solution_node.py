from src.agent.prompts.solution_prompt import SolutionPrompt
from src.agent.state.state import SocraticAgentState
from src.agent.llm.invoker import LLMInvoker
from src.utils.read_yaml import ReadYaml
from src.events import EventBus

config = ReadYaml.read_yaml()


class SolutionNode:
    @staticmethod
    def solution_node(state: SocraticAgentState) -> dict:
        current_status = state.get("eval_status", "solved")

        # Dynamically re-read config to adapt to live changes
        live_config = ReadYaml.read_yaml()

        prompt = SolutionPrompt.solution_prompt(
            error_type=state["error_type"],
            line_number=state["line_number"],
            code_snippet=state["code_snippet"],
            root_cause=state["root_cause"],
            eval_status=current_status,
            language=live_config.get("socratic_language", "English"),
            style=live_config.get("socratic_style", "friendly"),
        )

        response = LLMInvoker.invoke_with_retry(prompt)

        # Mark error event as resolved in database
        event_id = state.get("event_id")
        if event_id:
            from src.db.service import MetricsService
            MetricsService.record_error_resolved(event_id)

        EventBus.emit_solution(response.content)

        history = list(state.get("dialogue_history", []))
        history.append({"role": "mentor", "content": response.content})

        return {
            "dialogue_history": history,
            "is_solved": True,
        }
