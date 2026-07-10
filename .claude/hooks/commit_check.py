#!/usr/bin/env python3
"""Stop hook: prevent Claude from finishing with uncommitted vault changes.

If organized content (areas/, indexes/, reviews/, templates/, CLAUDE.md) has
uncommitted changes, exit 2 so Claude commits before stopping.
Uses stop_hook_active to avoid an infinite loop: if this hook already fired
once this stop cycle, allow the stop regardless.
"""
import json
import subprocess
import sys

try:
    event = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if event.get("stop_hook_active"):
    sys.exit(0)  # already nudged once — don't loop

WATCHED = ["areas", "indexes", "reviews", "templates", "CLAUDE.md"]

try:
    out = subprocess.run(
        ["git", "status", "--porcelain", "--"] + WATCHED,
        capture_output=True, text=True, timeout=10,
    ).stdout.strip()
except Exception:
    sys.exit(0)  # not a git repo yet, or git unavailable — don't block

if out:
    print(
        "Uncommitted vault changes detected:\n"
        f"{out}\n"
        "Commit them with a descriptive message (see CLAUDE.md conventions) before finishing.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
