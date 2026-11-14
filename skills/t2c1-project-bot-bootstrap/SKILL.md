---
name: t2c1-project-bot-bootstrap
description: Use this when you start a t2c1 repository.
---
# t2c1 Project and Bot Bootstrap

Use this checklist for a new t2c1 repository.

## Repository setup

Create the repository with a thin `CLAUDE.md`.
Point that file at the shared anbu skills.
Record only the project-specific facts in that file.
Record the stack, the lint command, and the test command.
Record the branch workflow and the environment boundaries.
Add a `.gitignore` before the first feature branch.

Cover `.env`, local state, and build artifacts in that file.
Wire CI before the first feature work.
Make CI enforce format, lint, and unit tests.
Make CI enforce golden-file checks when the project has those files.
Make CI enforce IaC checks when the project has infrastructure.

## Shared scope

Point the project at these shared skills.

- t2c1 Engineering Standards
- t2c1 Merge Gate Review
- t2c1 Cloud Agent and PR Workflow
- t2c1 Voice and Drafting
Verify the connected GitHub, Linear, and Notion workspaces.
Verify the Cursor cloud agent environments.

Do this check before you hand off the first build task.
Do not put a private assistant rule in this standard.
Do not put a private escalation path in this standard.
