# anbu

## What it is

Inspired by how the AWS team built AWS Emulator, anbu is my agent factory for building software with teams of agents.

## How to install

Run `/plugin marketplace add itstoni0/anbu`.
Run `/plugin install anbu@anbu`.

## How to use

Copy `templates/CLAUDE.md` into the project as its `CLAUDE.md`.

`/anbu:write-spec` takes one behavior, writes the specs and tests, runs the tests, and does not change product code.
`/anbu:triage-failures` takes a test command or a failure log, groups failures that share one cause, and does not change code.
`/anbu:fix-issue` takes one issue, fixes only that issue, and then stops.
`/anbu:review-gate` takes a diff or a pull request, runs the four gates, and does not merge.

Follow this order.

1. Send one behavior to `/anbu:write-spec` so the agent writes the specs and tests and runs them.
2. Send the test result to `/anbu:triage-failures` so the agent groups shared causes.
3. Send one issue to `/anbu:fix-issue`.
4. Repeat that command for each other issue.
5. Send the diff to `/anbu:review-gate` so the agent runs the four gates.
6. The human reviewer reviews the change and merges it.
