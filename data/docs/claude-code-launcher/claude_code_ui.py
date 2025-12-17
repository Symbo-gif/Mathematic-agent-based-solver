"""
Claude Code Symbo Math UI
A desktop interface for Claude Code with Symbo Math project context.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, font as tkfont
import subprocess
import threading
import queue
import os
import sys
from pathlib import Path

# Try to import PIL for image loading
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Project paths
PROJECT_DIR = Path(r"c:\dev\Mathematic agent based solver")
LAUNCHER_DIR = PROJECT_DIR / "claude-code-launcher"
CONTEXT_FILE = LAUNCHER_DIR / "PROJECT_CONTEXT.md"

# Logo paths
SYMBO_LOGO_PATH = PROJECT_DIR / "Symbo Math Logo.png"
CLAUDE_GOLD_LOGO_PATH = PROJECT_DIR / "claude_code_gold.png"

# Symbo Math Color Scheme
class Theme:
    # Primary - Gold
    GOLD_DARK = "#B8860B"
    GOLD_MAIN = "#DAA520"
    GOLD_LIGHT = "#FFD700"

    # Secondary - Teal
    TEAL_DARK = "#006D77"
    TEAL_MAIN = "#008B8B"
    TEAL_LIGHT = "#40E0D0"

    # Accent - Emerald
    EMERALD = "#2ECC71"

    # Backgrounds (Claude-like dark theme)
    BG_DARKEST = "#0D1117"
    BG_DARK = "#161B22"
    BG_MAIN = "#1C2128"
    BG_LIGHT = "#21262D"
    BG_LIGHTER = "#30363D"

    # Text
    TEXT_PRIMARY = "#E6EDF3"
    TEXT_SECONDARY = "#8B949E"
    TEXT_MUTED = "#6E7681"

    # Borders
    BORDER = "#30363D"
    BORDER_LIGHT = "#3D444D"

    # Status
    SUCCESS = "#2ECC71"
    ERROR = "#FF6B6B"
    WARNING = "#FFD93D"


class ClaudeSparkleIcon(tk.Canvas):
    """Draw the Claude sparkle logo in teal on gold"""
    def __init__(self, parent, size=40, **kwargs):
        super().__init__(parent, width=size, height=size,
                        bg=Theme.BG_DARK, highlightthickness=0, **kwargs)
        self.size = size
        self.draw_icon()

    def draw_icon(self):
        s = self.size
        padding = s * 0.1

        # Gold rounded background
        self.create_oval(padding, padding, s - padding, s - padding,
                        fill=Theme.GOLD_MAIN, outline=Theme.GOLD_LIGHT, width=1)

        # Teal sparkle shape (4-pointed star)
        cx, cy = s / 2, s / 2
        outer = s * 0.35
        inner = s * 0.1

        import math
        points = []
        for i in range(8):
            angle = (i * math.pi / 4) - math.pi / 2
            r = outer if i % 2 == 0 else inner
            points.extend([cx + r * math.cos(angle), cy + r * math.sin(angle)])

        self.create_polygon(points, fill=Theme.TEAL_MAIN, outline=Theme.TEAL_DARK, width=1)


class SymboMathLogo(tk.Canvas):
    """Draw the Symbo Math sigma logo"""
    def __init__(self, parent, size=40, **kwargs):
        super().__init__(parent, width=size, height=size,
                        bg=Theme.BG_DARK, highlightthickness=0, **kwargs)
        self.size = size
        self.draw_logo()

    def draw_logo(self):
        s = self.size
        padding = s * 0.1

        # Dark circular background with teal border
        self.create_oval(padding, padding, s - padding, s - padding,
                        fill=Theme.BG_DARKEST, outline=Theme.TEAL_LIGHT, width=2)

        # Sigma shape
        margin = s * 0.25
        top = margin
        bottom = s - margin
        left = margin
        right = s - margin
        mid = s / 2
        lw = max(2, s // 16)

        # Top horizontal (gold)
        self.create_line(left, top, right, top, fill=Theme.GOLD_MAIN, width=lw)
        # Diagonal to center (teal)
        self.create_line(left, top, mid, mid, fill=Theme.TEAL_LIGHT, width=lw)
        # Diagonal to bottom (teal)
        self.create_line(mid, mid, left, bottom, fill=Theme.TEAL_LIGHT, width=lw)
        # Bottom horizontal (gold)
        self.create_line(left, bottom, right, bottom, fill=Theme.GOLD_MAIN, width=lw)

        # Center dot (emerald)
        dot_r = s * 0.06
        self.create_oval(mid - dot_r, mid - dot_r, mid + dot_r, mid + dot_r,
                        fill=Theme.EMERALD, outline="")


class MessageBubble(tk.Frame):
    """A styled message bubble for chat display"""
    def __init__(self, parent, message, is_user=True, **kwargs):
        super().__init__(parent, bg=Theme.BG_MAIN, **kwargs)

        bubble_bg = Theme.BG_LIGHTER if is_user else Theme.BG_LIGHT
        text_color = Theme.TEXT_PRIMARY
        align = "e" if is_user else "w"

        # Container for alignment
        container = tk.Frame(self, bg=Theme.BG_MAIN)
        container.pack(fill="x", padx=10, pady=5)

        # Role label
        role = "You" if is_user else "Claude"
        role_color = Theme.GOLD_MAIN if is_user else Theme.TEAL_LIGHT

        role_label = tk.Label(container, text=role, bg=Theme.BG_MAIN,
                             fg=role_color, font=("Segoe UI", 9, "bold"))
        role_label.pack(anchor=align, padx=5)

        # Message bubble
        bubble = tk.Frame(container, bg=bubble_bg, padx=12, pady=8)
        bubble.pack(anchor=align, padx=5)

        # Message text
        msg_label = tk.Label(bubble, text=message, bg=bubble_bg, fg=text_color,
                            font=("Segoe UI", 10), wraplength=500, justify="left")
        msg_label.pack()


class ClaudeCodeUI(tk.Tk):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.title("Claude Code - Symbo Math")
        self.geometry("900x700")
        self.minsize(700, 500)
        self.configure(bg=Theme.BG_DARK)

        # Set window icon
        icon_path = LAUNCHER_DIR / "symbo_math_icon.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))

        # Message queue for thread-safe updates
        self.msg_queue = queue.Queue()
        self.claude_process = None
        self.is_processing = False

        self.setup_ui()
        self.load_context()
        self.process_queue()

    def setup_ui(self):
        """Build the UI components"""

        # Header bar
        self.create_header()

        # Main content area
        self.create_chat_area()

        # Input area
        self.create_input_area()

        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Create the header with logos and title"""
        header = tk.Frame(self, bg=Theme.BG_DARKEST, height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Left side - Symbo Math logo and title
        left_frame = tk.Frame(header, bg=Theme.BG_DARKEST)
        left_frame.pack(side="left", padx=15, pady=10)

        # Load Symbo Math logo from file
        if HAS_PIL and SYMBO_LOGO_PATH.exists():
            try:
                img = Image.open(SYMBO_LOGO_PATH)
                img = img.resize((40, 40), Image.Resampling.LANCZOS)
                self.symbo_logo_img = ImageTk.PhotoImage(img)
                symbo_logo = tk.Label(left_frame, image=self.symbo_logo_img, bg=Theme.BG_DARKEST)
                symbo_logo.pack(side="left", padx=(0, 10))
            except Exception:
                symbo_logo = SymboMathLogo(left_frame, size=40)
                symbo_logo.pack(side="left", padx=(0, 10))
        else:
            symbo_logo = SymboMathLogo(left_frame, size=40)
            symbo_logo.pack(side="left", padx=(0, 10))

        title_frame = tk.Frame(left_frame, bg=Theme.BG_DARKEST)
        title_frame.pack(side="left")

        title = tk.Label(title_frame, text="Symbo Math", bg=Theme.BG_DARKEST,
                        fg=Theme.GOLD_MAIN, font=("Segoe UI", 14, "bold"))
        title.pack(anchor="w")

        subtitle = tk.Label(title_frame, text="Claude Code Interface", bg=Theme.BG_DARKEST,
                           fg=Theme.TEXT_SECONDARY, font=("Segoe UI", 9))
        subtitle.pack(anchor="w")

        # Right side - Gold Claude sparkle logo
        right_frame = tk.Frame(header, bg=Theme.BG_DARKEST)
        right_frame.pack(side="right", padx=15, pady=10)

        # Load gold Claude logo from file
        if HAS_PIL and CLAUDE_GOLD_LOGO_PATH.exists():
            try:
                img = Image.open(CLAUDE_GOLD_LOGO_PATH)
                img = img.resize((40, 40), Image.Resampling.LANCZOS)
                self.claude_logo_img = ImageTk.PhotoImage(img)
                claude_logo = tk.Label(right_frame, image=self.claude_logo_img, bg=Theme.BG_DARKEST)
                claude_logo.pack(side="right")
            except Exception:
                claude_logo = ClaudeSparkleIcon(right_frame, size=40)
                claude_logo.pack(side="right")
        else:
            claude_logo = ClaudeSparkleIcon(right_frame, size=40)
            claude_logo.pack(side="right")

        # Divider line
        divider = tk.Frame(self, bg=Theme.TEAL_DARK, height=2)
        divider.pack(fill="x")

    def create_chat_area(self):
        """Create the scrollable chat display area"""
        # Container
        chat_container = tk.Frame(self, bg=Theme.BG_MAIN)
        chat_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Canvas with scrollbar for messages
        self.chat_canvas = tk.Canvas(chat_container, bg=Theme.BG_MAIN,
                                     highlightthickness=0)
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical",
                                  command=self.chat_canvas.yview)

        self.chat_frame = tk.Frame(self.chat_canvas, bg=Theme.BG_MAIN)

        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.chat_canvas.pack(side="left", fill="both", expand=True)

        self.chat_window = self.chat_canvas.create_window(
            (0, 0), window=self.chat_frame, anchor="nw"
        )

        # Configure scrolling
        self.chat_frame.bind("<Configure>", self.on_frame_configure)
        self.chat_canvas.bind("<Configure>", self.on_canvas_configure)

        # Mouse wheel scrolling
        self.chat_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Style the scrollbar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar",
                       background=Theme.BG_LIGHTER,
                       troughcolor=Theme.BG_DARK,
                       bordercolor=Theme.BG_DARK,
                       arrowcolor=Theme.TEXT_SECONDARY)

    def create_input_area(self):
        """Create the message input area"""
        # Divider
        divider = tk.Frame(self, bg=Theme.BORDER, height=1)
        divider.pack(fill="x")

        # Input container
        input_container = tk.Frame(self, bg=Theme.BG_DARK, pady=15)
        input_container.pack(fill="x", side="bottom")

        # Inner frame for centering
        inner = tk.Frame(input_container, bg=Theme.BG_DARK)
        inner.pack(fill="x", padx=20)

        # Text input with border
        input_border = tk.Frame(inner, bg=Theme.BORDER_LIGHT, padx=2, pady=2)
        input_border.pack(fill="x", side="left", expand=True)

        self.input_text = tk.Text(input_border, height=3, bg=Theme.BG_LIGHT,
                                  fg=Theme.TEXT_PRIMARY, font=("Segoe UI", 11),
                                  insertbackground=Theme.GOLD_MAIN,
                                  selectbackground=Theme.TEAL_DARK,
                                  relief="flat", padx=10, pady=8, wrap="word")
        self.input_text.pack(fill="both", expand=True)
        self.input_text.bind("<Return>", self.on_enter_key)
        self.input_text.bind("<Shift-Return>", lambda e: None)  # Allow shift+enter for newlines

        # Send button
        self.send_btn = tk.Button(inner, text="Send", bg=Theme.TEAL_MAIN,
                                  fg=Theme.TEXT_PRIMARY, font=("Segoe UI", 10, "bold"),
                                  relief="flat", padx=20, pady=10, cursor="hand2",
                                  activebackground=Theme.TEAL_LIGHT,
                                  command=self.send_message)
        self.send_btn.pack(side="right", padx=(10, 0))

        # Placeholder text
        self.input_text.insert("1.0", "Ask Claude about the Symbo Math project...")
        self.input_text.config(fg=Theme.TEXT_MUTED)
        self.input_text.bind("<FocusIn>", self.on_input_focus_in)
        self.input_text.bind("<FocusOut>", self.on_input_focus_out)

    def create_status_bar(self):
        """Create the bottom status bar"""
        status_bar = tk.Frame(self, bg=Theme.BG_DARKEST, height=25)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(status_bar, text="Ready", bg=Theme.BG_DARKEST,
                                     fg=Theme.TEXT_MUTED, font=("Segoe UI", 8))
        self.status_label.pack(side="left", padx=10)

        project_label = tk.Label(status_bar, text=str(PROJECT_DIR), bg=Theme.BG_DARKEST,
                                fg=Theme.TEXT_MUTED, font=("Segoe UI", 8))
        project_label.pack(side="right", padx=10)

    def on_frame_configure(self, event):
        """Reset scroll region when frame changes"""
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Adjust frame width to canvas width"""
        self.chat_canvas.itemconfig(self.chat_window, width=event.width)

    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_input_focus_in(self, event):
        """Clear placeholder on focus"""
        if self.input_text.get("1.0", "end-1c") == "Ask Claude about the Symbo Math project...":
            self.input_text.delete("1.0", "end")
            self.input_text.config(fg=Theme.TEXT_PRIMARY)

    def on_input_focus_out(self, event):
        """Show placeholder if empty"""
        if not self.input_text.get("1.0", "end-1c").strip():
            self.input_text.insert("1.0", "Ask Claude about the Symbo Math project...")
            self.input_text.config(fg=Theme.TEXT_MUTED)

    def on_enter_key(self, event):
        """Handle enter key press"""
        if not event.state & 0x1:  # Not shift+enter
            self.send_message()
            return "break"

    def add_message(self, message, is_user=True):
        """Add a message bubble to the chat"""
        bubble = MessageBubble(self.chat_frame, message, is_user)
        bubble.pack(fill="x", anchor="w" if not is_user else "e")

        # Scroll to bottom
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def load_context(self):
        """Load and display initial context"""
        # Welcome message
        welcome = """Welcome to Claude Code for Symbo Math!

