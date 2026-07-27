# Quickstart

Requirements: Git, Python 3.10 or newer, and either Claude Code or Codex.

## 1. Clone the public skill

```sh
git clone https://github.com/ConnorGriffin/follow-through.git
cd follow-through
```

Do not store personal records in this public clone.

## 2. Install it for your agents

From the public clone:

```sh
mkdir -p ~/.agents/skills ~/.claude/skills
ln -s "$PWD" ~/.agents/skills/follow-through
ln -s "$PWD" ~/.claude/skills/follow-through
```

Codex loads user skills from `~/.agents/skills`; Claude Code loads them from
`~/.claude/skills`. Both links point to the same source.

If either destination already exists, inspect it before replacing anything.

## 3. Create your private records repository

Choose any private location:

```sh
python3 scripts/follow_through.py setup ~/Code/my-follow-through
```

The command:

- copies the repository template;
- initializes a local Git repository on `main`;
- saves its absolute path in `~/.config/follow-through/config.json`;
- creates no remote and pushes nothing.

To use an existing compatible repository instead:

```sh
python3 scripts/follow_through.py connect /path/to/private-repository
```

Pass `--replace` only when intentionally changing an existing configuration.
Set `FOLLOW_THROUGH_HOME` to override the configured path temporarily.

## 4. Verify

```sh
python3 scripts/follow_through.py where
python3 scripts/follow_through.py validate
```

Then start a new agent session and say:

```text
Use $follow-through to bootstrap my personal context.
```

The bootstrap is intentionally incomplete. Start with identity, values,
constraints, key people, and active life areas; deepen it through real
decisions and reviews.

## Back up privately

The generated repository has no remote. If you add one, make it private and
review the complete history before the first push. Follow Through never creates
or pushes that remote for you.
