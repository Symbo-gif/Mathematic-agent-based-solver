"""Configuration exposure for mathematic_solver."""

from symbo_agentic_reasoners import config as _config

__all__ = list(getattr(_config, "__all__", []))
globals().update({name: getattr(_config, name) for name in __all__})
