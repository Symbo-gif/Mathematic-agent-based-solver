"""Domain model placeholders for mathematic_solver.

If legacy models exist under ``symbo_agentic_reasoners.models``, they are
re-exported here. Otherwise, the module remains empty until models are added
under the new namespace.
"""

import warnings

try:
    from symbo_agentic_reasoners import models as _models  # type: ignore
except ImportError:
    __all__ = []
else:
    __all__ = list(getattr(_models, "__all__", []))
    for name in __all__:
        if hasattr(_models, name):
            globals()[name] = getattr(_models, name)
        else:
            warnings.warn("Symbol not found in legacy models module", RuntimeWarning)
