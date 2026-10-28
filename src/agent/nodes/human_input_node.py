from src.agent.state.state import SocraticAgentState
from src.events import EventBus


class HumanInputNode:
    @staticmethod
    def human_input_node(state: SocraticAgentState) -> dict:
        user_input = EventBus.request_user_input()

        history = list(state.get("dialogue_history", []))
        history.append({"role": "student", "content": user_input})

        if user_input.lower().strip() in ["exit", "quit", "q"]:
            return {
                "user_input": user_input,
                "dialogue_history": history,
                "is_solved": True,
                "eval_status": "surrendered",
            }

        return {"user_input": user_input, "dialogue_history": history}
