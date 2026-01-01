"""
Mathematic Solver package shim.

This package provides the new canonical import path while delegating to the
existing ``symbo_agentic_reasoners`` implementation to avoid breaking changes
during the refactor.
"""

from importlib import import_module
from typing import Optional


def _safe_import(module_name: str) -> Optional[object]:
    try:
        return import_module(module_name)
    except ImportError:
        return None


core = _safe_import("symbo_agentic_reasoners.core")
agents = _safe_import("symbo_agentic_reasoners.agents")
utils = _safe_import("symbo_agentic_reasoners.utils")
config = _safe_import("symbo_agentic_reasoners.config")

_exported_modules = {
    "core": core,
    "agents": agents,
    "utils": utils,
    "config": config,
}

__all__ = [name for name, module in _exported_modules.items() if module]
