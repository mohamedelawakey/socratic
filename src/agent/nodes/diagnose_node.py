from src.agent.prompts.diagnose_prompt import DiagnosePrompt
from src.agent.state.state import SocraticAgentState
from src.agent.llm.factory import LLMFactory


class DiagnoseNode:
    @staticmethod
    def diagnose_node(state: SocraticAgentState) -> dict:
        prompt = DiagnosePrompt.diagnose_prompt(
            error_type=state["error_type"],
            error_name=state["error_name"],
            file_path=state["file_path"],
            line_number=state["line_number"],
            line_content=state["line_content"],
            code_snippet=state["code_snippet"],
            function_name=state.get("function_name") or "",
        )

        response = LLMFactory.get_llm().invoke(prompt)

        return {"root_cause": response.content}
