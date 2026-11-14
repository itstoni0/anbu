---
description: Send a diff to the merge-gate reviewer.
argument-hint: "<diff-or-pull-request>"
---
# Review the merge gate

Dispatch the `anbu:merge-gate-reviewer` agent on this task.
Do not edit files in the main session to force a pass.
Pass the diff or the pull request below as the task input.
Ask for four verdicts.
Ask for a handoff note to Antonio.

Stop when the agent stops.
Do not merge.
Do not run `git merge`.
Do not run `gh pr merge`.

$ARGUMENTS
