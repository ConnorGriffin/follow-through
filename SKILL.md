---
name: follow-through
description: Ground personal advice in a private Markdown memory and maintain approved facts, preferences, people, life areas, work, decisions, plans, reviews, and outcomes. Use for personal decisions, life planning, relationship or preference context, follow-up reviews, unresolved personal work, or explicit bootstrap, decide, plan, and review requests.
---

# Follow Through

Use the configured private repository as durable personal context. The
repository owns its records and schema; this skill owns the workflow.

## Start

1. Resolve the repository by running `python3 scripts/follow_through.py where`
   from this skill directory. If setup is incomplete, follow the command's
   instruction and stop.
2. Read the repository's `AGENTS.md`, then `INDEX.md`.
3. On the first Follow Through request in a conversation, inspect due reviews
   and relevant open work as directed by `AGENTS.md`.
4. Search before reading broadly. Open only records useful to the request.
5. Briefly state which stored context materially informed the answer.

When creating or changing records, also read the repository's `CONTEXT.md`. It
is the authority for record types, metadata, statuses, transitions, templates,
links, and supersession.

## Route

Read [references/workflows.md](references/workflows.md), then follow the
matching workflow:

- ordinary advice or a personal question: retrieve
- explicit initial setup: bootstrap
- explicit choice-making: decide
- explicit personal planning: plan
- due, early, or deferred follow-up: review
- a request meeting `CONTEXT.md`'s `work` definition: work
- an approved canonical update or requested commit: approve, write, validate,
  and commit

## Preserve trust

- Treat explicit current statements as stronger than stored context, but
  resolve material conflicts before relying on either.
- Never convert an inference into canonical knowledge without approval.
- Propose the exact distilled change before writing. Approval applies only to
  that proposal.
- Keep raw conversations, secrets, account numbers, identity documents, and
  raw medical or financial records out of the repository.
- Use synthetic examples only when demonstrating the public project.

## Repository commands

Run these from this skill directory:

```text
python3 scripts/follow_through.py setup PATH
python3 scripts/follow_through.py connect PATH
python3 scripts/follow_through.py where
python3 scripts/follow_through.py validate [PATH]
python3 scripts/follow_through.py schema-diff [PATH]
python3 scripts/follow_through.py schema-update [PATH] --apply
```

`setup` creates a new private repository from the bundled template. `connect`
registers an existing repository after validation. Schema updates print a diff
unless `--apply` is supplied; never apply one without explicit approval.
