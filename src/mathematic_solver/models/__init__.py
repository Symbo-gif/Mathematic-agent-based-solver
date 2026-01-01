"""Domain model placeholders for mathematic_solver.

The current implementation reuses models defined under the
``symbo_agentic_reasoners`` package. Additional domain models can be placed
here as the refactor progresses.
"""

try:
    from symbo_agentic_reasoners import models as _legacy_models  # type: ignore
except ImportError:
    _legacy_models = None

if _legacy_models:
    globals().update(
        {
            name: getattr(_legacy_models, name)
            for name in dir(_legacy_models)
            if not name.startswith("_")
        }
    )

__all__ = [name for name in globals() if not name.startswith("_")]
