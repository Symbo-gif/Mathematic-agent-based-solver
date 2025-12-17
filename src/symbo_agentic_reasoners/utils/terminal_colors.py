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
Terminal Color Theme for Symbo Math
====================================

Color scheme matching the Symbo Math brand:
- Gold (replaces white) - Primary text, success messages
- Teal (replaces blue) - Info, system messages, accents
- Vibrant Green - Success indicators
- Blood Red - Errors

Uses ANSI escape codes with colorama for cross-platform support.
"""

import sys
import os

# Try to import colorama for Windows support
try:
    import colorama
    colorama.init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        # Enable UTF-8 output on Windows
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8
    except Exception:
        pass

# Detect if we're in a terminal that supports colors
def supports_color():
    """Check if the terminal supports ANSI colors."""
    # Check for NO_COLOR environment variable (standard)
    if os.environ.get('NO_COLOR'):
        return False

    # Check for FORCE_COLOR environment variable
    if os.environ.get('FORCE_COLOR'):
        return True

    # Check if stdout is a TTY
    if not hasattr(sys.stdout, 'isatty'):
        return False

    if not sys.stdout.isatty():
        return False

    # Windows needs colorama
    if sys.platform == 'win32':
        return HAS_COLORAMA

    return True

# Enable colors by default if supported
COLORS_ENABLED = supports_color()


# =============================================================================
# ANSI Color Codes - Symbo Math Theme
# =============================================================================

class TerminalColors:
    """
    Terminal color codes matching Symbo Math brand colors.

    Uses 256-color mode for richer gold/teal colors when available,
    falls back to basic ANSI colors otherwise.
    """

    # Reset
    RESET = '\033[0m'

    # === GOLD (replaces white) - Primary/Highlight ===
    # 256-color gold: color 220 (gold) or 178 (dark gold)
    GOLD = '\033[38;5;220m'           # Bright gold - FFD700
    GOLD_DARK = '\033[38;5;178m'      # Dark gold/bronze - D7AF00
    GOLD_LIGHT = '\033[38;5;229m'     # Pale gold - FFFFAF

    # === TEAL (replaces blue) - Info/System ===
    # 256-color teal: color 30 (dark teal) or 37 (cyan)
    TEAL = '\033[38;5;37m'            # Teal/cyan - 00AFAF
    TEAL_DARK = '\033[38;5;30m'       # Dark teal - 008787
    TEAL_LIGHT = '\033[38;5;51m'      # Light cyan - 00FFFF
    TEAL_GLOW = '\033[38;5;44m'       # Turquoise glow - 00D7D7

    # === VIBRANT GREEN - Success ===
    # 256-color green: color 46 (bright green) or 40 (lime)
    GREEN = '\033[38;5;46m'           # Vibrant green - 00FF00
    GREEN_DARK = '\033[38;5;34m'      # Emerald - 00AF00
    GREEN_LIGHT = '\033[38;5;82m'     # Lime green - 5FFF00

    # === BLOOD RED - Errors ===
    # 256-color red: color 160 (dark red) or 196 (bright red)
    RED = '\033[38;5;196m'            # Bright red - FF0000
    RED_DARK = '\033[38;5;124m'       # Blood red/crimson - AF0000
    RED_BLOOD = '\033[38;5;160m'      # Deep blood red - D70000

    # === ADDITIONAL UTILITY COLORS ===
    YELLOW = '\033[38;5;226m'         # Warning yellow
    ORANGE = '\033[38;5;208m'         # Orange accent
    PURPLE = '\033[38;5;135m'         # Purple accent
    DIM = '\033[38;5;245m'            # Dimmed/muted text
    WHITE = '\033[38;5;255m'          # Pure white (for contrast)

    # === STYLE MODIFIERS ===
    BOLD = '\033[1m'
    DIM_STYLE = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'

    # === SEMANTIC ALIASES (for easy use) ===
    # These map to the Symbo brand colors
    SUCCESS = GREEN                    # Vibrant green for success
    ERROR = RED_BLOOD                  # Blood red for errors
    WARNING = YELLOW                   # Yellow for warnings
    INFO = TEAL                        # Teal for info messages
    HIGHLIGHT = GOLD                   # Gold for highlights/emphasis
    PRIMARY = GOLD                     # Gold as primary color
    SECONDARY = TEAL                   # Teal as secondary color
    MUTED = DIM                        # Dimmed text
    PROMPT = TEAL_GLOW                 # Prompt color
    RESULT = GOLD_LIGHT                # Result display
    BANNER = GOLD                      # Banner/header text


# Singleton instance
C = TerminalColors()


def color(text: str, color_code: str) -> str:
    """
    Apply a color to text.

    Args:
        text: The text to colorize
        color_code: ANSI color code from TerminalColors

    Returns:
        Colorized string if colors enabled, plain text otherwise
    """
    if not COLORS_ENABLED:
        return text
    return f"{color_code}{text}{C.RESET}"


def gold(text: str) -> str:
    """Apply gold color (primary/highlight)."""
    return color(text, C.GOLD)


def teal(text: str) -> str:
    """Apply teal color (info/system)."""
    return color(text, C.TEAL)


def green(text: str) -> str:
    """Apply vibrant green color (success)."""
    return color(text, C.GREEN)


def red(text: str) -> str:
    """Apply blood red color (errors)."""
    return color(text, C.RED_BLOOD)


def success(text: str) -> str:
    """Format as success message (vibrant green)."""
    return color(text, C.SUCCESS)


def error(text: str) -> str:
    """Format as error message (blood red)."""
    return color(text, C.ERROR)


def warning(text: str) -> str:
    """Format as warning message (yellow)."""
    return color(text, C.WARNING)


def info(text: str) -> str:
    """Format as info message (teal)."""
    return color(text, C.INFO)


def highlight(text: str) -> str:
    """Format as highlighted text (gold)."""
    return color(text, C.HIGHLIGHT)


def dim(text: str) -> str:
    """Format as dimmed/muted text."""
    return color(text, C.DIM)


def bold(text: str, color_code: str = None) -> str:
    """Apply bold style, optionally with color."""
    if not COLORS_ENABLED:
        return text
    if color_code:
        return f"{C.BOLD}{color_code}{text}{C.RESET}"
    return f"{C.BOLD}{text}{C.RESET}"


# =============================================================================
# Formatted Output Helpers
# =============================================================================

def print_banner(text: str):
    """Print a banner/header in gold."""
    print(color(text, C.GOLD + C.BOLD))


def print_success(text: str):
    """Print a success message in vibrant green."""
    print(color(text, C.SUCCESS))


def print_error(text: str):
    """Print an error message in blood red."""
    print(color(text, C.ERROR))


def print_warning(text: str):
    """Print a warning message in yellow."""
    print(color(text, C.WARNING))


def print_info(text: str):
    """Print an info message in teal."""
    print(color(text, C.INFO))


def print_result(label: str, value: str):
    """Print a result with gold label and teal value."""
    if COLORS_ENABLED:
        print(f"{C.GOLD}{label}{C.RESET} {C.TEAL_GLOW}{value}{C.RESET}")
    else:
        print(f"{label} {value}")


def format_ok(text: str) -> str:
    """Format [OK] style message."""
    if COLORS_ENABLED:
        return f"{C.GREEN}[OK]{C.RESET} {C.GOLD}{text}{C.RESET}"
    return f"[OK] {text}"


def format_error(text: str) -> str:
    """Format [ERROR] style message."""
    if COLORS_ENABLED:
        return f"{C.RED_BLOOD}[ERROR]{C.RESET} {C.RED_BLOOD}{text}{C.RESET}"
    return f"[ERROR] {text}"


def format_info(text: str) -> str:
    """Format [INFO] style message."""
    if COLORS_ENABLED:
        return f"{C.TEAL}[INFO]{C.RESET} {C.TEAL}{text}{C.RESET}"
    return f"[INFO] {text}"


def format_init(text: str) -> str:
    """Format [INIT] style message."""
    if COLORS_ENABLED:
        return f"{C.TEAL_DARK}[INIT]{C.RESET} {C.TEAL}{text}{C.RESET}"
    return f"[INIT] {text}"


def format_batch(text: str) -> str:
    """Format [BATCH] style message."""
    if COLORS_ENABLED:
        return f"{C.GOLD_DARK}[BATCH]{C.RESET} {C.GOLD}{text}{C.RESET}"
    return f"[BATCH] {text}"


def format_warn(text: str) -> str:
    """Format [WARN] style message."""
    if COLORS_ENABLED:
        return f"{C.YELLOW}[WARN]{C.RESET} {C.YELLOW}{text}{C.RESET}"
    return f"[WARN] {text}"


# =============================================================================
# CLI-Specific Helpers
# =============================================================================

def format_prompt() -> str:
    """Get the formatted math prompt."""
    if COLORS_ENABLED:
        return f"{C.TEAL_GLOW}math>{C.RESET} "
    return "math> "


def format_result_success(result: str, domain: str = None, specialist: str = None, time_ms: float = None) -> str:
    """Format a successful result."""
    lines = []
    if COLORS_ENABLED:
        lines.append(f"  {C.GREEN}\u2713{C.RESET} {C.GOLD}Result:{C.RESET} {C.GOLD_LIGHT}{result}{C.RESET}")
        if domain:
            lines.append(f"    {C.DIM}Domain:{C.RESET} {C.TEAL}{domain}{C.RESET}")
        if specialist:
            lines.append(f"    {C.DIM}Solved by:{C.RESET} {C.TEAL}{specialist}{C.RESET}")
        if time_ms is not None:
            lines.append(f"    {C.DIM}Time:{C.RESET} {C.TEAL}{time_ms:.1f}ms{C.RESET}")
    else:
        lines.append(f"  \u2713 Result: {result}")
        if domain:
            lines.append(f"    Domain: {domain}")
        if specialist:
            lines.append(f"    Solved by: {specialist}")
        if time_ms is not None:
            lines.append(f"    Time: {time_ms:.1f}ms")
    return '\n'.join(lines)


def format_result_failure(error: str, time_ms: float = None) -> str:
    """Format a failed result."""
    lines = []
    if COLORS_ENABLED:
        lines.append(f"  {C.RED_BLOOD}\u2717{C.RESET} {C.RED_BLOOD}Failed:{C.RESET} {C.RED}{error}{C.RESET}")
        if time_ms is not None:
            lines.append(f"    {C.DIM}Time:{C.RESET} {C.TEAL}{time_ms:.1f}ms{C.RESET}")
    else:
        lines.append(f"  \u2717 Failed: {error}")
        if time_ms is not None:
            lines.append(f"    Time: {time_ms:.1f}ms")
    return '\n'.join(lines)


def format_banner() -> str:
    """Get the formatted CLI banner."""
    # Use ASCII-safe characters for maximum compatibility
    if COLORS_ENABLED:
        return f"""{C.GOLD}
