from src.agent.llm.providers import *
from src.utils.read_yaml import ReadYaml


class LLMFactory:
    @staticmethod
    def get_llm():
        config = ReadYaml.read_yaml()

        if config["provider"] == "openrouter":
            return OpenRouterLLM.openrouter_llm()
        elif config["provider"] == "ollama":
            return OllamaLLM.ollama_llm()
        else:
            raise ValueError("Invalid provider")
