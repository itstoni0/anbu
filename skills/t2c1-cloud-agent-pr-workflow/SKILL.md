---
name: t2c1-cloud-agent-pr-workflow
description: Use this when you scope, launch, or steer an agent, or when you prepare a pull request.
---
# t2c1 Cloud Agent and PR Workflow

Follow this workflow when you delegate repository work to an agent.
Follow this workflow when you manage a pull request.

## Before launch

Read the target repository `CLAUDE.md` first.
Confirm these facts in that file.

- The branch rules
- The linter config
- Any documented workflow exception

One example is a direct-to-main workflow.
Launch a Cursor cloud agent for a non-trivial investigation or code change.
Do not clone the repository for that work when a cloud agent can do it.

## Prompt structure

Write an agent prompt in a ReAct structure.
The structure is Reason, then Act, then Observe.
State the scope boundaries in the prompt.
State the phased review gates in the prompt.
State the production safety guardrails in the prompt.
Include the project branch name pattern.

One pattern is `<user>/<key>-<number>-<short-description>` when the work uses Linear.
Forbid em dashes in the prompt.
Tell the agent to write these texts in ASD-STE100 Simplified Technical English.

- PR descriptions
- Commit messages
- Code comments
- Linear comments
- GitHub comments
t2c1 Engineering Standards states the STE rules.

## Pull request rules

Keep each commit message short.
Keep each PR description short.
Give only the context that another engineer needs.
Write these texts in ASD-STE100 Simplified Technical English.

- PR descriptions
- Linear ticket comments
- Status updates

Use short sentences, the active voice, and one instruction per sentence.
Use the same term for the same thing.
An agent drafts the change and verifies the change.
The human reviewer reviews the change and merges the change.
For an infrastructure change, PR review is the deployment gate.
A merge to `main` starts the pipeline apply.
