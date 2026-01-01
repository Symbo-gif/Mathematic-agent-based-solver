#!/usr/bin/env python3
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
Symbo Math GUI
==============

A visually appealing graphical interface for the SYMBO_AGENTIC_REASONERS system.

Features:
- Gold, Teal, and Emerald themed UI (matching Symbo Math logo)
- Logo displayed in top-left header
- Equation input with instant solving
- Start/Stop/Save controls
- File watcher for auto-processing new problems
- Real-time status display

Usage:
    python scripts/math_solver_ui.py
"""

import sys
import os
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from queue import Queue, Empty

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

# Try to import PIL for logo support
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Import solver components
from symbo_agentic_reasoners.core.resource_coordinator import (
    ResourceCoordinator, get_coordinator, shutdown_coordinator
)
from symbo_agentic_reasoners.core.solver_engine import (
    SolverEngine, SolveResult, SolveStatus, get_solver_engine
)

# Import imagination engine for autonomous exploration
try:
    from symbo_agentic_reasoners.discovery.imagination_engine import (
        ImaginationEngine, ExplorationResult, InterestLevel
    )
    HAS_IMAGINATION = True
except ImportError:
    HAS_IMAGINATION = False


# =============================================================================
# THEME COLORS - Matches Symbo Math Logo
# =============================================================================
class Theme:
    """Gold, Teal, and Emerald color theme matching Symbo Math logo"""
    # Primary colors - Gold/Bronze (from logo crown and face)
    GOLD_DARK = "#B8860B"      # Dark goldenrod
    GOLD_MAIN = "#DAA520"      # Goldenrod
    GOLD_LIGHT = "#FFD700"     # Gold
    GOLD_PALE = "#FFF8DC"      # Cornsilk

    # Secondary colors - Teal/Cyan (from logo accents and symbols)
    TEAL_DARK = "#006D77"
    TEAL_MAIN = "#008B8B"
    TEAL_LIGHT = "#00CED1"     # Dark turquoise
    TEAL_GLOW = "#40E0D0"      # Turquoise (for glowing effects)

    # Accent colors - Emerald Green (from logo patina)
    EMERALD_DARK = "#145A32"
    EMERALD_MAIN = "#1E8449"
    EMERALD_LIGHT = "#2ECC71"

    # Neutral colors - Dark backgrounds
    BG_DARK = "#0D1117"        # Near black
    BG_MAIN = "#161B22"        # Dark charcoal
    BG_LIGHT = "#21262D"       # Lighter charcoal
    TEXT_LIGHT = "#F0E68C"     # Khaki/light gold
    TEXT_DIM = "#8B8970"       # Dim gold/olive

    # Status colors
    SUCCESS = "#2ECC71"        # Emerald
    ERROR = "#E74C3C"
    WARNING = "#F39C12"

    # Legacy aliases for compatibility
    ORANGE_DARK = GOLD_DARK
    ORANGE_MAIN = GOLD_MAIN
    ORANGE_LIGHT = GOLD_LIGHT
    TEAL_PALE = GOLD_PALE


# =============================================================================
# FILE WATCHER
# =============================================================================
class FileWatcher:
    """Watches a file for new math problems to process"""

    def __init__(self, filepath: str, callback, check_interval: float = 2.0):
        self.filepath = Path(filepath)
        self.callback = callback
        self.check_interval = check_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_modified = 0
        self._processed_lines: set = set()

    def start(self):
        """Start watching the file"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop watching the file"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)

    def _watch_loop(self):
        """Main watch loop"""
        while self._running:
            try:
                if self.filepath.exists():
                    mtime = self.filepath.stat().st_mtime
                    if mtime > self._last_modified:
                        self._last_modified = mtime
                        self._process_new_lines()
            except Exception as e:
                pass  # Ignore file access errors
            time.sleep(self.check_interval)

    def _process_new_lines(self):
        """Process any new lines in the file"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                line = line.strip()
                line_key = f"{i}:{line}"

                if line and not line.startswith('#') and line_key not in self._processed_lines:
                    self._processed_lines.add(line_key)
                    self.callback(line)
        except Exception as e:
            pass


# =============================================================================
# MAIN APPLICATION
# =============================================================================
class MathSolverUI:
    """Main GUI application for the Math Solver"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Symbo Math")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        self.root.configure(bg=Theme.BG_DARK)

        # State
        self.coordinator: Optional[ResourceCoordinator] = None
        self.solver: Optional[SolverEngine] = None
        self.is_running = False
        self.results: List[Dict[str, Any]] = []
        self.message_queue = Queue()
        self.file_watcher: Optional[FileWatcher] = None

        # Imagination engine state
        self.imagination_engine: Optional['ImaginationEngine'] = None
        self.is_imagining = False

        # Logo path
        self.logo_path = Path(__file__).parent.parent / "Symbo Math Logo.png"
        self.logo_image = None  # Will hold PhotoImage reference

        # Watch file path
        self.watch_file = Path(__file__).parent.parent / "data" / "new_problems.txt"

        # Set window icon if logo exists
        self._set_window_icon()

        # Build UI
        self._setup_styles()
        self._build_ui()
        self._start_queue_processor()

    def _set_window_icon(self):
        """Set the window icon from logo"""
        try:
            if HAS_PIL and self.logo_path.exists():
                # Load and resize for icon
                icon_img = Image.open(self.logo_path)
                icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, self.icon_photo)
        except Exception:
            pass  # Ignore icon errors

    def _setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Button styles
        style.configure(
            "Teal.TButton",
            background=Theme.TEAL_MAIN,
            foreground=Theme.TEXT_LIGHT,
            bordercolor=Theme.TEAL_LIGHT,
            darkcolor=Theme.TEAL_DARK,
            lightcolor=Theme.TEAL_LIGHT,
            focuscolor=Theme.ORANGE_MAIN,
            padding=(20, 10),
            font=('Segoe UI', 11, 'bold')
        )
        style.map("Teal.TButton",
            background=[('active', Theme.TEAL_DARK), ('pressed', Theme.TEAL_DARK)],
            foreground=[('active', Theme.TEXT_LIGHT)]
        )

        style.configure(
            "Gold.TButton",
            background=Theme.GOLD_MAIN,
            foreground=Theme.BG_DARK,
            bordercolor=Theme.GOLD_LIGHT,
            darkcolor=Theme.GOLD_DARK,
            lightcolor=Theme.GOLD_LIGHT,
            focuscolor=Theme.TEAL_MAIN,
            padding=(20, 10),
            font=('Segoe UI', 11, 'bold')
        )
        style.map("Gold.TButton",
            background=[('active', Theme.GOLD_DARK), ('pressed', Theme.GOLD_DARK)],
            foreground=[('active', Theme.TEXT_LIGHT)]
        )

        # Alias for backwards compatibility
        style.configure(
            "Orange.TButton",
            background=Theme.GOLD_MAIN,
            foreground=Theme.BG_DARK,
            bordercolor=Theme.GOLD_LIGHT,
            darkcolor=Theme.GOLD_DARK,
            lightcolor=Theme.GOLD_LIGHT,
            focuscolor=Theme.TEAL_MAIN,
            padding=(20, 10),
            font=('Segoe UI', 11, 'bold')
        )
        style.map("Orange.TButton",
            background=[('active', Theme.GOLD_DARK), ('pressed', Theme.GOLD_DARK)],
            foreground=[('active', Theme.TEXT_LIGHT)]
        )

        style.configure(
            "Stop.TButton",
            background=Theme.ERROR,
            foreground=Theme.TEXT_LIGHT,
            bordercolor="#C0392B",
            padding=(20, 10),
            font=('Segoe UI', 11, 'bold')
        )
        style.map("Stop.TButton",
            background=[('active', '#C0392B'), ('pressed', '#A93226')]
        )

    def _build_ui(self):
        """Build the main UI components"""
        # Main container
        main_frame = tk.Frame(self.root, bg=Theme.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Header
        self._build_header(main_frame)

        # Control buttons
        self._build_controls(main_frame)

        # Chat/equation area
        self._build_chat_area(main_frame)

        # Input area
        self._build_input_area(main_frame)

        # Status bar
        self._build_status_bar(main_frame)

    def _build_header(self, parent):
        """Build the header section with logo"""
        header_frame = tk.Frame(parent, bg=Theme.BG_DARK)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        # Title frame with gradient-like appearance
        title_frame = tk.Frame(header_frame, bg=Theme.BG_LIGHT, bd=0)
        title_frame.pack(fill=tk.X)

        # Gold accent bar at top
        accent = tk.Frame(title_frame, bg=Theme.GOLD_MAIN, height=4)
        accent.pack(fill=tk.X, side=tk.TOP)

        # Content area with logo and title
        content_frame = tk.Frame(title_frame, bg=Theme.BG_LIGHT)
        content_frame.pack(fill=tk.X, padx=15, pady=10)

        # Load and display logo on the left
        self._load_header_logo(content_frame)

        # Title and subtitle on the right of logo
        text_frame = tk.Frame(content_frame, bg=Theme.BG_LIGHT)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))

        title_label = tk.Label(
            text_frame,
            text="Symbo Math",
            font=('Segoe UI', 28, 'bold'),
            fg=Theme.GOLD_LIGHT,
            bg=Theme.BG_LIGHT
        )
        title_label.pack(anchor=tk.W)

        subtitle = tk.Label(
            text_frame,
            text="Mathematical Discovery Engine",
            font=('Segoe UI', 11),
            fg=Theme.TEAL_GLOW,
            bg=Theme.BG_LIGHT
        )
        subtitle.pack(anchor=tk.W, pady=(2, 0))

        # Mathematical symbols decoration
        symbols = tk.Label(
            text_frame,
            text="π  Σ  ∫  ∞",
            font=('Segoe UI', 10),
            fg=Theme.TEAL_LIGHT,
            bg=Theme.BG_LIGHT
        )
        symbols.pack(anchor=tk.W, pady=(5, 0))

        # Teal accent bar at bottom
        accent2 = tk.Frame(title_frame, bg=Theme.TEAL_MAIN, height=3)
        accent2.pack(fill=tk.X, side=tk.BOTTOM)

    def _load_header_logo(self, parent):
        """Load and display the logo in the header"""
        logo_container = tk.Frame(parent, bg=Theme.BG_LIGHT)
        logo_container.pack(side=tk.LEFT, padx=(0, 10))

        try:
            if HAS_PIL and self.logo_path.exists():
                # Load and resize logo for header (64x64)
                logo_img = Image.open(self.logo_path)
                logo_img = logo_img.resize((72, 72), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(logo_img)

                logo_label = tk.Label(
                    logo_container,
                    image=self.logo_image,
                    bg=Theme.BG_LIGHT
                )
                logo_label.pack()
            else:
                # Fallback: Display stylized text logo
                self._create_text_logo(logo_container)
        except Exception:
            # Fallback on any error
            self._create_text_logo(logo_container)

    def _create_text_logo(self, parent):
        """Create a text-based logo as fallback"""
        logo_frame = tk.Frame(parent, bg=Theme.GOLD_DARK, bd=2, relief=tk.RAISED)
        logo_frame.pack()

        # Crown-like top
        crown = tk.Label(
            logo_frame,
            text="♔",
            font=('Segoe UI Symbol', 20),
            fg=Theme.GOLD_LIGHT,
            bg=Theme.GOLD_DARK
        )
        crown.pack(pady=(5, 0))

        # SM initials
        initials = tk.Label(
            logo_frame,
            text="SM",
            font=('Segoe UI', 16, 'bold'),
            fg=Theme.TEAL_GLOW,
            bg=Theme.GOLD_DARK
        )
        initials.pack(pady=(0, 5), padx=10)

    def _build_controls(self, parent):
        """Build the control buttons"""
        control_frame = tk.Frame(parent, bg=Theme.BG_DARK)
        control_frame.pack(fill=tk.X, pady=(0, 15))

        # Button container with border
        btn_container = tk.Frame(
            control_frame,
            bg=Theme.BG_LIGHT,
            bd=2,
            highlightbackground=Theme.TEAL_LIGHT,
            highlightthickness=2
        )
        btn_container.pack(fill=tk.X)

        inner = tk.Frame(btn_container, bg=Theme.BG_LIGHT, padx=15, pady=15)
        inner.pack(fill=tk.X)

        # Start button
        self.start_btn = ttk.Button(
            inner,
            text="▶ START",
            style="Teal.TButton",
            command=self._on_start
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Stop button
        self.stop_btn = ttk.Button(
            inner,
            text="■ STOP",
            style="Stop.TButton",
            command=self._on_stop,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Save button
        self.save_btn = ttk.Button(
            inner,
            text="💾 SAVE",
            style="Gold.TButton",
            command=self._on_save
        )
        self.save_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Imagination button (autonomous exploration)
        if HAS_IMAGINATION:
            self.imagine_btn = ttk.Button(
                inner,
                text="💡 IMAGINE",
                style="Teal.TButton",
                command=self._on_imagination,
                state=tk.DISABLED
            )
            self.imagine_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Status indicator
        self.status_indicator = tk.Label(
            inner,
            text="● STOPPED",
            font=('Segoe UI', 11, 'bold'),
            fg=Theme.TEXT_DIM,
            bg=Theme.BG_LIGHT
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=10)

        # File watcher indicator
        self.watcher_label = tk.Label(
            inner,
            text=f"📁 Watching: {self.watch_file.name}",
            font=('Segoe UI', 9),
            fg=Theme.TEAL_LIGHT,
            bg=Theme.BG_LIGHT
        )
        self.watcher_label.pack(side=tk.RIGHT, padx=10)

    def _build_chat_area(self, parent):
        """Build the equation input/output display area"""
        chat_frame = tk.Frame(
            parent,
            bg=Theme.BG_LIGHT,
            bd=2,
            highlightbackground=Theme.TEAL_MAIN,
            highlightthickness=2
        )
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Orange top border
        top_border = tk.Frame(chat_frame, bg=Theme.ORANGE_MAIN, height=3)
        top_border.pack(fill=tk.X, side=tk.TOP)

        # Label
        label_frame = tk.Frame(chat_frame, bg=Theme.BG_LIGHT)
        label_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(
            label_frame,
            text="Equations & Solutions",
            font=('Segoe UI', 12, 'bold'),
            fg=Theme.TEAL_LIGHT,
            bg=Theme.BG_LIGHT
        ).pack(side=tk.LEFT)

        # Clear button
        clear_btn = tk.Button(
            label_frame,
            text="Clear",
            font=('Segoe UI', 9),
            fg=Theme.TEXT_LIGHT,
            bg=Theme.TEAL_DARK,
            activebackground=Theme.TEAL_MAIN,
            activeforeground=Theme.TEXT_LIGHT,
            bd=0,
            padx=10,
            pady=2,
            cursor="hand2",
            command=self._clear_chat
        )
        clear_btn.pack(side=tk.RIGHT)

        # Chat display (read-only but copyable - use NORMAL state with key blocking)
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            font=('Consolas', 11),
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_LIGHT,
            insertbackground=Theme.BG_DARK,  # Hide cursor (same as background)
            selectbackground=Theme.TEAL_MAIN,
            selectforeground=Theme.TEXT_LIGHT,
            wrap=tk.WORD,
            state=tk.NORMAL,  # Keep NORMAL for selection, block keys instead
            padx=15,
            pady=15,
            bd=0,
            highlightthickness=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Make read-only by blocking all key input except copy/select shortcuts
        self.chat_display.bind('<Key>', self._block_chat_edit)
        self.chat_display.bind('<Control-c>', self._copy_selection)
        self.chat_display.bind('<Control-C>', self._copy_selection)
        self.chat_display.bind('<Control-a>', self._select_all_chat)
        self.chat_display.bind('<Control-A>', self._select_all_chat)

        # Right-click context menu for chat display
        self.chat_context_menu = tk.Menu(self.chat_display, tearoff=0)
        self.chat_context_menu.add_command(label="Copy", command=self._copy_selection)
        self.chat_context_menu.add_command(label="Select All", command=self._select_all_chat)
        self.chat_display.bind('<Button-3>', self._show_chat_context_menu)

        # Configure tags for styling - using logo colors
        self.chat_display.tag_configure("input", foreground=Theme.GOLD_LIGHT)
        self.chat_display.tag_configure("output", foreground=Theme.TEAL_GLOW)
        self.chat_display.tag_configure("error", foreground=Theme.ERROR)
        self.chat_display.tag_configure("info", foreground=Theme.TEXT_DIM)
        self.chat_display.tag_configure("success", foreground=Theme.EMERALD_LIGHT)

    def _build_input_area(self, parent):
        """Build the equation input area"""
        input_frame = tk.Frame(
            parent,
            bg=Theme.BG_LIGHT,
            bd=2,
            highlightbackground=Theme.GOLD_MAIN,
            highlightthickness=2
        )
        input_frame.pack(fill=tk.X, pady=(0, 15))

        inner = tk.Frame(input_frame, bg=Theme.BG_LIGHT, padx=10, pady=10)
        inner.pack(fill=tk.X)

        # Label
        tk.Label(
            inner,
            text="Enter Equation:",
            font=('Segoe UI', 10, 'bold'),
            fg=Theme.GOLD_LIGHT,
            bg=Theme.BG_LIGHT
        ).pack(anchor=tk.W, pady=(0, 5))

        # Input row
        input_row = tk.Frame(inner, bg=Theme.BG_LIGHT)
        input_row.pack(fill=tk.X)

        # Entry field
        self.equation_entry = tk.Entry(
            input_row,
            font=('Consolas', 12),
            bg=Theme.BG_DARK,
            fg=Theme.TEXT_LIGHT,
            insertbackground=Theme.GOLD_LIGHT,
            selectbackground=Theme.TEAL_MAIN,
            selectforeground=Theme.TEXT_LIGHT,
            bd=0,
            highlightbackground=Theme.TEAL_MAIN,
            highlightthickness=1,
            highlightcolor=Theme.GOLD_MAIN
        )
        self.equation_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        self.equation_entry.bind('<Return>', self._on_submit)
        self.equation_entry.bind('<FocusIn>', self._on_entry_focus)

        # Right-click context menu for input entry (copy/paste/cut)
        self.entry_context_menu = tk.Menu(self.equation_entry, tearoff=0)
        self.entry_context_menu.add_command(label="Cut", command=self._cut_entry)
        self.entry_context_menu.add_command(label="Copy", command=self._copy_entry)
        self.entry_context_menu.add_command(label="Paste", command=self._paste_entry)
        self.entry_context_menu.add_separator()
        self.entry_context_menu.add_command(label="Select All", command=self._select_all_entry)
        self.equation_entry.bind('<Button-3>', self._show_entry_context_menu)

        # Solve button
        solve_btn = tk.Button(
            input_row,
            text="SOLVE",
            font=('Segoe UI', 11, 'bold'),
            fg=Theme.TEXT_LIGHT,
            bg=Theme.TEAL_MAIN,
            activebackground=Theme.TEAL_DARK,
            activeforeground=Theme.TEXT_LIGHT,
            bd=0,
            padx=25,
            pady=8,
            cursor="hand2",
            command=self._on_submit
        )
        solve_btn.pack(side=tk.RIGHT)

        # Examples
        examples_frame = tk.Frame(inner, bg=Theme.BG_LIGHT)
        examples_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            examples_frame,
            text="Examples: ",
            font=('Segoe UI', 9),
            fg=Theme.TEXT_DIM,
            bg=Theme.BG_LIGHT
        ).pack(side=tk.LEFT)

        examples = ["x^2 + 2*x - 3 = 0", "diff(sin(x)*x^2, x)", "integrate(x^2, x)"]
        for ex in examples:
            btn = tk.Button(
                examples_frame,
                text=ex,
                font=('Consolas', 8),
                fg=Theme.TEAL_LIGHT,
                bg=Theme.BG_DARK,
                activebackground=Theme.TEAL_DARK,
                activeforeground=Theme.TEXT_LIGHT,
                bd=0,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda e=ex: self._insert_example(e)
            )
            btn.pack(side=tk.LEFT, padx=3)

    def _build_status_bar(self, parent):
        """Build the status bar"""
        status_frame = tk.Frame(
            parent,
            bg=Theme.BG_LIGHT,
            height=30
        )
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        # Gold accent
        tk.Frame(status_frame, bg=Theme.GOLD_MAIN, width=4).pack(side=tk.LEFT, fill=tk.Y)

        self.status_label = tk.Label(
            status_frame,
            text="Ready - Enter an equation or click START to begin",
            font=('Segoe UI', 9),
            fg=Theme.TEXT_LIGHT,
            bg=Theme.BG_LIGHT,
            padx=10
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.Y)

        # Problem count
        self.count_label = tk.Label(
            status_frame,
            text="Problems: 0",
            font=('Segoe UI', 9),
            fg=Theme.TEAL_GLOW,
            bg=Theme.BG_LIGHT,
            padx=10
        )
        self.count_label.pack(side=tk.RIGHT)

    def _start_queue_processor(self):
        """Start processing messages from the queue"""
        def process():
            try:
                while True:
                    msg = self.message_queue.get_nowait()
                    msg_type = msg.get('type', 'info')
                    text = msg.get('text', '')
                    self._append_to_chat(text, msg_type)
            except Empty:
                pass
            self.root.after(100, process)
        self.root.after(100, process)

    def _append_to_chat(self, text: str, tag: str = "info"):
        """Append text to the chat display"""
        # Widget is always NORMAL now (read-only via key blocking)
        self.chat_display.insert(tk.END, text + "\n", tag)
        self.chat_display.see(tk.END)

    def _clear_chat(self):
        """Clear the chat display"""
        # Widget is always NORMAL now (read-only via key blocking)
        self.chat_display.delete(1.0, tk.END)

    # =========================================================================
    # Copy/Paste/Select helpers for chat display and entry field
    # =========================================================================

    def _block_chat_edit(self, event=None):
        """Block all editing in chat display (makes it read-only)"""
        # Allow navigation keys
        allowed_keys = ['Left', 'Right', 'Up', 'Down', 'Home', 'End',
                        'Prior', 'Next', 'Shift_L', 'Shift_R',
                        'Control_L', 'Control_R', 'Alt_L', 'Alt_R']
        if event and event.keysym in allowed_keys:
            return  # Allow these keys
        return "break"  # Block everything else

    def _copy_selection(self, event=None):
        """Copy selected text from chat display to clipboard"""
        try:
            selected = self.chat_display.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except tk.TclError:
            pass  # No selection
        except Exception:
            pass
        return "break"

    def _select_all_chat(self, event=None):
        """Select all text in chat display"""
        self.chat_display.tag_add(tk.SEL, "1.0", tk.END)
        return "break"

    def _show_chat_context_menu(self, event):
        """Show context menu for chat display"""
        try:
            self.chat_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.chat_context_menu.grab_release()

    def _cut_entry(self, event=None):
        """Cut selected text from entry field"""
        try:
            self.equation_entry.event_generate('<<Cut>>')
        except Exception:
            pass

    def _copy_entry(self, event=None):
        """Copy selected text from entry field"""
        try:
            self.equation_entry.event_generate('<<Copy>>')
        except Exception:
            pass

    def _paste_entry(self, event=None):
        """Paste text into entry field"""
        try:
            self.equation_entry.event_generate('<<Paste>>')
        except Exception:
            pass

    def _select_all_entry(self, event=None):
        """Select all text in entry field"""
        self.equation_entry.select_range(0, tk.END)
        self.equation_entry.icursor(tk.END)

    def _show_entry_context_menu(self, event):
        """Show context menu for entry field"""
        try:
            self.entry_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.entry_context_menu.grab_release()

    def _on_entry_focus(self, event=None):
        """Handle entry field getting focus - clear chat selection to prevent accidental inserts"""
        try:
            # Clear any selection in the chat display
            self.chat_display.tag_remove(tk.SEL, "1.0", tk.END)
        except Exception:
            pass

    # =========================================================================

    def _insert_example(self, example: str):
        """Insert an example into the entry field"""
        self.equation_entry.delete(0, tk.END)
        self.equation_entry.insert(0, example)
        self.equation_entry.focus()

    def _update_status(self, text: str):
        """Update the status bar"""
        self.status_label.config(text=text)

    def _update_count(self):
        """Update the problem count"""
        self.count_label.config(text=f"Problems: {len(self.results)}")

    def _on_start(self):
        """Handle start button click"""
        if self.is_running:
            return

        self._update_status("Starting solver engine...")
        self._append_to_chat("═" * 50, "info")
        self._append_to_chat("Starting Symbo Math...", "info")

        # Initialize in background thread
        def init():
            try:
                self.coordinator = get_coordinator()
                self.solver = get_solver_engine(self.coordinator)

                # Create watch file if it doesn't exist
                self.watch_file.parent.mkdir(parents=True, exist_ok=True)
                if not self.watch_file.exists():
                    with open(self.watch_file, 'w') as f:
                        f.write("# Add math problems here (one per line)\n")
                        f.write("# Lines starting with # are ignored\n")
                        f.write("# The solver will automatically process new problems\n\n")

                # Start file watcher
                self.file_watcher = FileWatcher(
                    str(self.watch_file),
                    self._on_file_problem
                )
                self.file_watcher.start()

                self.is_running = True
                self.root.after(0, self._on_start_complete)
            except Exception as e:
                self.root.after(0, lambda: self._on_start_error(str(e)))

        threading.Thread(target=init, daemon=True).start()

    def _on_start_complete(self):
        """Called when start completes successfully"""
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        if HAS_IMAGINATION and hasattr(self, 'imagine_btn'):
            self.imagine_btn.config(state=tk.NORMAL)
        self.status_indicator.config(text="● RUNNING", fg=Theme.SUCCESS)
        self._update_status("Solver running - Enter equations or add to watch file")
        self._append_to_chat("✓ Solver engine initialized", "success")
        self._append_to_chat(f"✓ Watching file: {self.watch_file}", "success")
        if HAS_IMAGINATION:
            self._append_to_chat("✓ Imagination mode available (click 💡 IMAGINE)", "success")
        self._append_to_chat("═" * 50, "info")

    def _on_start_error(self, error: str):
        """Called when start fails"""
        self._update_status(f"Error: {error}")
        self._append_to_chat(f"✗ Failed to start: {error}", "error")

    def _on_stop(self):
        """Handle stop button click"""
        if not self.is_running:
            return

        self._update_status("Stopping solver...")

        def stop():
            try:
                # Stop imagination engine first if running
                if self.is_imagining and self.imagination_engine:
                    self.imagination_engine.stop()
                    self.imagination_engine = None
                    self.is_imagining = False

                if self.file_watcher:
                    self.file_watcher.stop()
                    self.file_watcher = None

                if self.coordinator:
                    shutdown_coordinator()
                    self.coordinator = None
                    self.solver = None

                self.is_running = False
                self.root.after(0, self._on_stop_complete)
            except Exception as e:
                self.root.after(0, lambda: self._append_to_chat(f"Stop error: {e}", "error"))

        threading.Thread(target=stop, daemon=True).start()

    def _on_stop_complete(self):
        """Called when stop completes"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        if HAS_IMAGINATION and hasattr(self, 'imagine_btn'):
            self.imagine_btn.config(state=tk.DISABLED)
        self.status_indicator.config(text="● STOPPED", fg=Theme.TEXT_DIM)
        self._update_status("Solver stopped")
        self._append_to_chat("═" * 50, "info")
        self._append_to_chat("Solver stopped", "info")

    def _on_imagination(self):
        """Handle imagination button click - toggle autonomous exploration"""
        if not HAS_IMAGINATION:
            self._append_to_chat("Imagination engine not available", "error")
            return

        if not self.is_running or not self.solver:
            self._append_to_chat("Start solver first before using imagination", "error")
            return

        if self.is_imagining:
            # Stop imagination
            self._stop_imagination()
        else:
            # Start imagination
            self._start_imagination()

    def _start_imagination(self):
        """Start autonomous mathematical exploration"""
        self._append_to_chat("═" * 50, "info")
        self._append_to_chat("💡 Starting Imagination Engine...", "info")
        self._append_to_chat("   SYMBO will autonomously explore mathematics", "info")

        def init_imagination():
            try:
                # Create imagination engine with discovery callback
                self.imagination_engine = ImaginationEngine(
                    self.solver,
                    idle_threshold=2.0,
                    exploration_interval=1.0,
                    max_exploration_time=10.0,
                    on_discovery=self._on_discovery
                )
                self.imagination_engine.start()
                self.is_imagining = True
                self.root.after(0, self._on_imagination_started)

            except Exception as e:
                self.root.after(0, lambda: self._append_to_chat(f"✗ Imagination error: {e}", "error"))

        threading.Thread(target=init_imagination, daemon=True).start()

    def _on_imagination_started(self):
        """Called when imagination engine starts"""
        self.imagine_btn.config(text="🛑 STOP IMAGINE", style="Stop.TButton")
        self.status_indicator.config(text="● IMAGINING", fg=Theme.TEAL_GLOW)
        self._update_status("Imagination active - SYMBO is exploring mathematics autonomously")
        self._append_to_chat("✓ Imagination engine active!", "success")
        self._append_to_chat("   Watch for discoveries below...", "info")
        self._append_to_chat("═" * 50, "info")

    def _stop_imagination(self):
        """Stop autonomous exploration"""
        if self.imagination_engine:
            self.imagination_engine.stop()

            # Show final stats
            stats = self.imagination_engine.get_statistics()
            img_stats = stats.get('imagination', {})
            total = img_stats.get('total_explorations', 0)
            discoveries = img_stats.get('interesting_discoveries', 0)

            self._append_to_chat("═" * 50, "info")
            self._append_to_chat("💡 Imagination session complete!", "info")
            self._append_to_chat(f"   Explorations: {total}", "info")
            self._append_to_chat(f"   Interesting discoveries: {discoveries}", "success" if discoveries > 0 else "info")

            # Show best discoveries
            best = self.imagination_engine.get_best_discoveries(3)
            if best:
                self._append_to_chat("   Best finds:", "info")
                for d in best:
                    self._append_to_chat(f"     • {d.problem[:50]}...", "output")
                    self._append_to_chat(f"       → {str(d.solution)[:50]}", "success")

            self._append_to_chat("═" * 50, "info")

            self.imagination_engine = None

        self.is_imagining = False
        self.imagine_btn.config(text="💡 IMAGINE", style="Teal.TButton")
        self.status_indicator.config(text="● RUNNING", fg=Theme.SUCCESS)
        self._update_status("Solver running - Enter equations or add to watch file")

    def _on_discovery(self, result: 'ExplorationResult'):
        """Callback when imagination finds something interesting"""
        # Queue for thread-safe UI update
        interest_name = result.interest_level.name if hasattr(result.interest_level, 'name') else str(result.interest_level)
        self.message_queue.put({
            'type': 'output',
            'text': f"💡 [{interest_name}] {result.problem[:60]}"
        })
        self.message_queue.put({
            'type': 'success',
            'text': f"   → {str(result.solution)[:60]}"
        })
        if result.notes:
            self.message_queue.put({
                'type': 'info',
                'text': f"   Note: {result.notes}"
            })

    def _on_save(self):
        """Handle save button click"""
        if not self.results:
            messagebox.showinfo("Save", "No results to save yet.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"math_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(self.results, f, indent=2, default=str)
                self._append_to_chat(f"✓ Saved {len(self.results)} results to {filepath}", "success")
                self._update_status(f"Results saved to {filepath}")
            except Exception as e:
                self._append_to_chat(f"✗ Save failed: {e}", "error")

    def _on_submit(self, event=None):
        """Handle equation submission"""
        equation = self.equation_entry.get().strip()
        if not equation:
            return

        self.equation_entry.delete(0, tk.END)
        self._solve_equation(equation)

    def _on_file_problem(self, problem: str):
        """Handle problem from watched file"""
        self.message_queue.put({
            'type': 'info',
            'text': f"[FILE] New problem detected: {problem}"
        })
        self._solve_equation(problem, from_file=True)

    def _solve_equation(self, equation: str, from_file: bool = False):
        """Solve an equation"""
        source = "[FILE] " if from_file else "[INPUT] "
        self._append_to_chat(f"{source}{equation}", "input")

        if not self.is_running or not self.solver:
            self._append_to_chat("  → Solver not running. Click START first.", "error")
            return

        self._update_status(f"Solving: {equation[:50]}...")

        def solve():
            try:
                result = self.solver.solve(equation)

                # Store result
                result_data = {
                    'timestamp': datetime.now().isoformat(),
                    'equation': equation,
                    'from_file': from_file,
                    'status': result.status.value if hasattr(result.status, 'value') else str(result.status),
                    'solution': str(result.result) if result.result else None,
                    'method': result.specialist_used
                }
                self.results.append(result_data)

                # Format output
                if result.status == SolveStatus.SUCCESS:
                    output = f"  → Solution: {result.result}"
                    tag = "output"
                elif result.status == SolveStatus.PARTIAL:
                    output = f"  → Partial: {result.result}"
                    tag = "output"
                else:
                    output = f"  → Could not solve: {result.error or 'Unknown error'}"
                    tag = "error"

                self.message_queue.put({'type': tag, 'text': output})
                if result.specialist_used:
                    self.message_queue.put({'type': 'info', 'text': f"  → Method: {result.specialist_used}"})

                self.root.after(0, lambda: self._update_status("Ready"))
                self.root.after(0, self._update_count)

            except Exception as e:
                self.message_queue.put({'type': 'error', 'text': f"  → Error: {str(e)}"})
                self.root.after(0, lambda: self._update_status("Ready"))

        threading.Thread(target=solve, daemon=True).start()

    def run(self):
        """Run the application"""
        # Welcome message
        self._append_to_chat("═" * 50, "info")
        self._append_to_chat("Welcome to Symbo Math", "info")
        self._append_to_chat("Mathematical Discovery Engine", "info")
        self._append_to_chat("", "info")
        self._append_to_chat("1. Click START to initialize the solver", "info")
        self._append_to_chat("2. Enter equations in the input box", "info")
        self._append_to_chat("3. Or add problems to the watch file:", "info")
        self._append_to_chat(f"   {self.watch_file}", "info")
        self._append_to_chat("═" * 50, "info")

        # Handle window close
        def on_close():
            if self.is_running:
                if messagebox.askyesno("Quit", "Solver is running. Stop and quit?"):
                    self._on_stop()
                    self.root.after(500, self.root.destroy)
            else:
                self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_close)
        self.root.mainloop()


# =============================================================================
# MAIN
# =============================================================================
def main():
    """Main entry point"""
    app = MathSolverUI()
    app.run()


if __name__ == "__main__":
    main()
