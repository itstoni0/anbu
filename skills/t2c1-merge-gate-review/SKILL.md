---
name: t2c1-merge-gate-review
description: Use this when you review a pull request or a diff before the human reviewer merges.
---
# t2c1 Merge Gate Review

Run this four-part gate before you approve a pull request.
Run this four-part gate before you hand an implementation to the human reviewer.
The human reviewer makes the merge decision.

## Gate 1 - Build and CI

Confirm that the build compiles with a clean result.
Confirm that every required CI check passes.
Confirm that every required linter passes.
Do not ignore a failure.
Confirm that generated files match their sources.
Confirm that lock files match their sources.

Confirm that golden files match their sources.
Do not leave a file that needs a fresh generation.

## Gate 2 - Coding standards and drift

Confirm that the change follows t2c1 Engineering Standards.
Confirm that the change follows the repository `CLAUDE.md`.
Confirm that the diff has no em dash.
Confirm that nobody edited a generated file by hand.
Confirm that the diff has no speculative abstraction for one-off code.
Confirm that the PR title follows ASD-STE100 Simplified Technical English.

Confirm that the PR description follows ASD-STE100 Simplified Technical English.
Confirm that each commit message follows ASD-STE100 Simplified Technical English.
Confirm that code comments in the diff follow ASD-STE100 Simplified Technical English.
Confirm that docs in the diff follow ASD-STE100 Simplified Technical English.
For an infrastructure change, check environment drift.
For an infrastructure change, check unintended blast radius.

For an infrastructure change, check side effects across environments.

## Gate 3 - Security and hygiene

Check the diff for a committed `.env` file.
Check the diff for a secret, a token, or a hardcoded credential.
Check the diff for an IAM rule that grants too much access.
Check the diff for a network rule that grants too much access.
Check the diff for input that the code does not validate.
Confirm that sensitive defaults stay in place.

Confirm that production safety guardrails stay in place.

## Gate 4 - Regression and verification

Confirm that unit tests cover the changed behavior.
Confirm that unit tests cover the edge cases.
Confirm that a bug fix was reproduced under realistic conditions.
Do not merge the pull request yourself.
Hand off with a short note in ASD-STE100 Simplified Technical English.
Point the note at the exact files, lines, and primary sources.

Do not replace a primary source with a summary.
The human reviewer makes the final merge decision.
