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
Solver Configuration
====================

Unified configuration for the mathematical solver with safety limits,
timeout settings, and logging options.

Configuration Priority (highest to lowest):
1. Explicit parameter values
2. Environment variables (MATH_SOLVER_*)
3. Configuration file (if specified)
4. Default values
"""

import os
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, Literal, Callable, Union, Type, Tuple

logger = logging.getLogger(__name__)

# Type for converter functions
ConverterType = Union[Type[float], Type[int], Type[str], Callable[[str], bool]]


@dataclass
class SolverConfig:
    """
    Unified configuration for the mathematical solver.

    Controls timeouts, safety limits, logging, and parallelism.

    Attributes:
        timeout_sec: Maximum wall-clock time per problem (default: 60.0)
        max_steps: Maximum agent steps per problem (default: 1000)
        max_recursion_depth: Maximum recursion depth for solvers (default: 50)
        max_parallel_problems: Maximum concurrent problems (default: 4)
        log_level: Logging level (default: "INFO")
        log_format: Logging format - "pretty" or "json" (default: "pretty")
        enable_timeouts: Whether to enforce timeouts (default: True)
        enable_caching: Whether to cache results (default: True)
        strict_mode: Fail fast on any error (default: False)

    Environment Variables:
        MATH_SOLVER_TIMEOUT_SEC: Override timeout_sec
        MATH_SOLVER_MAX_STEPS: Override max_steps
        MATH_SOLVER_LOG_LEVEL: Override log_level
        MATH_SOLVER_LOG_FORMAT: Override log_format

    Example:
        >>> config = SolverConfig(timeout_sec=30.0, max_steps=500)
        >>> config = SolverConfig.from_env()  # Load from environment
        >>> config = SolverConfig.from_file("config.yaml")  # Load from file
    """

    # Timeout and limits
    timeout_sec: float = 60.0
    max_steps: int = 1000
    max_recursion_depth: int = 50
    max_parallel_problems: int = 4

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["pretty", "json"] = "pretty"

    # Behavior flags
    enable_timeouts: bool = True
    enable_caching: bool = True
    strict_mode: bool = False

    # Advanced settings
    specialist_timeout_sec: float = 30.0
    expression_max_depth: int = 100
    expression_max_length: int = 10000

    def __post_init__(self):
        """Apply environment variable overrides after initialization."""
        self._apply_env_overrides()
        self._validate()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        def _parse_bool(x: str) -> bool:
            return x.lower() in ("true", "1", "yes")

        env_mappings: Dict[str, Tuple[str, ConverterType]] = {
            "MATH_SOLVER_TIMEOUT_SEC": ("timeout_sec", float),
            "MATH_SOLVER_MAX_STEPS": ("max_steps", int),
            "MATH_SOLVER_MAX_RECURSION_DEPTH": ("max_recursion_depth", int),
            "MATH_SOLVER_MAX_PARALLEL": ("max_parallel_problems", int),
            "MATH_SOLVER_LOG_LEVEL": ("log_level", str),
            "MATH_SOLVER_LOG_FORMAT": ("log_format", str),
            "MATH_SOLVER_ENABLE_TIMEOUTS": ("enable_timeouts", _parse_bool),
            "MATH_SOLVER_STRICT_MODE": ("strict_mode", _parse_bool),
        }

        for env_var, (attr, converter) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    setattr(self, attr, converter(value))
                    logger.debug(f"Config override from env: {attr}={getattr(self, attr)}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid env var {env_var}={value}: {e}")

    def _validate(self) -> None:
        """Validate configuration values."""
        if self.timeout_sec <= 0:
            raise ValueError(f"timeout_sec must be positive, got {self.timeout_sec}")
        if self.max_steps <= 0:
            raise ValueError(f"max_steps must be positive, got {self.max_steps}")
        if self.max_recursion_depth <= 0:
            raise ValueError(f"max_recursion_depth must be positive, got {self.max_recursion_depth}")
        if self.max_parallel_problems <= 0:
            raise ValueError(f"max_parallel_problems must be positive, got {self.max_parallel_problems}")
        if self.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            raise ValueError(f"Invalid log_level: {self.log_level}")
        if self.log_format not in ("pretty", "json"):
            raise ValueError(f"Invalid log_format: {self.log_format}")

    @classmethod
    def from_env(cls) -> "SolverConfig":
        """
        Create configuration from environment variables.

        Returns:
            SolverConfig: Configuration with environment overrides applied
        """
        return cls()  # __post_init__ handles env overrides

    @classmethod
    def from_file(cls, path: str) -> "SolverConfig":
        """
        Load configuration from a YAML or JSON file.

        Args:
            path: Path to configuration file

        Returns:
            SolverConfig: Configuration loaded from file
        """
        file_path = Path(path)
        if not file_path.exists():
            logger.warning(f"Config file not found: {path}, using defaults")
            return cls()

        try:
            with open(file_path, 'r') as f:
                if file_path.suffix in ('.yaml', '.yml'):
                    try:
                        import yaml
                        data = yaml.safe_load(f)
                    except ImportError:
                        logger.warning("PyYAML not installed, trying JSON")
                        f.seek(0)
                        data = json.load(f)
                else:
                    data = json.load(f)

            # Extract solver config section if present
            if "solver" in data:
                data = data["solver"]

            # Filter to valid fields
            valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in data.items() if k in valid_fields}

            return cls(**filtered_data)

        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
            return cls()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dict containing all configuration values
        """
        return {
            "timeout_sec": self.timeout_sec,
            "max_steps": self.max_steps,
            "max_recursion_depth": self.max_recursion_depth,
            "max_parallel_problems": self.max_parallel_problems,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "enable_timeouts": self.enable_timeouts,
            "enable_caching": self.enable_caching,
            "strict_mode": self.strict_mode,
            "specialist_timeout_sec": self.specialist_timeout_sec,
            "expression_max_depth": self.expression_max_depth,
            "expression_max_length": self.expression_max_length,
        }

    def save_to_file(self, path: str) -> None:
        """
        Save configuration to a file.

        Args:
            path: Path to save configuration
        """
        file_path = Path(path)
        with open(file_path, 'w') as f:
            if file_path.suffix in ('.yaml', '.yml'):
                try:
                    import yaml
                    yaml.dump({"solver": self.to_dict()}, f, default_flow_style=False)
                except ImportError:
                    json.dump({"solver": self.to_dict()}, f, indent=2)
            else:
                json.dump({"solver": self.to_dict()}, f, indent=2)
