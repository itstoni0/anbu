#!/usr/bin/env python3
"""Load the manifests and run the repository checks."""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EM_DASH = chr(0x2014)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILLS = (
    "t2c1-cloud-agent-pr-workflow",
    "t2c1-engineering-standards",
    "t2c1-merge-gate-review",
    "t2c1-project-bot-bootstrap",
    "t2c1-voice-drafting",
)
AGENTS = (
    "failure-triager",
    "merge-gate-reviewer",
    "single-issue-fixer",
    "spec-test-writer",
)
COMMANDS = (
    "fix-issue",
    "review-gate",
    "triage-failures",
    "write-spec",
)
SKIP = {".git", "node_modules", "__pycache__", ".venv"}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_json(rel: str):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{rel}: the manifest does not load. {exc}")
        return None


def frontmatter(text: str, label: str) -> dict:
    if not text.startswith("---\n"):
        fail(f"{label}: frontmatter does not open on line 1.")
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(f"{label}: frontmatter does not close.")
        return {}
    data: dict = {}
    key = None
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and isinstance(data.get(key), list):
            data[key].append(line[4:].strip())
            continue
        if ":" not in line:
            fail(f"{label}: frontmatter has a bad line.")
            continue
        name, value = line.split(":", 1)
        key = name.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        data[key] = [] if value == "" else value
    return data


def need_text(data: dict, field: str, label: str) -> None:
    if not str(data.get(field) or "").strip():
        fail(f"{label}: {field} is empty.")


def check_plugin() -> None:
    data = load_json(".claude-plugin/plugin.json")
    if not isinstance(data, dict):
        return
    if data.get("name") != "anbu":
        fail(".claude-plugin/plugin.json: name must be anbu.")


def check_marketplace() -> None:
    data = load_json(".claude-plugin/marketplace.json")
    if not isinstance(data, dict):
        return
    if data.get("name") != "anbu":
        fail(".claude-plugin/marketplace.json: name must be anbu.")
    owner = data.get("owner")
    if not isinstance(owner, dict) or not str(owner.get("name") or "").strip():
        fail(".claude-plugin/marketplace.json: owner.name is required.")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        fail(".claude-plugin/marketplace.json: plugins must list the plugin.")
        return
    entry = plugins[0]
    if not isinstance(entry, dict) or not entry.get("name") or not entry.get("source"):
        fail(".claude-plugin/marketplace.json: each plugin needs a name and a source.")


def check_skills() -> None:
    found = sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))
    if found != list(SKILLS):
        fail(f"skills: expected {list(SKILLS)} but found {found}.")
    for name in SKILLS:
        rel = f"skills/{name}/SKILL.md"
        path = ROOT / rel
        if not path.is_file():
            continue
        data = frontmatter(path.read_text(encoding="utf-8"), rel)
        if data.get("name") != name or NAME_RE.fullmatch(name) is None or len(name) > 64:
            fail(f"{rel}: name must match the directory and use kebab-case.")
        need_text(data, "description", rel)


def check_agents() -> None:
    found = sorted(path.stem for path in (ROOT / "agents").glob("*.md"))
    if found != list(AGENTS):
        fail(f"agents: expected {list(AGENTS)} but found {found}.")
    for name in AGENTS:
        rel = f"agents/{name}.md"
        path = ROOT / rel
        if not path.is_file():
            continue
        data = frontmatter(path.read_text(encoding="utf-8"), rel)
        if data.get("name") != name:
            fail(f"{rel}: name must be {name}.")
        need_text(data, "description", rel)


def check_commands() -> None:
    found = sorted(path.stem for path in (ROOT / "commands").glob("*.md"))
    if found != list(COMMANDS):
        fail(f"commands: expected {list(COMMANDS)} but found {found}.")
    for name in COMMANDS:
        rel = f"commands/{name}.md"
        path = ROOT / rel
        if not path.is_file():
            continue
        data = frontmatter(path.read_text(encoding="utf-8"), rel)
        need_text(data, "description", rel)


def check_tree() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if ".env" not in gitignore:
        fail(".gitignore: the file must ignore .env.")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "/plugin install anbu@anbu" not in readme:
        fail("README.md: the file must show the plugin install line.")
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP for part in rel.parts):
            continue
        if path.name == ".env":
            fail(f"{rel}: do not commit an env file.")
        if EM_DASH.encode("utf-8") in path.read_bytes():
            fail(f"{rel}: the file contains an em dash.")


def run_hook(script: str, payload: object) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / script)],
        input=json.dumps(payload).encode("utf-8"),
        capture_output=True,
        check=False,
    )
    return proc.returncode, proc.stdout.decode("utf-8")


def expect(script: str, payload: object, deny: bool, label: str) -> None:
    code, out = run_hook(script, payload)
    blocked = code == 0 and '"permissionDecision": "deny"' in out
    if deny and not blocked:
        fail(f"{script}: {label} did not deny the call.")
    if not deny and (code != 0 or out.strip()):
        fail(f"{script}: {label} did not allow the call.")


def check_hooks() -> None:
    agent = "anbu:merge-gate-reviewer"
    deny = (
        ("gh pr merge 1", "a direct gh pr merge"),
        ("pytest && git merge main", "a git merge after &&"),
        ("git -C repo merge", "a git merge after -C"),
        ("git --git-dir=x merge", "a git merge after --git-dir"),
        ("true && gh pr merge 1", "a gh pr merge after &&"),
        ("(git merge main)", "a git merge in a subshell"),
        ('bash -c "git merge main"', "a git merge inside quotes"),
    )
    for command, label in deny:
        expect(
            "hooks/block-merge.py",
            {"agent_type": agent, "tool_input": {"command": command}},
            True,
            label,
        )
    expect(
        "hooks/block-merge.py",
        {"tool_input": {"command": "gh pr merge 1"}},
        False,
        "a main-session merge",
    )
    expect(
        "hooks/block-merge.py",
        {"agent_type": agent, "tool_input": {"command": "git status"}},
        False,
        "a status command",
    )
    expect(
        "hooks/block-merge.py",
        {"agent_type": agent, "tool_input": {"command": "git mergetool"}},
        False,
        "a mergetool command",
    )
    em = chr(0x2014)
    expect(
        "hooks/block-em-dash.py",
        {"tool_input": {"content": f"bad {em} dash"}},
        True,
        "a write with an em dash",
    )
    expect(
        "hooks/block-em-dash.py",
        {"tool_input": {"content": "plain - dash"}},
        False,
        "a write with a plain dash",
    )


def main() -> int:
    check_plugin()
    check_marketplace()
    check_skills()
    check_agents()
    check_commands()
    check_tree()
    check_hooks()
    if errors:
        print("\n".join(errors))
        print(f"{len(errors)} check(s) failed.")
        return 1
    print("The plugin manifest loads. The repository checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
