# Ubiquitous language and record schema

This file is the sole authority for the repository's vocabulary, record types,
metadata, state transitions, links, and templates.

## Vocabulary

- **Canonical:** Approved knowledge that should guide current advice.
- **Current record:** A canonical record whose status is not `superseded`,
  `abandoned`, or otherwise terminal history.
- **Distilled knowledge:** A concise finding, preference, constraint, decision,
  plan, or outcome extracted from conversation; not a transcript.
- **Evidence:** What happened or was explicitly stated. Evidence may support a
  conclusion without itself becoming a durable preference.
- **Inference:** An interpretation not explicitly confirmed by the user.
- **Locked:** Settled. Reconsideration creates a new decision; it never reopens
  the original.
- **Review:** A comparison of expected and actual results that creates an
  outcome and may propose separate canonical changes.
- **Superseded:** Replaced by an explicitly linked newer decision or plan.
- **Volatile knowledge:** Current context likely to change, such as budgets,
  health constraints, job details, active relationships, or recurring
  preferences.

## Record types

| Type | Folder | Purpose |
| --- | --- | --- |
| `profile` | `profile/` | Current identity, values, constraints, and preferences. |
| `person` | `people/` | Decision-relevant relationship context about one person. |
| `area` | `areas/` | Standing prose, goals, constraints, and preferences for a life area. |
| `work` | `work/` | An inquiry that cannot yet be one decision or plan, or genuinely fans out. |
| `decision` | `decisions/` | A choice, its rationale, consequences, and reconsideration conditions. |
| `plan` | `plans/` | Intended action with assumptions, success signals, and a reviewable result. |
| `outcome` | `outcomes/` | Append-only evidence comparing a plan's expected and actual result. |

Create no wrapper work item for a simple decision or plan. Materialize folders
only when their first real record is approved.

## Statuses

- `open`: Active and able to progress.
- `awaiting-input`: Blocked on the user's answer. For work, the inquiry cannot
  progress; for a decision, a material choice remains unresolved.
- `settled`: Approved current knowledge or a resolved inquiry.
- `awaiting-outcome`: An adopted plan is waiting for evidence or review.
- `reviewed`: A plan's final review is complete, or an outcome has been
  recorded.
- `abandoned`: Intentionally stopped without resolution; the body states why.
- `superseded`: Historical because an explicitly linked replacement exists.

## Legal states and transitions

| Type | Legal states | Transitions |
| --- | --- | --- |
| `profile` | `settled` | Create as `settled`; approved edits remain `settled`. |
| `person` | `settled` | Create as `settled`; approved edits remain `settled`. |
| `area` | `settled` | Create as `settled`; approved edits remain `settled`. |
| `work` | `open`, `awaiting-input`, `settled`, `abandoned` | Create `open`; `open` ↔ `awaiting-input`; either active state → `settled` or `abandoned`. Settling requires at least one link under **Produced**. Terminal records never reopen. |
| `decision` | `open`, `awaiting-input`, `settled`, `abandoned`, `superseded` | Create `open` while unresolved or `settled` when approved before first write; `open` ↔ `awaiting-input`; either active state → `settled` or `abandoned`; `settled` → `superseded` only with a replacement. Terminal records never reopen. |
| `plan` | `open`, `awaiting-input`, `awaiting-outcome`, `reviewed`, `abandoned`, `superseded` | Create `open` while unresolved or `awaiting-outcome` when adopted before first write; `open` ↔ `awaiting-input`; either active state → `awaiting-outcome`, `abandoned`, or `superseded`; `awaiting-outcome` → `reviewed`, `abandoned`, or `superseded`. Terminal records never reopen. |
| `outcome` | `reviewed` | Create as `reviewed`; corrections are approved edits, not state changes. |

A revived terminal work item, decision, or plan is a new record that links to
the old one.

## Frontmatter

Every record uses:

```yaml
---
type: decision
status: open
created: 2026-07-25
updated: 2026-07-25
areas: []
people: []
---
```

Rules:

- Dates use ISO `YYYY-MM-DD`.
- `areas` and `people` contain quoted relative Markdown paths.
- Use only these optional workflow fields when applicable:
  `last_confirmed`, `review_after`, `supersedes`, `superseded_by`, `upholds`,
  `plan`, and `outcomes`.
- `review_after` is allowed on plans awaiting outcome and on volatile
  `profile`, `person`, or `area` records needing reconfirmation. It is never
  allowed on work items.
