# Scoring rubric

<!-- judge:begin -->
Judge responses blind. Label them `A`, `B`, or `C`; do not reveal which condition produced which. Score each dimension 1 (fails) to 5 (excellent).

| Dimension | Weight | What to measure |
| --- | ---: | --- |
| Correctness | 35% | Technically accurate. Plain wording did not change or lose the meaning. |
| Groundedness | 25% | Abstract claims are followed by a concrete case: a number, a file, an identifier, a worked example. |
| Term discipline | 20% | Load-bearing terms are kept and glossed once. Decorative terms are gone. Identifiers are never renamed. |
| Actionability | 10% | The reader could restate the explanation in their own words and be right. |
| Restraint | 10% | No praise adjectives, no metaphor standing in for a mechanism, no jargon covering a guess. |

Mark `blocker: true` when a response: replaces a precise term with a vague phrase and loses meaning, renames a real identifier, simplifies text where precision carries liability, or states a guess as an abstract fact.
<!-- judge:end -->

Ship the candidate only when:

1. No blocking findings.
2. Correctness is within 0.1 points of baseline or better. A plain answer that is now wrong is a regression, not a win.
3. Weighted score beats baseline.
4. Same cases, models, and trials as the baseline run.
