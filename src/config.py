"""Configuration module for ClaimsIQ Nexus.

Loads environment variables from .env file using python-dotenv.
Supports multiple LLM providers (OpenAI and DeepSeek).
"""

import os
from typing import Literal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# LLM Provider Configuration
LLM_PROVIDER: Literal["openai", "deepseek"] = os.getenv("LLM_PROVIDER", "openai").lower()  # type: ignore

# OpenAI Configuration
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# DeepSeek Configuration
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# Application Configuration
APP_DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"
APP_LOG_LEVEL: str = os.getenv("APP_LOG_LEVEL", "INFO")

# Performance Thresholds (in milliseconds)
TIMEOUT_API: int = int(os.getenv("TIMEOUT_API", "60000"))
TIMEOUT_VECTOR_SEARCH: int = int(os.getenv("TIMEOUT_VECTOR_SEARCH", "5000"))
TIMEOUT_GRAPH_RENDER: int = int(os.getenv("TIMEOUT_GRAPH_RENDER", "5000"))

# Data Configuration
CLAIMS_COUNT: int = int(os.getenv("CLAIMS_COUNT", "1500"))
CLINICAL_NOTES_COUNT: int = int(os.getenv("CLINICAL_NOTES_COUNT", "25"))
FRAUD_RING_ENABLED: bool = os.getenv("FRAUD_RING_ENABLED", "true").lower() == "true"
GOLDEN_NUGGETS_COUNT: int = int(os.getenv("GOLDEN_NUGGETS_COUNT", "3"))

# File Paths
DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
GENERATED_DATA_DIR: str = os.path.join(DATA_DIR, "generated")
CLAIMS_CSV_PATH: str = os.path.join(GENERATED_DATA_DIR, "claims.csv")
CLINICAL_NOTES_DIR: str = os.path.join(GENERATED_DATA_DIR, "clinical_notes")
GOLDEN_PATH_DIR: str = os.path.join(DATA_DIR, "golden_path")


def get_llm_config() -> dict:
    """Get the LLM configuration based on the selected provider.
    
    Returns:
        Dictionary containing:
            - api_key: API key for the provider
            - model: Model name to use
            - base_url: Base URL for the API (None for OpenAI default)
            - provider: The provider name
    """
    if LLM_PROVIDER == "deepseek":
        return {
            "api_key": DEEPSEEK_API_KEY,
            "model": DEEPSEEK_MODEL,
            "base_url": DEEPSEEK_BASE_URL,
            "provider": "deepseek",
        }
    else:
        # Default to OpenAI
        return {
            "api_key": OPENAI_API_KEY,
            "model": OPENAI_MODEL,
            "base_url": None,  # Use default OpenAI base URL
            "provider": "openai",
        }


def validate_config() -> bool:
    """Validate that required configuration is present."""
    llm_config = get_llm_config()
    
    if not llm_config["api_key"]:
        provider = llm_config["provider"].upper()
        raise ValueError(f"{provider}_API_KEY environment variable is required when using {provider} provider")
    
    return True
