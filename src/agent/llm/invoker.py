import time
from src.agent.llm.factory import LLMFactory
from ui.app import bridge


class LLMInvoker:
    @staticmethod
    def invoke_with_retry(prompt: str):
        while True:
            try:
                return LLMFactory.get_llm().invoke(prompt)
            except Exception as e:
                bridge.llm_error_occurred.emit(str(e))
                time.sleep(2)
