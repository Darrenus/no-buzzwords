# Install

## Claude Code (plugin)

```bash
claude plugin marketplace add Darrenus/no-buzzwords
claude plugin install no-buzzwords@no-buzzwords
```

Verify:

```bash
claude plugin list
```

Start a session and type `/no-buzzwords`. It applies until you say "stop no-buzzwords" or "normal mode".

### Update

```bash
claude plugin marketplace update no-buzzwords
```

### Uninstall

```bash
claude plugin uninstall no-buzzwords
claude plugin marketplace remove no-buzzwords
```

Or keep it and turn it off: `claude plugin disable no-buzzwords`.

## Claude Code (manual, no marketplace)

Copy the skill into your skills directory:

```bash
mkdir -p ~/.claude/skills
curl -fsSL https://raw.githubusercontent.com/Darrenus/no-buzzwords/main/skills/no-buzzwords/SKILL.md \
  -o ~/.claude/skills/no-buzzwords.md
```

Per project instead of per user: put the same file at `.claude/skills/no-buzzwords/SKILL.md` in the repo.

## Always-on

The skill sets `disable-model-invocation: true`, so the model never turns it on by itself. You do, with `/no-buzzwords`.

To have it on from message one of every session, create the opt-in flag:

```bash
touch ~/.claude/.no-buzzwords-always
```

The `SessionStart` hook in `hooks/hooks.json` checks for that file and injects the ruleset when it exists. No flag, no injection. The hook exits 0 on any error, so it can never block a session from starting.

Turn always-on off:

```bash
rm ~/.claude/.no-buzzwords-always
```

## Cursor

`.cursor/skills/no-buzzwords/SKILL.md` in this repo is a copy of the canonical skill. Drop it into your project or into `~/.cursor/skills/`:

```bash
mkdir -p ~/.cursor/skills/no-buzzwords
curl -fsSL https://raw.githubusercontent.com/Darrenus/no-buzzwords/main/.cursor/skills/no-buzzwords/SKILL.md \
  -o ~/.cursor/skills/no-buzzwords/SKILL.md
```

## Any other assistant

The skill body is plain Markdown with no runtime dependencies. Paste everything below the frontmatter into whatever the tool calls its system prompt, custom instructions, or rules file. Nothing in the rules assumes a particular harness.
