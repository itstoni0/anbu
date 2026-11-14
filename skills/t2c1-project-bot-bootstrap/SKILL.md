---
name: t2c1-project-bot-bootstrap
description: Use this when you start a t2c1 repository or a project Grok Bot.
---
# t2c1 Project and Bot Bootstrap

Use this checklist for a new t2c1 repository.
Use this checklist for a new project Grok Bot.

## Repository setup

Create the repository with a thin `CLAUDE.md`.
Point that file at the shared anbu standards.
Record only the project-specific facts in that file.
Record the stack, the lint command, and the test command.
Record the branch workflow and the environment boundaries.
Add a `.gitignore` before the first feature branch.

Cover `.env`, local state, and build artifacts in that file.
Wire CI before the first feature work.
Make CI enforce format, lint, and unit tests.
Make CI enforce golden-file checks when the project has those files.
Make CI enforce IaC checks when the project has infrastructure.

## Project bot setup

Set the Grok Bot profile to the project scope.
Keep Reunitus and NetTracer outside that scope.
Escalate to Master Chief for a cross-project standard.
Escalate to Mr. Robot for a cross-project standard.
Escalate to Master Chief for a cloud agent task.
Escalate to Mr. Robot for a cloud agent task.

Point the bot at the shared skills.
The skills are t2c1 Engineering Standards and t2c1 Merge Gate Review.
The skills also include t2c1 Cloud Agent and PR Workflow.
The skills also include t2c1 Voice and Drafting.
Verify the connected GitHub, Linear, and Notion workspaces.
Verify the Cursor cloud agent environments.

Do this check before you hand off the first build task.
