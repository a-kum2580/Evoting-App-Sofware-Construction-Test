"""
Console UI helpers — Colors, formatting, and input utilities.

This module is the foundation of the presentation layer. It provides:
  - ANSI escape code constants for colors and text styles
  - Theme color definitions for consistent visual identity
  - Reusable display functions (headers, menus, tables, messages)
  - Secure masked password input (cross-platform: Windows + Unix)
  - Screen clearing and pause utilities

All other UI modules import from here rather than defining their
own formatting, ensuring visual consistency (DRY principle).
"""

import os
import sys

# Enable ANSI escape sequences on Windows terminal
if sys.platform == "win32":
    os.system("")

# ── ANSI Escape Codes ───────────────────────────────────────
# Text style modifiers

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Foreground colors
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
GRAY = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# Background colors
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"
BG_GRAY = "\033[100m"

# ── Theme Colors ─────────────────────────────────────────────
# Each screen type has its own color scheme for visual distinction
THEME_LOGIN = BRIGHT_CYAN          # Login / welcome screens
THEME_ADMIN = BRIGHT_GREEN         # Admin dashboard and menus
THEME_ADMIN_ACCENT = YELLOW        # Admin secondary highlights
THEME_VOTER = BRIGHT_BLUE          # Voter dashboard and menus
THEME_VOTER_ACCENT = MAGENTA       # Voter secondary highlights


# ── Display Helper Functions ─────────────────────────────────

def colored(text, color):
    """Wrap text with ANSI color codes and auto-reset at the end."""
    return f"{color}{text}{RESET}"


def header(title, theme_color):
    """Print a prominent double-line box header for major sections."""
    width = 58
    top = f"  {theme_color}{'═' * width}{RESET}"
    mid = (f"  {theme_color}{BOLD} {title.center(width - 2)} "
           f"{RESET}{theme_color} {RESET}")
    bot = f"  {theme_color}{'═' * width}{RESET}"
    print(top)
    print(mid)
    print(bot)


def subheader(title, theme_color):
    print(f"\n  {theme_color}{BOLD}▸ {title}{RESET}")


def table_header(format_str, theme_color):
    print(f"  {theme_color}{BOLD}{format_str}{RESET}")


def table_divider(width, theme_color):
    print(f"  {theme_color}{'─' * width}{RESET}")


def error(msg):
    print(f"  {RED}{BOLD} {msg}{RESET}")


def success(msg):
    print(f"  {GREEN}{BOLD} {msg}{RESET}")


def warning(msg):
    print(f"  {YELLOW}{BOLD} {msg}{RESET}")


def info(msg):
    print(f"  {GRAY}{msg}{RESET}")


def menu_item(number, text, color):
    """Print a single numbered menu entry with consistent alignment."""
    print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")


def status_badge(text, is_good):
    """Return a color-coded status label (green = good, red = bad)."""
    if is_good:
        return f"{GREEN}{text}{RESET}"
    return f"{RED}{text}{RESET}"


def prompt(text):
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()


def masked_input(prompt_text="Password: "):
    """Read a password with echo replaced by yellow asterisks.
    Handles both Windows (msvcrt) and Unix (termios/tty) terminals.
    Supports backspace for corrections and Ctrl+C to cancel."""
    print(f"  {BRIGHT_WHITE}{prompt_text}{RESET}", end="", flush=True)
    password = ""
    if sys.platform == "win32":
        import msvcrt
        while True:
            char = msvcrt.getwch()
            if char in ("\r", "\n"):
                print()
                break
            elif char in ("\x08", "\b"):
                if password:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif char == "\x03":
                raise KeyboardInterrupt
            else:
                password += char
                sys.stdout.write(f"{YELLOW}*{RESET}")
                sys.stdout.flush()
    else:
        import tty
        import termios
        file_descriptor = sys.stdin.fileno()
        old_settings = termios.tcgetattr(file_descriptor)
        try:
            tty.setraw(file_descriptor)
            while True:
                char = sys.stdin.read(1)
                if char in ("\r", "\n"):
                    print()
                    break
                elif char in ("\x7f", "\x08"):
                    if password:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif char == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += char
                    sys.stdout.write(f"{YELLOW}*{RESET}")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(
                file_descriptor, termios.TCSADRAIN, old_settings
            )
    return password


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def pause():
    input(f"\n  {DIM}Press Enter to continue...{RESET}")
