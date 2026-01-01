"""CLI entrypoint shim for mathematic_solver."""

from symbo_agentic_reasoners import cli as _cli

_exports = list(getattr(_cli, "__all__", []))
if not _exports:
    # Expected public CLI surface when legacy module lacks __all__
    _exports = ["MathSolverCLI", "main"]

__all__ = []
for _name in _exports:
    if hasattr(_cli, _name):
        globals()[_name] = getattr(_cli, _name)
        __all__.append(_name)
