#!/usr/bin/env python3
"""Block a merge command from an anbu subagent."""

import json
import re
import sys

AGENTS = {
    "spec-test-writer",
    "failure-triager",
    "single-issue-fixer",
    "merge-gate-reviewer",
}

MERGE = re.compile(
    r"(?:^|[;&|]\s*)(?:git\s+merge|gh\s+pr\s+merge|hub\s+merge)\b",
    re.IGNORECASE,
)


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    agent = str(data.get("agent_type") or "")
    short = agent.split(":")[-1]
    if short not in AGENTS:
        return 0
    command = str((data.get("tool_input") or {}).get("command") or "")
    if MERGE.search(command) is None:
        return 0
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "An anbu agent does not merge. The human reviewer merges.",
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
