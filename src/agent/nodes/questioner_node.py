from src.agent.prompts.questioner_prompt import QuestionerPrompt
from src.agent.state.state import SocraticAgentState
from src.agent.llm.invoker import LLMInvoker
from src.utils.read_yaml import ReadYaml

from src.events import EventBus

config = ReadYaml.read_yaml()


class QuestionerNode:
    @staticmethod
    def questioner_node(state: SocraticAgentState) -> dict:
        current_hint = state.get("hint_level", 1)
        raw_history = state.get("dialogue_history", [])

        # Re-read YAML configuration dynamically to reflect any runtime updates
        live_config = ReadYaml.read_yaml()

        formatted_history = "\n".join(
            f"- {turn.get('role', 'unknown').capitalize()}: {turn.get('content', '')}"
            for turn in raw_history
        )

        prompt = QuestionerPrompt.questioner_prompt(
            error_type=state["error_type"],
            line_number=state["line_number"],
            line_content=state["line_content"],
            code_snippet=state["code_snippet"],
            root_cause=state["root_cause"],
            dialogue_history=formatted_history,
            hint_level=current_hint,
            language=live_config.get("socratic_language", "English"),
            style=live_config.get("socratic_style", "friendly"),
        )

        response = LLMInvoker.invoke_with_retry(prompt)

        # Update hint level metric in database
        event_id = state.get("event_id")
        if event_id:
            from src.db.service import MetricsService
            MetricsService.update_hint_level(event_id, current_hint)

        EventBus.emit_mentor_message(
            content=response.content,
            hint_level=current_hint,
        )

        history = list(state.get("dialogue_history", []))
        history.append({"role": "mentor", "content": response.content})
        
        return {
            "dialogue_history": history,
            "hint_level": current_hint + 1 if current_hint < 3 else current_hint,
        }
