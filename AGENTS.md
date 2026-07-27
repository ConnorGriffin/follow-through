# Follow Through

Public Agent Skill and repository template for durable personal memory,
ADR-style decisions, plans, reviews, and outcomes.

profile: reviewed

## Repo facts

- Install: none.
- Test: `python3 -m unittest discover -s tests -v`
- Validate example: `python3 scripts/validate.py examples/maya-chen`
- Check publication boundary: `python3 scripts/privacy_check.py`
- Development server: none.
- Skill and implementation: `SKILL.md`, `references/`, `scripts/`, `assets/`
- Tests: `tests/`
- Synthetic fixture: `examples/maya-chen/`

## Hazards

- Never copy personal records or Git history from a private repository into
  this project.
- Never use real personal records as examples or test fixtures. Create
  explicitly labeled synthetic records.
- Never weaken or bypass `scripts/privacy_check.py` to make a finding pass.
- Never make bootstrap create a remote or push a user's private repository.
- Never apply a schema update without first presenting its diff for explicit
  approval.
- Keep runtime code on the Python standard library unless a dependency is
  genuinely unavoidable and approved.
- Preserve the two-commit synthetic lifecycle: its Git history is validator
  coverage for `awaiting-outcome` to `reviewed`.
