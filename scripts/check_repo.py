#!/usr/bin/env python3
"""Load the plugin manifest and check frontmatter, STE, and the em dash rule."""

import ast
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EM_DASH = "\u2014"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
SENTENCE_SPLIT_RE = re.compile(r"[.?!]\s+[A-Z]")
ING_RE_SKIP = {
    "during",
    "anything",
    "something",
    "nothing",
    "everything",
    "engineering",
    "warning",
    "drafting",
    "coding",
    "ing",
    "thing",
    "meaning",
    "boring",
}
IMPERATIVES = {
    "add",
    "apply",
    "ask",
    "block",
    "change",
    "check",
    "close",
    "confirm",
    "copy",
    "cover",
    "create",
    "cut",
    "define",
    "dispatch",
    "do",
    "edit",
    "enable",
    "end",
    "escalate",
    "flag",
    "follow",
    "forbid",
    "give",
    "group",
    "hand",
    "include",
    "install",
    "judge",
    "keep",
    "launch",
    "leave",
    "list",
    "make",
    "name",
    "never",
    "open",
    "pass",
    "point",
    "prefer",
    "put",
    "read",
    "record",
    "report",
    "require",
    "reserve",
    "return",
    "run",
    "say",
    "set",
    "split",
    "state",
    "stay",
    "stop",
    "tell",
    "treat",
    "use",
    "verify",
    "wire",
    "wrap",
    "write",
}
SKILLS = {
    "t2c1-engineering-standards": "standards/engineering-standards.md",
    "t2c1-voice-drafting": "standards/voice-and-drafting.md",
    "t2c1-merge-gate-review": "standards/merge-gate.md",
    "t2c1-cloud-agent-pr-workflow": "standards/cloud-agent-pr-workflow.md",
    "t2c1-project-bot-bootstrap": "standards/project-bootstrap.md",
}
AGENTS = {
    "spec-test-writer": (
        "agents/spec-test-writer.md",
        ("do not change product code", "do not merge"),
    ),
    "failure-triager": (
        "agents/failure-triager.md",
        ("you do not change code", "do not edit a file"),
    ),
    "single-issue-fixer": (
        "agents/single-issue-fixer.md",
        ("do not fix a second issue", "reproduce it before you write the fix", "do not merge"),
    ),
    "merge-gate-reviewer": (
        "agents/merge-gate-reviewer.md",
        (
            "you never merge",
            "gate 1",
            "gate 2",
            "gate 3",
            "gate 4",
            "do not run `git merge`",
            "do not run `gh pr merge`",
        ),
    ),
}
COMMANDS = (
    "write-spec",
    "triage-failures",
    "fix-issue",
    "review-gate",
)
PHRASES = {
    "standards/engineering-standards.md": (
        "em dash",
        "CHANGELOG.md",
        "auto-generated",
        "ASD-STE100",
        "20 words",
        "25 words",
        "active voice",
        "Terragrunt",
        "%w",
        "one-off",
        "unit tests",
        "integration test",
        "blast radius",
    ),
    "standards/voice-and-drafting.md": (
        "Hey X",
        "Best,",
        "emoji",
        "idiom",
        "audience",
        "em dash",
    ),
    "standards/merge-gate.md": (
        "Gate 1",
        "Gate 2",
        "Gate 3",
        "Gate 4",
        "Do not merge",
        "the human reviewer",
        "hardcoded",
        ".env",
    ),
    "standards/cloud-agent-pr-workflow.md": (
        "ReAct",
        "Reason",
        "CLAUDE.md",
        "direct-to-main",
        "pipeline apply",
        "human reviewer",
    ),
    "standards/project-bootstrap.md": (
        ".gitignore",
        ".env",
        "private assistant",
        "private escalation",
    ),
}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def parse_frontmatter(text: str, label: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        fail(f"{label}: frontmatter does not open on line 1.")
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(f"{label}: frontmatter does not close.")
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict = {}
    current = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current is None or not isinstance(data.get(current), list):
                fail(f"{label}: a list item has no key.")
                continue
            data[current].append(line[4:].strip())
            continue
        if ":" not in line:
            fail(f"{label}: frontmatter has a bad line.")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            current = key
            data[key] = []
            continue
        current = None
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        data[key] = value
    return data, body


def words_of(line: str) -> list[str]:
    masked = re.sub(r"`[^`]*`", " NAME ", line)
    masked = re.sub(r'"[^"]*"', " ", masked)
    return WORD_RE.findall(masked)


def check_sentence(label: str, line_no: int, line: str) -> None:
    count = len(words_of(line))
    first = words_of(line)[:1]
    limit = 25
    if first and first[0].lower() in IMPERATIVES:
        limit = 20
    if count > limit:
        fail(f"{label}:{line_no}: the sentence has {count} words. The limit is {limit}.")
    for word in words_of(line):
        token = word.lower()
        if token.endswith("ing") and token not in ING_RE_SKIP:
            fail(f"{label}:{line_no}: the word '{word}' is an -ing verb form.")
    masked = re.sub(r"`[^`]*`", "X", line)
    masked = masked.replace("Mr.", "Mr")
    masked = masked.replace("...", "")
    if SENTENCE_SPLIT_RE.search(masked):
        fail(f"{label}:{line_no}: the line has two sentences.")
    if not re.search(r"[.?!][\"']?$", line):
        fail(f"{label}:{line_no}: the line does not end with a stop mark.")


def check_markdown(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    label = str(path.relative_to(ROOT))
    body = text
    if text.startswith("---\n"):
        data, body = parse_frontmatter(text, label)
        description = data.get("description")
        if not isinstance(description, str) or not description.strip():
            fail(f"{label}: frontmatter needs a description.")
        else:
            check_sentence(label, 1, description)
    lines = body.splitlines()
    in_fence = False
    paragraph = 0
    paragraph_start = 1

    def flush(line_no: int) -> None:
        nonlocal paragraph, paragraph_start
        if paragraph > 6:
            fail(
                f"{label}:{paragraph_start}: the paragraph has {paragraph} sentences. The limit is 6."
            )
        paragraph = 0
        paragraph_start = line_no

    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            flush(index)
            continue
        if in_fence:
            continue
        if not stripped or stripped.startswith("#") or stripped == "$ARGUMENTS":
            flush(index)
            continue
        if stripped.startswith("|"):
            flush(index)
            continue
        prose = re.sub(r"^[-*]\s+", "", stripped)
        prose = re.sub(r"^\d+\.\s+", "", prose)
        check_sentence(label, index, prose)
        if paragraph == 0:
            paragraph_start = index
        paragraph += 1
    flush(len(lines) + 1)


def check_em_dash(path: Path) -> None:
    data = path.read_bytes()
    if EM_DASH.encode("utf-8") in data:
        fail(f"{path.relative_to(ROOT)}: the file contains an em dash.")


def check_url(label: str, value: object) -> None:
    if not isinstance(value, str):
        fail(f"{label}: the value is not a URL string.")
        return
    parts = urllib.parse.urlparse(value)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        fail(f"{label}: the URL does not load as an http URL.")


def check_plugin() -> None:
    path = ROOT / ".claude-plugin" / "plugin.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f".claude-plugin/plugin.json: the plugin manifest does not load. {exc}")
        return
    if not isinstance(manifest, dict):
        fail(".claude-plugin/plugin.json: the plugin manifest does not load as an object.")
        return
    name = manifest.get("name")
    if name != "anbu" or not isinstance(name, str) or NAME_RE.fullmatch(name) is None:
        fail(".claude-plugin/plugin.json: name must be anbu.")
    description = manifest.get("description")
    if not isinstance(description, str) or not description.strip():
        fail(".claude-plugin/plugin.json: description is empty.")
    version = manifest.get("version")
    if not isinstance(version, str) or re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        fail(".claude-plugin/plugin.json: version must be major.minor.patch.")
    author = manifest.get("author")
    if not isinstance(author, dict) or not str(author.get("name") or "").strip():
        fail(".claude-plugin/plugin.json: author.name is required.")
    check_url(".claude-plugin/plugin.json homepage", manifest.get("homepage"))
    check_url(".claude-plugin/plugin.json repository", manifest.get("repository"))
    keywords = manifest.get("keywords")
    if not isinstance(keywords, list) or not keywords or not all(isinstance(item, str) for item in keywords):
        fail(".claude-plugin/plugin.json: keywords must be a list of strings.")


def check_marketplace() -> None:
    path = ROOT / ".claude-plugin" / "marketplace.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f".claude-plugin/marketplace.json: the marketplace manifest does not load. {exc}")
        return
    if manifest.get("name") != "anbu":
        fail(".claude-plugin/marketplace.json: name must be anbu.")
    owner = manifest.get("owner")
    if not isinstance(owner, dict) or not str(owner.get("name") or "").strip():
        fail(".claude-plugin/marketplace.json: owner.name is required.")
    plugins = manifest.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        fail(".claude-plugin/marketplace.json: plugins must list one plugin.")
        return
    entry = plugins[0]
    if entry.get("name") != "anbu":
        fail(".claude-plugin/marketplace.json: the plugin entry name must be anbu.")
    if entry.get("source") != "./":
        fail(".claude-plugin/marketplace.json: source must be ./.")
    if not str(entry.get("description") or "").strip():
        fail(".claude-plugin/marketplace.json: the plugin entry needs a description.")


def check_skills() -> None:
    root = ROOT / "skills"
    found = sorted(path.parent.name for path in root.glob("*/SKILL.md"))
    if found != sorted(SKILLS):
        fail(f"skills: expected {sorted(SKILLS)} but found {found}.")
    for name, standard_rel in SKILLS.items():
        skill_path = root / name / "SKILL.md"
        standard_path = ROOT / standard_rel
        text = skill_path.read_text(encoding="utf-8")
        data, body = parse_frontmatter(text, f"skills/{name}/SKILL.md")
        if data.get("name") != name:
            fail(f"skills/{name}/SKILL.md: name must match the directory.")
        elif NAME_RE.fullmatch(name) is None or len(name) > 64:
            fail(f"skills/{name}/SKILL.md: name must be kebab-case and at most 64 characters.")
        description = data.get("description")
        if not isinstance(description, str) or not description.strip():
            fail(f"skills/{name}/SKILL.md: description is empty.")
        elif len(description) > 1024:
            fail(f"skills/{name}/SKILL.md: description is too long.")
        standard = standard_path.read_text(encoding="utf-8")
        if body != standard:
            fail(f"skills/{name}/SKILL.md: the body does not match {standard_rel}.")
        for phrase in PHRASES[standard_rel]:
            if phrase not in standard:
                fail(f"{standard_rel}: the file lacks the phrase {phrase!r}.")


def check_agents() -> None:
    for name, (rel, phrases) in AGENTS.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        data, _body = parse_frontmatter(text, rel)
        if data.get("name") != name:
            fail(f"{rel}: name must be {name}.")
        if not str(data.get("description") or "").strip():
            fail(f"{rel}: description is empty.")
        if not str(data.get("tools") or "").strip():
            fail(f"{rel}: tools must list the allowed tools.")
        if data.get("model") != "inherit":
            fail(f"{rel}: model must be inherit.")
        try:
            turns = int(data.get("maxTurns"))
        except (TypeError, ValueError):
            turns = 0
        if not 1 <= turns <= 80:
            fail(f"{rel}: maxTurns must be a bound from 1 to 80.")
        skills = data.get("skills")
        if not isinstance(skills, list) or not skills:
            fail(f"{rel}: skills must list one or more skills.")
        else:
            for skill in skills:
                if skill not in SKILLS:
                    fail(f"{rel}: unknown skill {skill}.")
        if name == "merge-gate-reviewer" and "Edit" in str(data.get("tools")):
            fail(f"{rel}: the merge-gate reviewer must not edit files.")
        if name == "merge-gate-reviewer" and "Write" in str(data.get("tools")):
            fail(f"{rel}: the merge-gate reviewer must not write files.")
        lowered = text.lower()
        for phrase in phrases:
            if phrase not in lowered:
                fail(f"{rel}: the file lacks the phrase {phrase!r}.")


def check_commands() -> None:
    found = sorted(path.stem for path in (ROOT / "commands").glob("*.md"))
    if found != sorted(COMMANDS):
        fail(f"commands: expected {sorted(COMMANDS)} but found {found}.")
    for name in COMMANDS:
        rel = f"commands/{name}.md"
        text = (ROOT / rel).read_text(encoding="utf-8")
        data, body = parse_frontmatter(text, rel)
        if not str(data.get("description") or "").strip():
            fail(f"{rel}: description is empty.")
        if "$ARGUMENTS" not in body:
            fail(f"{rel}: the command must accept arguments.")
        if "do not merge" not in body.lower():
            fail(f"{rel}: the command must tell the agent not to merge.")


def check_hooks() -> None:
    path = ROOT / "hooks" / "hooks.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"hooks/hooks.json: the hook manifest does not load. {exc}")
        return
    hooks = manifest.get("hooks")
    if not isinstance(hooks, dict) or "PreToolUse" not in hooks:
        fail("hooks/hooks.json: hooks.PreToolUse is required.")
        return
    blob = json.dumps(manifest)
    for script in ("hooks/block-merge.py", "hooks/block-em-dash.py"):
        if script not in blob:
            fail(f"hooks/hooks.json: the manifest must call {script}.")
        file_path = ROOT / script
        if not file_path.is_file():
            fail(f"{script}: the hook file is absent.")
            continue
        try:
            ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            fail(f"{script}: the hook does not parse. {exc}")
    run_hook_samples()


def run_hook(script: str, payload: object) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / script)],
        input=json.dumps(payload).encode("utf-8"),
        capture_output=True,
        check=False,
    )
    return proc.returncode, proc.stdout.decode("utf-8")


