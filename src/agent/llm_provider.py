"""LLM Provider Factory for ClaimsIQ Nexus.

Creates LLM instances based on the configured provider (OpenAI or DeepSeek).
Both providers use ChatOpenAI since DeepSeek is OpenAI API-compatible.
"""

from langchain_openai import ChatOpenAI

from src.config import get_llm_config, LLM_PROVIDER, APP_DEBUG

# Global LLM cache to avoid recreating instances
_llm_instance = None


def get_llm(
    temperature: float = 0.1,
    timeout: int = 60,
    force_new: bool = False,
) -> ChatOpenAI:
    """Get a configured LLM instance based on the selected provider.
    
    This factory function creates a ChatOpenAI instance configured for
    either OpenAI or DeepSeek based on the LLM_PROVIDER environment variable.
    
    Args:
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        timeout: Request timeout in seconds
        force_new: If True, create a new instance instead of using cached one
        
    Returns:
        Configured ChatOpenAI instance
        
    Example:
        # Using OpenAI (default)
        export LLM_PROVIDER=openai
        llm = get_llm()
        
        # Using DeepSeek
        export LLM_PROVIDER=deepseek
        llm = get_llm()
    """
    global _llm_instance
    
    if _llm_instance is not None and not force_new:
        return _llm_instance
    
    # Get provider-specific configuration
    config = get_llm_config()
    
    if APP_DEBUG:
        print(f"[LLM Provider] Initializing {config['provider'].upper()} with model: {config['model']}")
    
    # Build LLM kwargs
    llm_kwargs = {
        "model": config["model"],
        "api_key": config["api_key"],
        "temperature": temperature,
        "timeout": timeout,
    }
    
    # Add base_url for non-OpenAI providers (like DeepSeek)
    if config["base_url"]:
        llm_kwargs["base_url"] = config["base_url"]
    
    # Create the LLM instance
    _llm_instance = ChatOpenAI(**llm_kwargs)
    
    return _llm_instance


def get_provider_info() -> dict:
    """Get information about the currently configured LLM provider.
    
    Returns:
        Dictionary with provider details (name, model, base_url)
    """
    config = get_llm_config()
    return {
        "provider": config["provider"],
        "model": config["model"],
        "base_url": config["base_url"] or "https://api.openai.com/v1",
        "is_deepseek": config["provider"] == "deepseek",
    }


def reset_llm_cache() -> None:
    """Reset the cached LLM instance.
    
    Useful when switching providers or updating configuration.
    """
    global _llm_instance
    _llm_instance = None
