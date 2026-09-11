# Evals

`cases.jsonl` holds prompts that invite inflated language. Each one names the rule it exercises, in `category`.

The point is not to prove the skill makes answers plainer. That is easy and not worth measuring. The point is to catch the two ways it can go wrong:

- **Plainer but wrong.** `correctness` carries 35% of the weight, and the release gate fails the candidate if correctness drops more than 0.1 below baseline, even when the weighted score went up.
- **Overcorrection.** Two cases exist only for this. `expert-register` fails if the assistant explains CQRS to someone who just used the word. `precision-liability` fails if it softens an AGPL clause to make it readable.

## Setup

```bash
cp evals/runners.example.json evals/runners.json
```

A runner entry is a command plus optional stdin. Two placeholders get substituted:

- `{prompt}` — the case prompt
- `{skill}` — `skills/no-buzzwords/SKILL.md` with its frontmatter stripped

Every entry except `judge` is treated as a condition to compare. The example config uses the `claude` CLI, but nothing depends on it; any command that reads a prompt and writes an answer works.

## Run

```bash
python3 scripts/run_evals.py validate          # cases and rubric; no model calls, no credentials
python3 scripts/run_evals.py run --trials 3    # -> evals/out/responses.jsonl
python3 scripts/run_evals.py judge             # -> evals/out/scores.jsonl
python3 scripts/run_evals.py report            # weighted scores and the release gate
```

`report` exits non-zero when the gate fails, so it can front a release script.

## How blind grading works

For each case and trial, the responses are shuffled and relabelled `A`, `B`, `C...`. The shuffle is seeded on the case id, so it is reproducible but differs from case to case; a judge that always favors `A` shows up as noise rather than as a win for one condition. The judge sees only the rubric block between the `judge:begin` and `judge:end` markers, the question, the case criteria, and the labelled responses. Condition names never reach it.

Change `--seed` to re-blind an existing response set without regenerating it.

## Case format

```json
{"id": "...", "category": "...", "prompt": "...", "risk": "low|medium|high", "criteria": ["...", "..."]}
```

`validate` rejects a duplicate id, a missing field, an unknown risk level, or an empty criteria list. It also fails if the rubric weights stop summing to 100%, which is the usual way a rubric edit breaks silently.
