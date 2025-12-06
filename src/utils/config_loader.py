"""
Configuration loading utilities.
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any

from src.models.config import Config
from src.utils.exceptions import ConfigurationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Optional path to config file. If None, uses default path.
        
    Returns:
        Config object with loaded configuration
        
    Raises:
        ConfigurationError: If config file cannot be loaded or is invalid
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    
    try:
        logger.info(f"Loading configuration from {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        if not config_dict:
            raise ConfigurationError("Configuration file is empty")
        
        config = Config.from_dict(config_dict)
        
        # Validate weights
        if not config.weights.validate():
            logger.warning("Weights do not sum to 1.0, but continuing...")
        
        logger.info("Configuration loaded successfully")
        return config
        
    except FileNotFoundError:
        error_msg = f"Configuration file not found: {config_path}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg) from None
    except yaml.YAMLError as e:
        error_msg = f"Error parsing YAML configuration: {e}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error loading configuration: {e}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg) from e


def get_weights_dict(config: Config) -> Dict[str, float]:
    """
    Get weights dictionary from config.
    
    Args:
        config: Config object
        
    Returns:
        Dictionary with weight values
    """
    return {
        "size": config.weights.size,
        "growth": config.weights.growth,
        "profitability": config.weights.profitability,
        "debt": config.weights.debt,
        "risk": config.weights.risk,
    }

