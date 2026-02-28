"""
Legacy config module - redirects to core.config.

Для нового кода используйте: from core.config import settings
"""

from core.config import settings

# Legacy compatibility
config_env = settings
API_KEY = settings.API_KEY if hasattr(settings, 'API_KEY') else None

__all__ = ["settings", "config_env", "API_KEY"]