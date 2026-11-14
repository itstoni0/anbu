# t2c1 Cloud Agent and PR Workflow

Follow this workflow when you delegate repository work to an agent.
Follow this workflow when you manage a pull request.

## Before launch

Read the target repository `CLAUDE.md` first.
Confirm the branch rules in that file.
Confirm the linter config in that file.
Confirm any documented workflow exception in that file.
One example is a direct-to-main workflow.
Launch a Cursor cloud agent for a non-trivial repository investigation.

Launch a Cursor cloud agent for a non-trivial code change.
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
Tell the agent to write each PR description in ASD-STE100 Simplified Technical English.
Tell the agent to write each commit message in ASD-STE100 Simplified Technical English.
Tell the agent to write each code comment in ASD-STE100 Simplified Technical English.
Tell the agent to write each Linear comment in ASD-STE100 Simplified Technical English.

Tell the agent to write each GitHub comment in ASD-STE100 Simplified Technical English.
t2c1 Engineering Standards states the STE rules.

## Pull request rules

Keep each commit message short.
Keep each PR description short.
Give only the context that another engineer needs.
Write PR descriptions in ASD-STE100 Simplified Technical English.
Write Linear ticket comments in ASD-STE100 Simplified Technical English.
Write status updates in ASD-STE100 Simplified Technical English.

Use short sentences, the active voice, and one instruction per sentence.
Use the same term for the same thing.
An agent drafts the change and verifies the change.
The human reviewer reviews the change and merges the change.
For an infrastructure change, PR review is the deployment gate.
A merge to `main` starts the pipeline apply.
