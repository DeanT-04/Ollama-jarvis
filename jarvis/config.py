#!/usr/bin/env python3
"""
Configuration module for Jarvis.

This module provides functions for loading and accessing configuration settings
from environment variables and configuration files.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Default configuration values
DEFAULT_CONFIG = {
    # Ollama configuration
    "OLLAMA_API_BASE": "http://localhost:11434",
    "OLLAMA_MODEL": "gemma3:4b",
    "TEMPERATURE": 0.7,
    "MAX_TOKENS": 1000,

    # Workspace configuration
    "WORKSPACE_DIR": os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jarvis_workspace"),

    # Execution configuration
    "MAX_RETRIES": 2,
    "SECURITY_LEVEL": "medium",  # Options: low, medium, high

    # Memory configuration
    "USER_ID": "jarvis_user",
    "NO_MEMORY": False,
    "DISABLE_MEMORY": False,
    "MEMORY_FILE": None,

    # Web search configuration
    "WEB_SEARCH_ENABLED": True,
    "WEB_SEARCH_MAX_RESULTS": 3,

    # Perplexica configuration
    "PERPLEXICA_URL": "http://localhost:3000",
    "PERPLEXICA_CHAT_MODEL_PROVIDER": "ollama",
    "PERPLEXICA_CHAT_MODEL_NAME": "gemma3:4b",
    "PERPLEXICA_EMBEDDING_MODEL_PROVIDER": "ollama",
    "PERPLEXICA_EMBEDDING_MODEL_NAME": "gemma3:4b",
    "PERPLEXICA_FOCUS_MODE": "webSearch",
    "PERPLEXICA_OPTIMIZATION_MODE": "balanced",

    # System configuration
    "SYSTEM_PROMPT": None,
    "DEBUG": False,
}

# Configuration dictionary
CONFIG: Dict[str, Any] = {}


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables and default values.

    Returns:
        A dictionary containing the configuration settings.
    """
    global CONFIG

    # Start with default configuration
    config = DEFAULT_CONFIG.copy()

    # Override with environment variables
    for key in config:
        env_value = os.getenv(key)
        if env_value is not None:
            # Convert boolean strings to actual booleans
            if env_value.lower() in ["true", "yes", "1"]:
                config[key] = True
            elif env_value.lower() in ["false", "no", "0"]:
                config[key] = False
            # Convert numeric strings to integers or floats
            elif env_value.isdigit():
                config[key] = int(env_value)
            elif env_value.replace(".", "", 1).isdigit() and env_value.count(".") == 1:
                config[key] = float(env_value)
            else:
                config[key] = env_value

    # Ensure workspace directory exists
    os.makedirs(config["WORKSPACE_DIR"], exist_ok=True)

    # Update the global CONFIG dictionary
    CONFIG = config

    return config


def get_config(key: str, default: Optional[Any] = None) -> Any:
    """
    Get a configuration value.

    Args:
        key: The configuration key.
        default: The default value to return if the key is not found.

    Returns:
        The configuration value, or the default value if the key is not found.
    """
    global CONFIG

    # Load configuration if not already loaded
    if not CONFIG:
        load_config()

    return CONFIG.get(key, default)


# Load configuration when the module is imported
load_config()
