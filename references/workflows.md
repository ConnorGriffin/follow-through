# Workflows

The repository's `CONTEXT.md` owns all schemas and state transitions. Read it
before proposing or changing records.

## Retrieve

1. Read `INDEX.md`.
2. Search relevant terms and linked areas or people with `rg`.
3. Use `CONTEXT.md` to identify current records. Open historical records only
   for provenance.
4. If two current records conflict materially, show both and ask which is
   current. Do not prefer the newer file automatically.
5. If the request conflicts with a settled decision, cite it and ask whether
   evidence or circumstances changed.
6. Answer from the smallest relevant context set and name that context briefly.
7. If durable knowledge emerged, propose a distilled update; otherwise leave
   the repository unchanged.

## Bootstrap

Build a minimum useful foundation, not a comprehensive biography.

1. If no repository is configured, ask for its intended path, then run
   `python3 scripts/follow_through.py setup PATH` from the skill directory.
2. Cover identity, values, constraints, key people, recurring preferences, and
   active life areas.
3. Ask one question at a time.
4. Mark uncertainty instead of filling gaps by inference.
5. Batch proposed records by topic.
6. At each topic checkpoint, show one concise proposed diff and wait for
   approval.
7. Commit approved batches directly to `main` using the repository's change
   protocol.
8. Leave bootstrap explicitly incomplete. Deepen the model through real use.

## Decide

1. Search related profile, area, people, and decision records.
2. State existing constraints and any conflict with a settled decision.
3. Resolve one ambiguity at a time. Use a grilling workflow when available.
4. Draft the decision using the repository template.
5. Follow `CONTEXT.md`'s reconsideration and linking rules.
6. Propose the record and every required index or supersession edit together.
7. Write only after approval.

## Plan

1. Search relevant preferences, people, areas, prior decisions, plans, and
   outcomes.
2. Draft the plan using the repository template.
3. Keep the plan unresolved while material questions remain.
4. When the user adopts it, apply the legal adopted-plan state from
   `CONTEXT.md` and record a useful review date when one is known.
5. Propose the plan and index update before writing.

## Review

Support due, overdue, early, and deferred reviews.

1. Use `CONTEXT.md` to identify plans eligible for outcome review, ordered by
   overdue, due, then future.
2. Allow the user to select any plan early; the date is a prompt, not a gate.
3. To defer, propose only the revised review date and necessary timestamp
   update.
4. During review, ask one question at a time about expected versus actual,
   surprises, causes, and evidence.
5. Ask whether a finding is specific to this event or generally true before
   proposing a durable preference.
6. Draft an outcome record first. Keep any proposed profile, area, or decision
   changes separate so one experience does not silently become a general rule.
7. Link the outcome and apply the final-review transition only when the user
   says the review is final. Otherwise keep the review pending and choose
   another date.
8. Propose all changes together and write only after approval.

## Work

Create a work item only when the request meets `CONTEXT.md`'s `work`
definition.

1. Use the work template in `CONTEXT.md`.
2. If the request is intended action with an outcome, route it to plan.
3. Keep evidence in the work item while investigating. When it produces a
   decision, move decision-relevant reasoning into that decision and leave only
   a pointer in the work item.
4. Apply a terminal transition only after the requirements in `CONTEXT.md` are
   met.
5. If it ultimately produces one decision or plan, propose folding the useful
   content into that artifact and removing the redundant work file.
6. Apply the repository's current-versus-historical retrieval rules.

## Approve, write, and commit

1. Distill findings into exact target files.
2. Show the proposed diff before writing.
3. Wait for explicit approval. If the proposal changes, show it again.
4. Apply the approved files and update `INDEX.md` when its contract requires.
5. Validate the change against `AGENTS.md` and `CONTEXT.md` by running
   `python3 scripts/follow_through.py validate` from the skill directory.
6. Inspect `git status` and the diff.
7. Follow the repository's staging, commit, and push rules.
