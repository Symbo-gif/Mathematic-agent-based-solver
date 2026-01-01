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
SYMBO_AGENTIC_REASONERS Utilities
"""
from pathlib import Path

# Path constants
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
TRACE_DIR = DATA_DIR / "traces"
OUTPUT_DIR = DATA_DIR / "output"

# Terminal colors
from symbo_agentic_reasoners.utils.terminal_colors import (
    C, TerminalColors, COLORS_ENABLED,
    gold, teal, green, red, info, success, error, warning, dim, bold,
    format_ok, format_error, format_info, format_init, format_batch, format_warn,
    format_banner, format_divider, format_prompt
)

__all__ = [
    # Paths
    "PROJECT_ROOT", "SRC_ROOT", "DATA_DIR", "TRACE_DIR", "OUTPUT_DIR",
    # Terminal colors
    "C", "TerminalColors", "COLORS_ENABLED",
    "gold", "teal", "green", "red", "info", "success", "error", "warning", "dim", "bold",
    "format_ok", "format_error", "format_info", "format_init", "format_batch", "format_warn",
    "format_banner", "format_divider", "format_prompt"
]
