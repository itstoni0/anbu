---
name: t2c1-engineering-standards
description: Use this when you write code, organize IaC, review a technical choice, or set project rules.
---
# t2c1 Engineering Standards

Apply these baseline standards on every t2c1 project.
A repository may record an exception in its `CLAUDE.md`.
That file must state the exception in clear text.

## Non-negotiable rules

Never use an em dash in code comments, docs, commits, or copy.
Use a plain dash `-` in place of an em dash.
Never edit `CHANGELOG.md` by hand.
Never edit a file that the project marks as auto-generated.
Put each full sentence on its own line in a long Markdown file.
Write agent technical text in ASD-STE100 Simplified Technical English.

The next section states the STE rules.

## Written content (ASD-STE100)

This rule covers every technical text that an agent writes.
The list is PR titles, PR descriptions, and commit messages.
The list also covers Linear issues, Linear comments, GitHub issues, and review comments.
The list also covers code comments, READMEs, and docs.

Use one word for one meaning.
Use the same term for the same thing every time.
Use common words.
Use a technical name as it stands.
Examples of technical names are `terragrunt`, `VPC`, and `golangci-lint`.
Write a procedural sentence of 20 words or fewer.

Write a descriptive sentence of 25 words or fewer.
Write one instruction in each sentence.
Use the imperative for an instruction.
An example is "Run the tests."
Put the steps in a numbered list when the order matters.
Use the active voice.

Say who or what does the action.
Use the simple present, the simple past, or the simple future.
Do not use an "-ing" verb form, except in a technical name.
Do not drop an article to make a sentence short.
The articles are "a", "an", and "the".
Do not drop a verb to make a sentence short.

Write a paragraph of 6 sentences or fewer.
Give each paragraph one topic.
Put a warning before the step that it covers.
Put a caution before the step that it covers.

## Engineering judgment

Prefer quality, simplicity, robustness, scalability, and long-term maintainability.
This preference is strongest for platform code and for IaC code.
Do not trade those qualities for a faster implementation.
Reproduce a bug before you propose a fix.
Reproduce a bug before you write a fix.
Use an environment as close to real use as you can.

Flag a lint error when you see it.
Flag a failed test or a flaky test when you see it.
Flag infrastructure drift when you see it.
Flag an unintended blast radius when you see it.
Flag an inconsistent module pattern when you see it.
Flag these issues even when they sit outside the current task.

## Language and IaC defaults

Write boring Go.
Prefer the standard library.
Keep dependencies few.
Wrap a plain error with `%w`.
Define a small interface at the point of use.
Use generics rarely.

Use Terragrunt to organize Terraform on a new project.
Split infrastructure into a separate module only when more than one environment reuses it.
Never make a module for a one-off use.
Never make a helper abstraction for a one-off use.
Write unit tests first.
Reserve an integration test for a critical path.
