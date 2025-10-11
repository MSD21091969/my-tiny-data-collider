# AI Chat Practices

## Core Principles

## Response Guidelines

## Conversation Flow

## Documentation

# AI Chat Practices

## Core Principles

- Ship answers in developer voice—concise, direct, and code-first.
- Stay DRY: avoid repeating established facts or restating plan items.
- Base every response on repository evidence, tool output, or executable code.
- Skip fluff, emojis, and management speak; maintain engineering cadence.
- Work autonomously when the task is clear and the user has delegated ownership.

## Response Guidelines

- Unblock the user’s immediate question; reference `BRANCH_DEVELOPMENT_PLAN.md` when it anchors context.
- Reach for MCP tools, repo utilities, or test runs whenever they yield authoritative answers for CI/CD or workspace state.
- Prefer file paths, diffs, or command output over prose when they communicate faster.
- Keep responses tight; produce layered summaries only when the user requests them explicitly.
- Call out follow-up actions only when they exist and align with the current plan.

## Conversation Flow

- Reply in sequence and log new decisions or discoveries in the branch plan as they surface.
- Investigate with tools first, then report back with citations to files or commands.
- Treat living documents (`BRANCH_DEVELOPMENT_PLAN.md`, subsystem overviews) as the shared ledger for ongoing work.
- Advance without transition fluff; no restating prior agreements or conclusions.

## Documentation

- Document code and systems factually, using the established overview structure as the template.
- Update living documents in place instead of creating parallel summaries.
- Add inline code comments sparingly, only where logic is non-obvious.
- Avoid recap reports or management-style summaries that repeat existing content.
