from src.agent.prompts.solution_prompt import SolutionPrompt
from src.agent.state.state import SocraticAgentState
from src.agent.llm.factory import LLMFactory
from src.utils.read_yaml import ReadYaml
from src.events import EventBus

config = ReadYaml.read_yaml()


class SolutionNode:
    @staticmethod
    def solution_node(state: SocraticAgentState) -> dict:
        current_status = state.get("eval_status", "solved")

        prompt = SolutionPrompt.solution_prompt(
            error_type=state["error_type"],
            line_number=state["line_number"],
            code_snippet=state["code_snippet"],
            root_cause=state["root_cause"],
            eval_status=current_status,
            language=config.get("socratic_language", "English"),
            style=config.get("socratic_style", "friendly"),
        )

        response = LLMFactory.get_llm().invoke(prompt)

        EventBus.emit_solution(response.content)

        history = list(state.get("dialogue_history", []))
        history.append({"role": "mentor", "content": response.content})

        return {
            "dialogue_history": history,
            "is_solved": True,
        }