+==============================================================================+
|{C.GOLD_LIGHT}                    SYMBO AGENTIC REASONERS v1.0                              {C.GOLD}|
|{C.TEAL}                 Mathematical Agent-Based Solver System                        {C.GOLD}|
|{C.TEAL_GLOW}                        65 Agents | 24 Teams | 6 Phases                       {C.GOLD}|
+==============================================================================+{C.RESET}
    """
    else:
        return """
+==============================================================================+
|                    SYMBO AGENTIC REASONERS v1.0                              |
|                 Mathematical Agent-Based Solver System                        |
|                        65 Agents | 24 Teams | 6 Phases                       |
+==============================================================================+
    """


def format_divider(char: str = '-', width: int = 78) -> str:
    """Get a formatted divider line."""
    if COLORS_ENABLED:
        return f"{C.DIM}{char * width}{C.RESET}"
    return char * width


def format_status_running(status_text: str) -> str:
    """Format running status indicator."""
    if COLORS_ENABLED:
        return f"{C.GREEN}\u2713{C.RESET} {C.GREEN}Running{C.RESET}"
    return "\u2713 Running"


def format_status_stopped(status_text: str) -> str:
    """Format stopped status indicator."""
    if COLORS_ENABLED:
        return f"{C.RED}\u2717{C.RESET} {C.DIM}Stopped{C.RESET}"
    return "\u2717 Stopped"


# =============================================================================
# Export all
# =============================================================================

__all__ = [
    'TerminalColors', 'C', 'COLORS_ENABLED',
    'color', 'gold', 'teal', 'green', 'red',
    'success', 'error', 'warning', 'info', 'highlight', 'dim', 'bold',
    'print_banner', 'print_success', 'print_error', 'print_warning', 'print_info', 'print_result',
    'format_ok', 'format_error', 'format_info', 'format_init', 'format_batch', 'format_warn',
    'format_prompt', 'format_result_success', 'format_result_failure',
    'format_banner', 'format_divider', 'format_status_running', 'format_status_stopped',
]
