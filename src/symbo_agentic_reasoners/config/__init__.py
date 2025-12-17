# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
SYMBO_AGENTIC_REASONERS Configuration System
=============================================

Centralized configuration management for all system components.

This module provides:
- Default configuration values
- Environment variable overrides
- YAML/JSON configuration file support
- Runtime configuration validation
- Type-safe configuration access

Usage:
------
    from symbo_agentic_reasoners.config import get_config, Config

    # Get configuration singleton
    config = get_config()

    # Access values
    vram_threshold = config.hardware.vram_threshold
    default_timeout = config.timeouts.default

    # Override via environment variables
    # SYMBO_VRAM_THRESHOLD=0.85 python main.py

    # Override via config file
    config.load_from_file("config.yaml")
"""

from .settings import (
    Config,
    HardwareConfig,
    ResourceThresholds,
    TimeoutConfig,
    AgentPoolConfig,
    MonitoringConfig,
    LoggingConfig,
    PathConfig,
    get_config,
    reload_config,
)

__all__ = [
    "Config",
    "HardwareConfig",
    "ResourceThresholds",
    "TimeoutConfig",
    "AgentPoolConfig",
    "MonitoringConfig",
    "LoggingConfig",
    "PathConfig",
    "get_config",
    "reload_config",
]
