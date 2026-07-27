# Follow Through operating contract

This private repository is your durable personal context. Preserve trust:
retrieve narrowly, distinguish evidence from inference, and never make
unapproved knowledge canonical.

## Authority

- Your explicit current statement is authoritative, subject to resolving
  any material conflict it creates.
- Current record files hold canonical knowledge.
- `CONTEXT.md` solely owns artifact definitions, metadata, states,
  transitions, templates, and supersession rules.
- `INDEX.md` is navigation, not a second knowledge store. If it disagrees with
  record files, the records win and the index needs correction.
- Apply `CONTEXT.md` when determining whether a record is current or
  historical.

## Before advising

1. Read `INDEX.md`.
2. On the first Follow Through task in a conversation, scan for overdue plan
   reviews and relevant open work. Surface them briefly without forcing the
   user to handle them.
3. Search relevant terms, areas, people, decisions, plans, and outcomes. Read
   only the records needed for the request.
4. Briefly state which stored context materially informed the response.
5. If current records conflict materially, show both and ask which is current;
   do not automatically trust the newer file.
6. If a request conflicts with a settled decision, cite it and ask whether
   evidence or circumstances changed.

## Change protocol

- Store approved, distilled knowledge. Do not archive raw conversations by
  default.
- Draft the exact change and show a concise proposed diff before writing.
  Approval applies only to that proposal; changed proposals require approval
  again.
- Never make an inference canonical without confirmation.
- Update `INDEX.md` in the same approved diff whenever its `CONTEXT.md`
  contract requires it.
- Apply all `CONTEXT.md` path, link, lifecycle, date, and supersession rules.
  Structural migrations use a branch.
- For ordinary approved knowledge changes, commit directly to `main`. Stage
  explicit paths only; never use `git add .`, `git add -A`, or `git stash`.
- Use one plain-language commit per coherent approved change, then push to the
  private `origin` remote unless the user asks to keep it local.

## Privacy and redaction

- Never store credentials, recovery codes, account numbers, identity
  documents, or raw medical or financial records. Store only decision-relevant
  summaries.
- Before commit, remove prohibited data from the proposed files and show the
  corrected diff.
- If prohibited data is already committed, stop. Do not push it. Identify the
  affected path and commit, recommend revoking any exposed credential, and ask
  before rewriting history.
- If it was already pushed, treat it as an incident: stop normal work, identify
  the exposure, rotate revocable secrets, and get explicit approval before any
  destructive history rewrite or force-push.