def expect_deny(script: str, payload: object, label: str) -> None:
    code, out = run_hook(script, payload)
    if code != 0 or '"permissionDecision": "deny"' not in out:
        fail(f"{script}: {label} did not deny the call.")


def expect_allow(script: str, payload: object, label: str) -> None:
    code, out = run_hook(script, payload)
    if code != 0 or out.strip():
        fail(f"{script}: {label} did not allow the call.")


def run_hook_samples() -> None:
    expect_deny(
        "hooks/block-merge.py",
        {
            "agent_type": "anbu:merge-gate-reviewer",
            "tool_input": {"command": "gh pr merge 1"},
        },
        "a merge-gate gh pr merge",
    )
    expect_deny(
        "hooks/block-merge.py",
        {
            "agent_type": "anbu:single-issue-fixer",
            "tool_input": {"command": "pytest && git merge main"},
        },
        "a fixer git merge",
    )
    expect_allow(
        "hooks/block-merge.py",
        {"tool_input": {"command": "gh pr merge 1"}},
        "a main-session merge",
    )
    expect_allow(
        "hooks/block-merge.py",
        {
            "agent_type": "anbu:merge-gate-reviewer",
            "tool_input": {"command": "git status"},
        },
        "a status command",
    )
    em = "\u2014"
    expect_deny(
        "hooks/block-em-dash.py",
        {"tool_input": {"content": f"bad {em} dash"}},
        "a write with an em dash",
    )
    expect_deny(
        "hooks/block-em-dash.py",
        {"tool_input": {"new_string": em}},
        "an edit with an em dash",
    )
    expect_allow(
        "hooks/block-em-dash.py",
        {"tool_input": {"content": "plain - dash"}},
        "a write with a plain dash",
    )
    proc = subprocess.run(
        [sys.executable, str(ROOT / "hooks" / "block-merge.py")],
        input=b"not-json",
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0 or proc.stdout.strip():
        fail("hooks/block-merge.py: bad input must not block the call.")


def check_tree() -> None:
    if (ROOT / "CLAUDE.md").exists():
        fail("CLAUDE.md: do not put this file at the plugin root.")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if ".env" not in gitignore:
        fail(".gitignore: the file must ignore .env.")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "/plugin install anbu@anbu" not in readme:
        fail("README.md: the file must show the plugin install line.")
    skip = {".git", "node_modules", "__pycache__", ".venv"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip for part in path.relative_to(ROOT).parts):
            continue
        if path.name == ".env":
            fail(f"{path.relative_to(ROOT)}: do not commit an env file.")
        check_em_dash(path)


def check_markdown_tree() -> None:
    for path in sorted(ROOT.rglob("*.md")):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        check_markdown(path)


def main() -> int:
    check_tree()
    check_plugin()
    check_marketplace()
    check_skills()
    check_agents()
    check_commands()
    check_hooks()
    check_markdown_tree()
    if errors:
        for message in errors:
            print(message)
        print(f"{len(errors)} check(s) failed.")
        return 1
    print("The plugin manifest loads. Frontmatter, STE, and the em dash scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
