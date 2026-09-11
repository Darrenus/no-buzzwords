# Evals

`cases.jsonl` holds prompts that invite inflated language. Each one names a rule it is meant to exercise, in `category`.

Run the same prompts through a baseline session and a session with `/no-buzzwords` active, then score both blind against `rubric.md`.

The point of the rubric is the Correctness weight. It is easy to write an answer that scores well on plainness by being vaguer, and that is a regression. A candidate whose Correctness drops does not ship, however plain it reads.

Two cases (`expert-register`, `precision-liability`) exist to catch overcorrection. If the skill starts explaining CQRS to someone who used the word, or softening a license clause, those fire first.

Case format:

```json
{"id": "...", "category": "...", "prompt": "...", "risk": "low|medium|high", "criteria": ["...", "..."]}
```
