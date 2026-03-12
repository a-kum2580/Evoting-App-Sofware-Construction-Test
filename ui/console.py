"""
Console UI utilities.

Contains all ANSI colour constants and reusable display / input helpers.
Extracted verbatim from the monolith so that every header, prompt, and
status badge looks identical to the original application.
"""

import os
import sys


# ------------------------------------------------------------------
# ANSI escape sequences
# ------------------------------------------------------------------

if sys.platform == "win32":
    os.system("")

# Base styles
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Foreground colours
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

# Background colours
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"
BG_GRAY = "\033[100m"

# Theme colours (per context)
THEME_LOGIN = BRIGHT_CYAN
THEME_ADMIN = BRIGHT_GREEN
THEME_ADMIN_ACCENT = YELLOW
THEME_VOTER = BRIGHT_BLUE
THEME_VOTER_ACCENT = MAGENTA


# ------------------------------------------------------------------
# Display helpers
# ------------------------------------------------------------------

def colored(text, color):
    return f"{color}{text}{RESET}"


def header(title, theme_color):
    width = 58
    top = f"  {theme_color}{'═' * width}{RESET}"
    mid = f"  {theme_color}{BOLD} {title.center(width - 2)} {RESET}{theme_color} {RESET}"
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
    print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")


def status_badge(text, is_good):
    if is_good:
        return f"{GREEN}{text}{RESET}"
    return f"{RED}{text}{RESET}"


# ------------------------------------------------------------------
# Input helpers
# ------------------------------------------------------------------

def prompt(text):
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()


def masked_input(prompt_text="Password: "):
    """Read a password with asterisk masking (cross-platform)."""
    print(f"  {BRIGHT_WHITE}{prompt_text}{RESET}", end="", flush=True)
    password = ""

    if sys.platform == "win32":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                print()
                break
            elif ch in ("\x08", "\b"):
                if password:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                password += ch
                sys.stdout.write(f"{YELLOW}*{RESET}")
                sys.stdout.flush()
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    print()
                    break
                elif ch in ("\x7f", "\x08"):
                    if password:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += ch
                    sys.stdout.write(f"{YELLOW}*{RESET}")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return password


# ------------------------------------------------------------------
# Misc helpers
# ------------------------------------------------------------------

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def pause():
    input(f"\n  {DIM}Press Enter to continue...{RESET}")
