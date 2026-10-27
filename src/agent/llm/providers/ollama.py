from langchain_ollama import ChatOllama
from src.utils.read_yaml import ReadYaml


class OllamaLLM:
    @staticmethod
    def ollama_llm():
        config = ReadYaml.read_yaml()

        return ChatOllama (
            model=config["provider_name"],
            base_url=config["provider_link"],
        )
