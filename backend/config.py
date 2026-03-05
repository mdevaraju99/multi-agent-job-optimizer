import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "multi-agent-job-optimizer")
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    
    # Models
    MODEL_NAME = "llama-3.3-70b-versatile" # High performance model
    FAST_MODEL_NAME = "llama-3.1-8b-instant" # Faster model for simple tasks
    
    # App Settings
    PROJECT_NAME = "Multi-Agent Job Optimizer"
    VERSION = "0.1.0"
    API_PREFIX = "/api"

settings = Settings()
