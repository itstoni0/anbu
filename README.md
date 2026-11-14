# anbu

## What it is

anbu is the public standards repository for the t2c1 brand.
It holds the shared rules, the skills, and a bounded agent plugin.

## How to install

Run `/plugin marketplace add itstoni0/anbu`.
Run `/plugin install anbu@anbu`.

## How to use

Copy `templates/CLAUDE.md` into a project as its `CLAUDE.md`.
`/anbu:write-spec` sends one behavior to the spec and test writer.
`/anbu:triage-failures` sends a failure log to the failure triager.
`/anbu:fix-issue` sends one issue to the single-issue fixer.
`/anbu:review-gate` sends a diff to the merge-gate reviewer.
