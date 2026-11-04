import os
import time
from src.agent.llm.factory import LLMFactory
from src.events import EventBus


class LLMInvoker:
    @staticmethod
    def invoke_with_retry(prompt: str, max_headless_retries: int = 3):
        is_gui = os.environ.get("SOCRATIC_GUI_ACTIVE") == "1"
        attempts = 0

        while True:
            if EventBus.is_session_cancelled():
                raise RuntimeError("Session was cancelled by user.")

            try:
                return LLMFactory.get_llm().invoke(prompt)
            except Exception as e:
                err_msg = str(e)
                EventBus.emit_llm_error(err_msg)

                if not is_gui:
                    attempts += 1
                    if attempts >= max_headless_retries:
                        raise RuntimeError(f"LLM invocation failed after {attempts} attempts: {err_msg}") from e

                time.sleep(2)
