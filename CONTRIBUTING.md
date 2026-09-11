# Contributing

## Changing a rule

`skills/no-buzzwords/SKILL.md` is the only place behavior is defined. Everything else is packaging.

A rule change needs three things in the pull request:

1. The Bad/Good pair. If you cannot write a realistic sentence the rule rejects, the rule is a preference.
2. The case it fixes, added to `evals/cases.jsonl`.
3. A note on what it overlaps with. Ten rules is the budget. A new rule usually means an old one should absorb it or retire.

After editing the canonical file:

```bash
cp skills/no-buzzwords/SKILL.md .cursor/skills/no-buzzwords/SKILL.md
```

The two files must be byte-identical.

## What gets rejected

- A rule that bans a word without saying what replaces it.
- A rule that makes the assistant vaguer. Plain is not the same as fuzzy; rule 7 exists to hold that line.
- A longer word list with no test behind it. Rule 3's negation test is the pattern to follow.
- Rules about response length or structure. That is [i-have-adhd](https://github.com/ayghri/i-have-adhd)'s territory and the two are meant to stack, not overlap.

## Checks

```bash
diff skills/no-buzzwords/SKILL.md .cursor/skills/no-buzzwords/SKILL.md
python3 -c "import json;[json.load(open(p)) for p in ['.claude-plugin/plugin.json','.claude-plugin/marketplace.json','hooks/hooks.json']]"
claude plugin validate .
```
