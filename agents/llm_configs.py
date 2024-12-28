class AnalystConfig:
    LLM_MODEL = "llama3.2:3b"
    BASE_URL = "http://localhost:11434/v1"
    API_KEY = "ollama"  # dummy key, required by autogen
    TEMPERATURE = 0.85

class ManagerConfig:
    LLM_MODEL = "mistral"
    BASE_URL = "http://localhost:11434/v1"
    API_KEY = "mistral"  # dummy key, required by autogen
    TEMPERATURE = 0.85  # Different temperature for the manager