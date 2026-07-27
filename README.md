# Follow Through

Durable personal memory for decisions, plans, and what happened next.

AI memory and the decision journal solve different halves of the same problem.
Memory gives an assistant the context to advise you. A decision journal
preserves what you believed before hindsight rewrites it. Follow Through joins
them: your AI can remember the life around a plan, return when evidence exists,
compare expected with actual, and record the outcome without pretending one
event proves a universal rule.

I built the original version around a private repository I use for real personal
decisions and plans. That repository cannot be published. This project contains
the mechanism, a clean template, and an explicitly synthetic example instead.

## The loop

```text
personal context → decision → plan → outcome review → approved learning
       ↑                                                   │
       └───────────────────────────────────────────────────┘
```

Follow Through stores plain Markdown in a private Git repository:

- current facts, constraints, preferences, people, and life areas;
- ADR-style decisions with alternatives, rationale, and reconsideration
  conditions;
- plans with assumptions, observable success signals, and review dates;
- append-only outcomes comparing predictions with evidence;
- a human approval boundary before an inference becomes durable context.

It is an [Agent Skill](https://agentskills.io) for Claude Code and Codex. It has
no service, database, account, model API, or runtime dependency beyond Python
and Git.

## The example that matters

The fictional example does not make every plan succeed.

[Maya predicts](examples/maya-chen/plans/test-four-day-workweek.md) that
protecting Friday will increase deep-work output by 25 percent. The
[completed review](examples/maya-chen/outcomes/four-day-workweek-trial.md)
records that output barely changed, Thursday became more tiring, and the trial
should end. It also declines to generalize from one schedule experiment into a
permanent belief about four-day weeks.

That distinction is the point: preserve the prediction, record the result, and
keep evidence separate from the story you are tempted to tell afterward.

Every person and event under [`examples/`](examples/) is synthetic.

## Start

Follow [QUICKSTART.md](QUICKSTART.md) to install the skill and create a private
records repository in under ten minutes.

Once configured:

- ask ordinary personal questions and let the skill retrieve only relevant
  context;
- say “help me decide” to create a decision record;
- say “help me plan” to record assumptions, actions, and review criteria;
- say “review my due plans” to compare predictions with outcomes;
- run `python3 scripts/follow_through.py validate` to verify the repository.

## Validation

The stdlib-only validator checks:

- required frontmatter and legal status for each record type;
- legal status transitions across Git history;
- dates, paths, typed relations, reciprocal outcome and supersession links;
- all local Markdown links;
- whether `INDEX.md` matches current records on disk.

CI runs the validator against the synthetic repository and exercises failure
cases for broken links, invalid states, index drift, and illegal history.

## Privacy model

The public project and private records repository are separate.

- Bootstrap creates a new Git repository with no remote.
- Connecting an existing repository copies nothing into this project.
- No command creates a GitHub repository or pushes personal records.
- The workflow stores distilled, approved context—not chat transcripts,
  credentials, account numbers, identity documents, or raw medical or
  financial records.
- Public examples must be synthetic, never redacted personal records.

Read diffs before committing personal context. A Git repository preserves
deleted content in history; deleting a file does not erase an exposure.

## Project structure

```text
SKILL.md                         Agent workflow
references/workflows.md         Detailed record workflows
assets/repository-template/     Private-repository scaffold
scripts/follow_through.py       Setup, discovery, validation, schema updates
scripts/validate.py             Record and history validator
examples/maya-chen/             Fully synthetic worked example
tests/                          Stdlib test suite
```

## Prior art

Follow Through builds on several traditions rather than claiming to invent
durable memory or written decisions:

- [MADR / Any Decision Records](https://adr.github.io/madr/) for concise,
  versioned decisions with context and consequences;
- [Farnam Street's decision journal](https://fs.blog/decision-journal/) for
  recording expectations before hindsight changes the story;
- [DiffMem](https://github.com/Growth-Kinetics/DiffMem) for plain Markdown and
  Git as inspectable agent memory;
- [Letta](https://github.com/letta-ai/letta) for the broader work on stateful
  agents with long-term memory;
- [Daniel Rosehill's Personal AI Resources](https://github.com/danielrosehill/Personal-AI-Resources)
  for mapping the personal-AI and context-engineering ecosystem.

The narrower contribution here is the review boundary: personal memory feeds a
decision and plan, an outcome later tests the prediction, and only separately
approved learning changes durable context.

## License

MIT. See [LICENSE](LICENSE).

If Follow Through proves useful, you can [sponsor its maintenance](https://github.com/sponsors/ConnorGriffin).