I'm ready to help with the multi-agent mathematical discovery engine. I have context about:

- Project architecture (BDI agents, FIPA-ACL messaging)
- Recent edits (native calculus enhancements, UI updates)
- Planned next steps (zeta functions, Fresnel integrals, etc.)

What would you like to work on?"""

        self.add_message(welcome, is_user=False)

    def send_message(self):
        """Send a message to Claude Code"""
        message = self.input_text.get("1.0", "end-1c").strip()

        if not message or message == "Ask Claude about the Symbo Math project...":
            return

        if self.is_processing:
            return

        # Clear input
        self.input_text.delete("1.0", "end")

        # Add user message
        self.add_message(message, is_user=True)

        # Process with Claude Code
        self.is_processing = True
        self.status_label.config(text="Processing...", fg=Theme.GOLD_MAIN)
        self.send_btn.config(state="disabled", bg=Theme.BG_LIGHTER)

        # Run in background thread
        thread = threading.Thread(target=self.run_claude_code, args=(message,))
        thread.daemon = True
        thread.start()

    def run_claude_code(self, message):
        """Run Claude Code CLI and capture output"""
        try:
            # Prevent terminal window from appearing on Windows
            kwargs = {
                'cwd': str(PROJECT_DIR),
                'capture_output': True,
                'text': True,
                'timeout': 120,
                'encoding': 'utf-8',
                'errors': 'replace'
            }
            if sys.platform == 'win32':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

            # Run claude with the message
            result = subprocess.run(
                ["claude", "--print", message],
                **kwargs
            )

            response = result.stdout.strip() if result.stdout else ""
            if result.stderr and not response:
                response = f"Error: {result.stderr.strip()}"
            if not response:
                response = "No response received from Claude Code."

            self.msg_queue.put(("response", response))

        except subprocess.TimeoutExpired:
            self.msg_queue.put(("response", "Request timed out. Please try again."))
        except FileNotFoundError:
            self.msg_queue.put(("response", "Claude Code CLI not found. Please ensure it's installed and in PATH."))
        except Exception as e:
            self.msg_queue.put(("response", f"Error: {str(e)}"))

    def process_queue(self):
        """Process messages from background threads"""
        try:
            while True:
                msg_type, content = self.msg_queue.get_nowait()
                if msg_type == "response":
                    self.add_message(content, is_user=False)
                    self.is_processing = False
                    self.status_label.config(text="Ready", fg=Theme.TEXT_MUTED)
                    self.send_btn.config(state="normal", bg=Theme.TEAL_MAIN)
        except queue.Empty:
            pass

        # Check again after 100ms
        self.after(100, self.process_queue)


def main():
    app = ClaudeCodeUI()
    app.mainloop()


if __name__ == "__main__":
    main()
