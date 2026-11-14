#!/usr/bin/env python3
"""Block a write that contains an em dash."""

import json
import sys

EM_DASH = "\u2014"


def text_parts(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from text_parts(item)
    elif isinstance(value, list):
        for item in value:
            yield from text_parts(item)


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    blob = "\n".join(text_parts(data.get("tool_input") or {}))
    if EM_DASH not in blob:
        return 0
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "The text has an em dash. Use a plain dash.",
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
