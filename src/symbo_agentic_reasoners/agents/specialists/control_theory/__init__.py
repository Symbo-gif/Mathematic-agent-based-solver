# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Control Theory & Dynamical Systems Specialists Package
========================================================

Provides comprehensive control theory and dynamical systems capabilities:
- DynamicalSystemsSpecialist: Fixed points, stability, Lyapunov, bifurcations
- LinearControlSpecialist: State-space, controllability, observability, LQR

NO SYMPY - Pure Python/NumPy implementation.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'DynamicalSystemsSpecialist':
        from .dynamical_systems_specialist import DynamicalSystemsSpecialist
        return DynamicalSystemsSpecialist
    elif name == 'StabilityType':
        from .dynamical_systems_specialist import StabilityType
        return StabilityType
    elif name == 'BifurcationType':
        from .dynamical_systems_specialist import BifurcationType
        return BifurcationType
    elif name == 'FixedPointResult':
        from .dynamical_systems_specialist import FixedPointResult
        return FixedPointResult
    elif name == 'TrajectoryResult':
        from .dynamical_systems_specialist import TrajectoryResult
        return TrajectoryResult
    elif name == 'LyapunovResult':
        from .dynamical_systems_specialist import LyapunovResult
        return LyapunovResult
    elif name == 'LinearControlSpecialist':
        from .linear_control_specialist import LinearControlSpecialist
        return LinearControlSpecialist
    elif name == 'StateSpaceSystem':
        from .linear_control_specialist import StateSpaceSystem
        return StateSpaceSystem
    elif name == 'ControllabilityResult':
        from .linear_control_specialist import ControllabilityResult
        return ControllabilityResult
    elif name == 'ObservabilityResult':
        from .linear_control_specialist import ObservabilityResult
        return ObservabilityResult
    elif name == 'LQRResult':
        from .linear_control_specialist import LQRResult
        return LQRResult
    elif name == 'TransferFunction':
        from .linear_control_specialist import TransferFunction
        return TransferFunction
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Dynamical systems
    "DynamicalSystemsSpecialist",
    "StabilityType",
    "BifurcationType",
    "FixedPointResult",
    "TrajectoryResult",
    "LyapunovResult",
    # Linear control
    "LinearControlSpecialist",
    "StateSpaceSystem",
    "ControllabilityResult",
    "ObservabilityResult",
    "LQRResult",
    "TransferFunction",
]
