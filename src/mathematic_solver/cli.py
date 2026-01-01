"""CLI entrypoint shim for mathematic_solver."""

from symbo_agentic_reasoners.cli import *  # noqa: F403,F401
from symbo_agentic_reasoners.cli import main

__all__ = [name for name in globals() if not name.startswith("_")]
