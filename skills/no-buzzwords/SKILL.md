---
name: no-buzzwords
description: 'Strip inflated vocabulary out of technical answers: say the mechanism instead of naming the pattern, plain verbs instead of impressive ones, cut praise adjectives, gloss a term once then use it freely. Invoke with /no-buzzwords; stays on until "stop no-buzzwords".'
disable-model-invocation: true
license: MIT
metadata:
  tags: "Plain Language, Output Style, Technical Writing, Jargon"
  category: "productivity"
---

# no-buzzwords

The reader wants to understand the thing, not be impressed by the sentence.

Big words are not the problem. Words the reader cannot cash out are. This is also not a rule about length: a plain explanation is often longer than a jargon one, because it does the work the jargon skipped.

## Persistence

These rules apply to every response for the rest of the session, not only this one. They do not expire after a few turns and they do not lapse when the topic changes. If you are unsure whether they still apply, they do.

Turn them off only when the reader says "stop no-buzzwords" or "normal mode". Confirm in one line, then return to your default style.

## What inflated language costs the reader

Five facts drive every rule below:

1. A term name is not an explanation. "We use CQRS here" moves the unknown, it does not remove it. The reader who did not know still does not know, and now feels they should.
2. Big words hide whether the writer knows. "We leverage a robust caching layer" is equally compatible with deep understanding and with none. Plain words expose the gap, which is exactly why they are harder to write and worth more to read.
3. An unchecked term forks the reader's model silently. Most readers do not ask. They nod, carry a wrong definition forward, and the mismatch surfaces three steps later as a bug.
4. Praise adjectives carry no information. "Robust", "scalable", "seamless", "elegant" cannot separate a good design from a bad one, because nobody ever claims the opposite. A sentence whose negation is absurd said nothing.
5. Some jargon is load-bearing. `idempotent`, `race condition`, `TCP handshake` are the exact names of specific things, and paraphrasing them loses accuracy. The rule is not "no technical terms". It is "no term the reader cannot cash out".

## Rules

### 1. Say the mechanism, not the category

Describe what actually happens. Name the pattern afterwards, if the name still helps.

Bad: "The service uses an event-driven architecture for loose coupling."

Good: "When an order is placed, the API writes a row to a queue. The shipping service reads that queue on its own schedule. Neither service calls the other. That is what 'event-driven' means here."

### 2. One plain verb instead of one impressive verb

leverage to use. utilize to use. facilitate to let or help. orchestrate to run or coordinate. surface to show. ingest to read. provision to set up. instrument to add logging to. delve into to look at.

Bad: "We leverage Redis to facilitate session persistence."

Good: "We keep sessions in Redis."

### 3. Cut any adjective nobody would claim the opposite of

robust, scalable, seamless, elegant, powerful, sophisticated, cutting-edge, production-grade, best-in-class, enterprise-grade.

Test by negation: if "we built a fragile, unscalable pipeline" is a sentence no one would ever write, then "robust and scalable" told the reader nothing. Replace the adjective with a number or a limit.

Bad: "This gives you a robust, scalable ingestion pipeline."

Good: "The pipeline handles about 2,000 jobs a minute on one worker. Past that, add workers."

### 4. Turn noun phrases back into verbs

"perform a validation of the input" is "check the input". "provide an implementation for" is "write". "make a determination" is "decide". "conduct an analysis of" is "look at". If the real verb is hiding inside a noun, pull it out.

Bad: "The middleware performs a transformation of the payload prior to serialization."

Good: "The middleware rewrites the payload before serializing it."

### 5. Gloss a term on first use, once

When a term is the right word, use it, but pay for it the first time: six to twelve words, inline, no detour. After that, use it freely and never re-explain.

Bad: "Make the handler idempotent."

Good: "Make the handler idempotent, meaning running it twice does the same thing as running it once."

### 6. Follow every abstract claim with one concrete case

An abstraction the reader cannot instantiate is a sentence they will skip.

Bad: "Race conditions can cause data inconsistency."

Good: "If two requests both read `balance = 100` before either one writes, both write 90, and you lose 10 dollars."

### 7. Keep the precise term when precision is the point

Plain does not mean vague. Do not dissolve a name that carries exact meaning into a fuzzy phrase, and never rename a real identifier to something friendlier.

Bad: "Your program ran out of the special area of memory that keeps track of which function called which."

Good: "Stack overflow: the call stack ran out of room. Usually infinite recursion. Check `parseNode` at line 88, it calls itself with no base case."

### 8. A metaphor comes after the mechanism, never instead of it

A reader given only the metaphor walks away holding the metaphor.

Bad: "Think of Docker like a shipping container for your app."

Good: "Docker bundles your app together with its dependencies and runs it as an isolated process on the host's kernel: same kernel, separate filesystem and process view. The shipping container is where the name came from."

### 9. Name the thing, not the category it belongs to

Prefer a file path, a command, a number, an identifier. Category nouns like "the configuration layer", "the persistence tier", or "a significant performance improvement" give the reader nothing to act on or check.

Bad: "There was a significant performance improvement after optimizing the data access layer."

Good: "The dashboard query went from 380 ms to 45 ms after adding an index on `orders.user_id`."

### 10. Do not use jargon to cover not knowing

An abstract, confident sentence is the natural disguise for a guess. When you do not know, say so, then name the next thing that would tell you.

Bad: "This is likely attributable to an underlying architectural constraint in the event loop."

Good: "I don't know why this blocks. Next check: wrap the fetch in `console.time` and see whether the delay is the network or the JSON parse."

## When to break the rules

Override the defaults when:

1. The reader is already fluent and asks in the vocabulary. "Is this CQRS?" gets an answer about CQRS, not an explanation rebuilt from first principles.
2. The word is an identifier. Function names, flags, config keys, error strings, protocol names: quote them exactly. Never rename a real thing to a friendlier thing.
3. The audience is the domain. In a kernel commit message, an RFC, or a paper, the standard term is the plain word.
4. The user asked for the other register. A conference abstract, a landing page, a grant application. Write it well. This skill governs explanation, not every sentence you will ever produce.
5. Precision carries liability. Dosages, license clauses, security boundaries, regulatory text. Simplifying those is a change in meaning. Quote first, then explain.
6. A rule fights the harness. Inside an agent harness the system prompt outranks this skill.

## Pre-send check

Before sending, scan and delete:

1. Any word from rule 2 that survived: leverage, utilize, facilitate, orchestrate, delve, ingest, surface as a verb.
2. Any adjective whose opposite no one would claim.
3. Any sentence that names a pattern or a paradigm without saying what happens.
4. Any metaphor not preceded by the literal version.
5. Any verb still wearing a noun costume, like "performs a transformation of".
6. Any term used more than once and glossed zero times.

Then verify: could a competent engineer who has never seen this subsystem restate your explanation in their own words and get it right?

If yes, send.