- `plan` links an outcome to its plan. `outcomes` is a list of outcome links on
  a plan.
- Keep relations as standard relative Markdown paths, for example
  `"../areas/travel.md"`.

## Paths and links

- Use lowercase human-readable kebab-case filenames.
- A committed path is stable during routine work. Change it only in an approved
  structural migration that updates every inbound link and `INDEX.md` in one
  branch.
- Use standard relative Markdown links, never Obsidian-only wikilinks.
- Keep each current assertion in one canonical record. Link to it rather than
  copying it.

## Supersession

Profile, person, and area knowledge updates in place with a dated change note
when the change is material.

To replace a decision or plan, update both records in the same approved diff:

```yaml
# old record
status: superseded
superseded_by: "./replacement.md"

# replacement
status: settled
supersedes: "./original.md"
```

Use a legal current status for the replacement type; a replacement plan may be
`awaiting-outcome` rather than `settled`. If reconsideration upholds an earlier
decision, keep the earlier decision settled and link it using `upholds` from the
new settled decision.

## Index contract

`INDEX.md` contains only:

- bootstrap status;
- links plus one-line descriptions for current profile, people, and areas;
- open or awaiting-input work and decisions;
- settled decisions still relevant to future requests;
- open, awaiting-input, and awaiting-outcome plans;
- a pending-review queue.

It never duplicates rationale, detailed preferences, plan steps, or outcome
evidence. Update it in the same approved diff as every navigational state
change. If it disagrees with record files, record files win and the index must
be corrected.

## Templates

Delete unused optional fields when creating a record.

### Profile

```markdown
---
type: profile
status: settled
created: YYYY-MM-DD
updated: YYYY-MM-DD
areas: []
people: []
last_confirmed: YYYY-MM-DD
---

# <Topic>

## Current understanding

<Approved facts, values, constraints, or preferences.>

## Change notes

- YYYY-MM-DD: <Material change and why.>
```

### Person

```markdown
---
type: person
status: settled
created: YYYY-MM-DD
updated: YYYY-MM-DD
areas: []
people: []
last_confirmed: YYYY-MM-DD
---

# <Name>

## Relationship context

<Only decision-relevant, approved context.>

## Known preferences and boundaries

<Confirmed knowledge, with uncertainty stated plainly.>

## Change notes

- YYYY-MM-DD: <Material change and why.>
```

### Area

```markdown
---
type: area
status: settled
created: YYYY-MM-DD
updated: YYYY-MM-DD
areas: []
people: []
last_confirmed: YYYY-MM-DD
---

# <Area>

## Current state

<Approved standing context.>

## Goals

<Current goals.>

## Constraints and preferences

<Current constraints and preferences.>

## Change notes

- YYYY-MM-DD: <Material change and why.>
```

### Work

```markdown
---
type: work
status: open
created: YYYY-MM-DD
updated: YYYY-MM-DD
areas: []
people: []
---

# <Inquiry>

## Question

<One sentence.>

## Evidence

<Evidence gathered so far.>

## Open questions

<What remains unresolved.>

## Produced

<Relative links to resulting artifacts.>
```

### Decision

```markdown
---
type: decision
status: open
created: YYYY-MM-DD
updated: YYYY-MM-DD
areas: []
people: []
---

# <Decision>

## Question

<What must be decided?>

## Context

<Relevant current facts and constraints.>

## Alternatives considered

<Serious options and tradeoffs.>

## Decision

<The ruling once settled.>

## Rationale

<Why this option won.>

## Consequences

<What follows from the decision.>

## Reconsider when

<New evidence or changed circumstances that justify a new decision record.>
```

### Plan

```markdown
---
type: plan
status: open
created: YYYY-MM-DD
updated: YYYY-MM-DD
areas: []
people: []
outcomes: []
---

# <Plan>

## Intended result

<Observable result.>

## Constraints and assumptions

<What shapes the plan and what may prove wrong.>

## Actions

<The intended actions.>

## Success signals

<How the result will be judged.>

## Review

<When and what to review.>
```

### Outcome

```markdown
---
type: outcome
status: reviewed
created: YYYY-MM-DD
updated: YYYY-MM-DD
areas: []
people: []
plan: "../plans/example.md"
---

# <Outcome>

## Expected

<What the plan predicted.>

## Actual

<What happened.>

## Surprises

<Unexpected results.>

## Causes and evidence

<Best current explanation, with uncertainty.>

## Proposed learnings

<Possible durable updates. These are not canonical until separately approved.>
```
