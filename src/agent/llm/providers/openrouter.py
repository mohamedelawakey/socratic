from langchain_openrouter import ChatOpenRouter
from src.utils.read_yaml import ReadYaml


class OpenRouterLLM:
    @staticmethod
    def openrouter_llm():
        config = ReadYaml.read_yaml()

        return ChatOpenRouter(
            model=config["provider_name"],
            base_url=config["provider_link"],
            api_key=config["api_key"],
        )
