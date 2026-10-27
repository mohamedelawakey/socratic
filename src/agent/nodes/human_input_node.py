from src.agent.state.state import SocraticAgentState
from ui.views import SocraticUI
from ui.console import console


class HumanInputNode:
    @staticmethod
    def human_input_node(state: SocraticAgentState) -> dict:
        user_input = SocraticUI.prompt_user_input()

        if user_input.lower().strip() in ["exit", "quit", "q"]:
            console.print("\n[bold yellow]👋 Exiting Socratic debugging session. Keep coding![/bold yellow]\n")
            return {"is_solved": True}

        history = list(state.get("dialogue_history", []))
        history.append({"role": "student", "content": user_input})
        
        return {"user_input": user_input, "dialogue_history": history}
