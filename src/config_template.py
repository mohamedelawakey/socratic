class ConfigTemplate:
    DEFAULT_CONFIG_TEMPLATE = """# Socratic Configuration
# in this file you can configure the socratic debugging tool

# LLM Configurations
provider: "ollama"
provider_name: "gemma4:31b-cloud"
provider_link: "http://localhost:11434"

# API Key (the variable name must named `api_key`)
api_key: "your_api_key"

# Socratic Mentor configuration
socratic_language: "English"
socratic_style: "friendly"

# Observability
LANGSMITH_TRACING: "true"
LANGSMITH_API_KEY: "your_langsmith_api_key"
LANGSMITH_PROJECT: "socratic-debug"
"""
