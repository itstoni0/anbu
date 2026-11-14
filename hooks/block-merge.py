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

GIT_MERGE = re.compile(
    r"""
    \bgit\b
    (?:
        \s+
        (?:
            -(?:C|c)\s+\S+
            | --(?:git-dir|work-tree|namespace|super-prefix|config-env|exec-path)(?:=\S+|\s+\S+)
            | --[\w-]+
            | -[A-Za-z]+
        )
    )*
    \s+merge(?![\w-])
    """,
    re.IGNORECASE | re.VERBOSE,
)
OTHER_MERGE = re.compile(
    r"\b(?:gh\s+pr\s+merge|hub\s+merge)(?![\w-])",
    re.IGNORECASE,
)


def normalize(command: str) -> str:
    text = re.sub(r'"([^"]*)"', r" \1 ", command)
    return re.sub(r"'([^']*)'", r" \1 ", text)


def is_merge(command: str) -> bool:
    text = normalize(command)
    return GIT_MERGE.search(text) is not None or OTHER_MERGE.search(text) is not None


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    agent = str(data.get("agent_type") or "")
    if agent.split(":")[-1] not in AGENTS:
        return 0
    command = str((data.get("tool_input") or {}).get("command") or "")
    if not is_merge(command):
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
