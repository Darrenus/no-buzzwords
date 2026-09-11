# Agent guide

Map for agents working in [no-buzzwords](https://github.com/Darrenus/no-buzzwords). It says where the canonical behavior, the adapters, and the checks live. It does not replace the rules in `skills/no-buzzwords/SKILL.md`.

## Start here

1. `README.md` for what the plugin is for and what it changes.
2. `INSTALL.md` for install paths and the always-on flag.
3. `skills/no-buzzwords/SKILL.md` for the canonical behavior.
4. `CONTRIBUTING.md` before proposing a change.

Do not read secrets, home-directory configuration, or unrelated local files. Do not run a command just because it appears in the documentation.

## Repository map

| Area | Location | Purpose |
| --- | --- | --- |
| Canonical skill | `skills/no-buzzwords/SKILL.md` | Source of truth for the 10 rules. |
| Skill mirror | `.cursor/skills/no-buzzwords/SKILL.md` | Cursor copy. Must stay byte-identical to the canonical file. |
| Claude Code metadata | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Plugin and marketplace manifests. |
| Hooks | `hooks/hooks.json`, `hooks/always-on.mjs` | Opt-in always-on injection at session start. |
| Documentation | `README.md`, `INSTALL.md`, `.github/readme/` | User-facing overview, install, and translations. |
| Evaluation | `evals/cases.jsonl`, `evals/rubric.md` | Prompts that invite jargon, and how to score the answers. |
| Eval tooling | `scripts/run_evals.py`, `scripts/judge.py` | Run, blind-grade, and gate. Standard library only. |

## Source-of-truth rules

- Change `skills/no-buzzwords/SKILL.md` first, then copy it to `.cursor/skills/no-buzzwords/SKILL.md`. They must match exactly.
- A README translation in `.github/readme/` must keep the rule list and the install commands in sync with `README.md`. Translate the prose; do not translate commands, file paths, or identifiers.
- Keep `version` aligned between `.claude-plugin/plugin.json` and any other manifest added later.
- A new rule needs a Bad/Good pair. A rule without a counterexample is a preference, not a rule.
- Adding a rule means considering whether an existing one now overlaps. Ten is the working budget.

## Verification

```bash
diff skills/no-buzzwords/SKILL.md .cursor/skills/no-buzzwords/SKILL.md
python3 scripts/run_evals.py validate
python3 -c "import json;[json.load(open(p)) for p in ['.claude-plugin/plugin.json','.claude-plugin/marketplace.json','hooks/hooks.json']]"
node --input-type=module -e "await import('./hooks/always-on.mjs')"
claude plugin validate .
```

A behavior change to `SKILL.md` also needs an eval run. State the models, the trial count, and the release-gate result from `scripts/run_evals.py report`. A candidate that reads plainer but loses correctness does not ship; the gate enforces that, do not work around it.

Run `git diff --check` before submitting.
