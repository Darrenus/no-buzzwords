<p align="center">
  <strong>Plain technical answers. Keep the terms that do work, drop the ones that don't.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/Darrenus/no-buzzwords?style=flat" alt="License"></a>
</p>

## What it does

A skill for your coding assistant that stops it from dressing up an explanation. It says what actually happens instead of naming the pattern, uses `use` instead of `leverage`, and replaces "robust and scalable" with a number.

It is not a brevity plugin. A plain explanation is often longer than a jargon one, because it does the work the jargon skipped.

## What changes

<table>
<tr>
<td width="50%">

### Before

> The service employs an event-driven architecture that leverages a message broker to facilitate loose coupling between bounded contexts. This yields a robust, horizontally scalable topology with minimal operational overhead. The consumer should be designed to be idempotent to mitigate at-least-once delivery semantics.

</td>
<td width="50%">

### After

> When an order is placed, the API writes a row to a RabbitMQ queue. The shipping service reads that queue on its own schedule. Neither service calls the other, so either one can be down for a while without breaking the other.
>
> RabbitMQ may hand you the same message twice, so the shipping service has to be idempotent: running it twice has to do the same thing as running it once. In practice, key the write on `order_id` so the second run overwrites instead of inserting.
>
> One worker handles about 2,000 messages a minute. Past that, add workers.

</td>
</tr>
</table>

The second version is longer. It is also the only one you could act on.

## The rules

10 rules. Full text in [SKILL.md](./skills/no-buzzwords/SKILL.md).

1. Say the mechanism, not the category.
2. One plain verb instead of one impressive verb.
3. Cut any adjective nobody would claim the opposite of.
4. Turn noun phrases back into verbs.
5. Gloss a term on first use, once.
6. Follow every abstract claim with one concrete case.
7. Keep the precise term when precision is the point.
8. A metaphor comes after the mechanism, never instead of it.
9. Name the thing, not the category it belongs to.
10. Do not use jargon to cover not knowing.

## The test that drives all of them

> Could a competent engineer who has never seen this subsystem restate your explanation in their own words and get it right?

If not, the sentence is not plain yet.

## Install

```bash
claude plugin marketplace add Darrenus/no-buzzwords
claude plugin install no-buzzwords@no-buzzwords
```

Then type `/no-buzzwords` in a session. It stays on until you say "stop no-buzzwords".

Other runtimes and the manual copy route: [INSTALL.md](INSTALL.md).

## Always-on (optional)

The skill is opt-in by default, the same way a style choice should be. To have it apply from the first message of every session:

```bash
touch ~/.claude/.no-buzzwords-always
```

Delete that file to go back to opt-in.

## What it does not do

- It does not ban technical terms. `idempotent`, `race condition`, and `TCP handshake` are the exact names of specific things; rule 5 makes the assistant pay for them once instead of dropping them.
- It does not rename identifiers. A function called `serialize` is still called `serialize`.
- It does not simplify text where precision carries liability: license clauses, dosages, security boundaries.
- It does not shorten answers. That is a different problem, and [i-have-adhd](https://github.com/ayghri/i-have-adhd) already solves it. The two stack.

## Credits

Structure and packaging follow [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd), which does the same thing for response shape. The rules here are about word choice and level of abstraction.

## License

MIT
