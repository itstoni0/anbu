# anbu

anbu holds shared engineering standards, a skills library, and a bounded agent plugin.
Any project can point here from a thin `CLAUDE.md`.
The human reviewer reviews each change.
The human reviewer merges each change.

## Layout

`standards/` holds the five rule documents.
`skills/` holds the same rules as portable skills.
Each skill directory contains one `SKILL.md`.
The skill names are `t2c1-engineering-standards`, `t2c1-voice-drafting`, and `t2c1-merge-gate-review`.
The skill names also include `t2c1-cloud-agent-pr-workflow` and `t2c1-project-bot-bootstrap`.
`.claude-plugin/plugin.json` is the plugin manifest.

`.claude-plugin/marketplace.json` lists the plugin for install.
`agents/` holds four bounded subagents.
`commands/` holds one command for each subagent.
`hooks/` blocks a merge from those agents and blocks an em dash in a write.
`templates/CLAUDE.md` is the thin file for a downstream repository.
`scripts/check_repo.py` checks the manifest, the frontmatter, and the em dash rule.

`.github/workflows/ci.yml` runs that check and Markdown lint.

## Install the plugin

Add the anbu marketplace from GitHub.
Run `/plugin marketplace add itstoni0/anbu`.
Run `/plugin install anbu@anbu`.
You can also load a local checkout for one session.
Run `claude --plugin-dir /path/to/anbu` from that checkout.
The hooks call `python3`, so install Python 3 on that machine.

## Point a project at anbu

Put a thin `CLAUDE.md` in the project repository.
Point that file at `https://github.com/itstoni0/anbu`.
Copy `templates/CLAUDE.md`.
Fill in the project facts.
Do not copy the standards into the project.
Read the standards from this repository.

Enable the anbu plugin in that project when you want the agents.

## This repository

This repository has no root `CLAUDE.md`.
A root file of that name warns when the plugin manifest loads.
Use `templates/CLAUDE.md` for a downstream repository.

## Agents

`spec-test-writer` writes specs and tests for one behavior.
It does not change product code, and it stops after the test run.
`failure-triager` groups failures that share one root cause.
It does not change code, and it stops when every failure has a group.
`single-issue-fixer` fixes one issue and then stops.
It does not take a second issue, and it does not merge.

`merge-gate-reviewer` runs the build, standards, security, and regression gates.
It never merges, and it never edits a file to force a pass.
The human reviewer makes the merge decision.

## Commands

`/anbu:write-spec` sends one behavior to the spec and test writer.
`/anbu:triage-failures` sends a test failure log to the triager.
`/anbu:fix-issue` sends one issue to the fixer.
`/anbu:review-gate` sends a diff to the merge-gate reviewer.
The main session does not do that work itself.

## CI

CI lints Markdown.
CI loads the plugin manifest and the skill, agent, and command frontmatter.
CI fails when any file contains an em dash.
