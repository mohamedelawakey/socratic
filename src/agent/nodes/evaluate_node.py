from src.agent.prompts.evaluation_prompt import EvaluationPrompt
from src.agent.state.state import SocraticAgentState
from src.agent.llm.factory import LLMFactory
from src.events import EventBus


class EvaluationNode:
    @staticmethod
    def evaluation_node(state: SocraticAgentState):
        user_input = state.get("user_input") or (
            state["dialogue_history"][-1]["content"] if state.get("dialogue_history") else ""
        )

        # Immediate exit bypass: if user typed exit / quit / q
        if state.get("is_solved") or user_input.lower().strip() in ["exit", "quit", "q"]:
            EventBus.emit_evaluator_verdict("SOLVED")
            return {
                "eval_status": "surrendered",
                "is_solved": True,
            }

        prompt = EvaluationPrompt.evaluation_prompt(
            error_type=state["error_type"],
            code_snippet=state["code_snippet"],
            root_cause=state["root_cause"],
            user_input=user_input,
        )

        response = LLMFactory.get_llm().invoke(prompt)
        verdict = response.content.strip().upper()

        if "SOLVED" in verdict and "UNSOLVED" not in verdict and "NOT SOLVED" not in verdict:
            verdict_key = "SOLVED"
            status = "solved"
            is_solved = True
        elif "SURRENDERED" in verdict:
            verdict_key = "SURRENDERED"
            status = "surrendered"
            is_solved = True
        else:
            verdict_key = "STRUGGLING"
            status = "struggling"
            is_solved = False

        EventBus.emit_evaluator_verdict(verdict_key)

        return {
            "eval_status": status,
            "is_solved": is_solved,
        }
