#!/usr/bin/env python3
"""PreToolUse guard for the knowledge base vault.

Blocks destructive bash commands. Exit code 2 = block (stderr shown to Claude).
Reads the hook event JSON from stdin.
"""
import json
import re
import sys

try:
    event = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # can't parse — don't break the session

command = (event.get("tool_input") or {}).get("command", "")
if not command:
    sys.exit(0)

BLOCKED = [
    (r"\brm\s+(-[a-zA-Z]*[rf][a-zA-Z]*\s+)+", "recursive/forced rm is not allowed; move files to _archive/ instead"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard rewrites history; the vault's git log is the audit trail"),
    (r"\bgit\s+clean\b", "git clean deletes untracked files; not allowed in the vault"),
    (r"\bgit\s+push\s+.*(--force|-f)\b", "force pushes rewrite history; not allowed"),
    (r"\bgit\s+checkout\s+\.\s*$", "git checkout . discards uncommitted work; commit or stash explicitly instead"),
    (r">\s*/dev/sd", "raw device writes are not allowed"),
]

for pattern, reason in BLOCKED:
    if re.search(pattern, command):
        print(f"BLOCKED by vault guard: {reason}\nCommand was: {command}", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
