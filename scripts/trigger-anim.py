#!/usr/bin/env python3
"""
3AM trigger-anim — REAL terminal animation for mandate activation.

Run exactly ONCE on Turn 1 (activation) when the mandate loads. Plays frames in
the live terminal: typewriter header -> rule sweep -> boot lines with spinners ->
loading bar -> ARMED flash -> pulse equalizer -> P0 demand. ~3.5s, zero deps.

Non-TTY (logged output, injected endpoints, pipes): prints the static sequence and
exits 0 — no escape garbage.

Env:
  NO_COLOR=1   disable ANSI color
  3AM_FAST=1   shorten timings (tests / impatient operators)

Exit codes: 0 ok (animation played or static printed).
"""
import os
import sys
import time

IS_TTY = sys.stdout.isatty()
FAST = os.environ.get("3AM_FAST") == "1"
NO_COLOR = os.environ.get("NO_COLOR") == "1"

TICK = 0.05 if FAST else 0.09          # base frame tick (s)
SPIN = "|/-\\"
PULSE = "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁"


def c(s, code):
    return s if NO_COLOR else f"\x1b[{code}m{s}\x1b[0m"


CYAN, GREEN, YEL, RED, BOLD, DIM = "36;1", "32;1", "33;1", "31;1", "1", "2"

STATIC = (
    "▸ 3AM SHINJITSU — TRIGGER SEQUENCE\n"
    "  ═══════════════════════════════════\n"
    "  [ OK ] mandate core loaded\n"
    "  [ OK ] scope gate armed\n"
    "  [ OK ] velocity engine online\n"
    "  ⚡ MANDATE TRIGGERED · STATUS: ARMED\n"
    "  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁\n"
    "  ─ waiting P0: target · objective · authorization"
)

RULE = "═" * 37


def _w(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def typewriter(s, color=None, tick=None):
    for ch in s:
        _w(c(ch, color) if color else ch)
        time.sleep(tick or TICK * 0.12)


def sweep_rule():
    for i in range(1, len(RULE) + 1):
        _w("\r  " + RULE[:i])
        time.sleep(TICK * 0.06)
    _w("\n")


def boot_line(label, msg):
    """[ spinner ] label — then finalize [ OK ] green."""
    _w(f"  [ {SPIN[0]} ] {msg}")
    for tick in range(1, 10):
        _w("\r" + f"  [ {SPIN[tick % 4]} ] {msg}")
        time.sleep(TICK * 0.4)
    _w("\r" + c(f"  [ OK ] {msg}", GREEN) + "\n")


def progress_bar():
    total = 20
    for i in range(total + 1):
        filled = "█" * i
        rest = "░" * (total - i)
        pct = i * 5
        _w("\r" + f"  [{filled}{rest}] {pct:3d}%  {c('arming velocity engine', DIM)}")
        time.sleep(TICK * (0.5 if FAST else 1.1))
    _w("\n")


def armed_flash():
    line = "  ⚡ MANDATE TRIGGERED · STATUS: ARMED"
    for _ in range(3):
        _w("\r" + c(line, RED))
        time.sleep(TICK * 1.6)
        _w("\r" + c(line, BOLD))
        time.sleep(TICK * 1.6)
    _w("\n")


def pulse():
    for i in range(6):
        frame = "  " + PULSE
        _w("\r" + c(frame, YEL))
        time.sleep(TICK * 1.8)
    _w("\n")


def animate():
    try:
        _w("\x1b[?25l")            # hide cursor
        _w("\x1b[2J\x1b[H")        # clear + home
        typewriter("  ▸ 3AM SHINJITSU — TRIGGER SEQUENCE", CYAN)
        _w("\n")
        sweep_rule()
        time.sleep(TICK * 0.8)
        boot_line("core", "mandate core loaded")
        boot_line("gate", "scope gate armed")
        boot_line("engn", "velocity engine online")
        progress_bar()
        armed_flash()
        pulse()
        _w(c("  ─ waiting P0: target · objective · authorization", DIM) + "\n\n")
    finally:
        _w("\x1b[?25h")            # restore cursor


def main():
    if not IS_TTY:
        print(STATIC)
        return 0
    try:
        animate()
    except KeyboardInterrupt:
        _w("\x1b[?25h\n")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())