# Claude Code Symbo Math Launcher

A custom launcher for Claude Code that opens directly into the Symbo Math project with full context about the project, recent changes, and planned work.

## Desktop Shortcuts

| Shortcut | Description |
|----------|-------------|
| **Claude Code Symbo Math** | Opens Claude Code CLI in terminal |
| **Claude Code Symbo Math UI** | Opens graphical desktop interface |

## Files

| File | Description |
|------|-------------|
| `claude_code_ui.py` | Desktop UI application (Claude-like interface) |
| `launch_claude_symbo.bat` | CLI launcher - opens Claude Code in terminal |
| `launch_claude_ui.bat` | UI launcher - opens desktop interface |
| `launch_claude_wt.bat` | Windows Terminal version (uses WT if available) |
| `create_shortcut.ps1` | Creates CLI desktop shortcut |
| `create_ui_shortcut.ps1` | Creates UI desktop shortcut |
| `symbo_math_icon.ico` | Custom teal-on-gold Claude logo icon |
| `symbo_math_terminal_scheme.json` | Windows Terminal color scheme |
| `symbo_math_terminal_profile.json` | Full Windows Terminal profile configuration |
| `PROJECT_CONTEXT.md` | Project overview, recent changes, and planned work |

## Quick Start

### Option 1: Desktop UI (Recommended)
Double-click **"Claude Code Symbo Math UI"** on your desktop.

Features:
- Symbo Math logo (top left) + Claude logo in teal/gold (top right)
- Claude desktop app-style dark theme with Symbo Math colors
- Chat interface with message bubbles
- Integrated Claude Code CLI backend

### Option 2: Terminal CLI
Double-click **"Claude Code Symbo Math"** on your desktop.

### Option 3: Run Batch Script
```cmd
cd "c:\dev\Mathematic agent based solver"
claude-code-launcher\launch_claude_symbo.bat
```

### Option 4: Windows Terminal
```cmd
claude-code-launcher\launch_claude_wt.bat
```

## Setting Up Windows Terminal Color Scheme

1. Open Windows Terminal
2. Press `Ctrl+,` to open Settings
3. Click **"Open JSON file"** at the bottom left
4. Find the `"schemes"` array and add this color scheme:

```json
{
    "name": "Symbo Math",
    "background": "#0D1117",
    "foreground": "#E6EDF3",
    "cursorColor": "#DAA520",
    "selectionBackground": "#264F78",
    "black": "#0D1117",
    "red": "#FF7B72",
    "green": "#2ECC71",
    "yellow": "#DAA520",
    "blue": "#008B8B",
    "purple": "#A371F7",
    "cyan": "#40E0D0",
    "white": "#E6EDF3",
    "brightBlack": "#21262D",
    "brightRed": "#FFA198",
    "brightGreen": "#56D364",
    "brightYellow": "#FFD700",
    "brightBlue": "#00CED1",
    "brightPurple": "#D2A8FF",
    "brightCyan": "#79F2E6",
    "brightWhite": "#FFFFFF"
}
```

5. Save the file

### Optional: Add Dedicated Profile

Add this to the `"profiles": { "list": [...] }` section:

```json
{
    "name": "Claude Code Symbo Math",
    "commandline": "cmd.exe /k \"cd /d c:\\dev\\Mathematic agent based solver && claude-code-launcher\\launch_claude_symbo.bat\"",
    "startingDirectory": "c:\\dev\\Mathematic agent based solver",
    "colorScheme": "Symbo Math",
    "icon": "c:\\dev\\Mathematic agent based solver\\claude-code-launcher\\symbo_math_icon.ico",
    "tabTitle": "Symbo Math"
}
```

## Color Scheme

The Symbo Math theme uses colors from the project logo:

| Color | Hex | Usage |
|-------|-----|-------|
| Gold | `#DAA520` | Primary accent, cursor |
| Teal | `#008B8B` | Secondary color |
| Turquoise | `#40E0D0` | Bright cyan/teal |
| Emerald | `#2ECC71` | Success/green |
| Dark Background | `#0D1117` | Terminal background |

## Recreating the Desktop Shortcut

If you need to recreate the shortcut:

```powershell
powershell -ExecutionPolicy Bypass -File "c:\dev\Mathematic agent based solver\claude-code-launcher\create_shortcut.ps1"
```

## What Happens When You Launch

1. Terminal opens with Symbo Math color scheme
2. Changes to project directory
3. Displays project header
4. Launches Claude Code
5. Claude automatically reads PROJECT_CONTEXT.md for full context

## Updating Context

Edit `PROJECT_CONTEXT.md` to update the project information that Claude receives at the start of each session.
