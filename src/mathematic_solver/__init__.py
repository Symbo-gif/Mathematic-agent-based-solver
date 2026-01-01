"""
Mathematic Solver package shim.

This package provides the new canonical import path while delegating to the
existing ``symbo_agentic_reasoners`` implementation to avoid breaking changes
during the refactor.
"""

from importlib import import_module

core = import_module("symbo_agentic_reasoners.core")
agents = import_module("symbo_agentic_reasoners.agents")
utils = import_module("symbo_agentic_reasoners.utils")
config = import_module("symbo_agentic_reasoners.config")

__all__ = ["core", "agents", "utils", "config"]
