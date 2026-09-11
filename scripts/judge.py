#!/usr/bin/env python3
"""Blind grading for the no-buzzwords evals.

The judge never learns which runner produced which response. Responses for one
case are shuffled and relabelled A, B, C..., and only the rubric block between
the judge:begin and judge:end markers is sent along with them.

Standard library only, so `validate` runs in CI without installing anything.
"""

from __future__ import annotations

import json
import random
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUBRIC = REPO / "evals" / "rubric.md"

JUDGE_BLOCK = re.compile(r"<!--\s*judge:begin\s*-->(.*?)<!--\s*judge:end\s*-->", re.S)
# Table rows look like: | Correctness | 35% | what to measure |
WEIGHT_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d+)%\s*\|", re.M)


def dimension_key(label: str) -> str:
    return label.strip().lower().replace(" ", "_")


def load_rubric(path: Path = RUBRIC) -> tuple[str, dict[str, float]]:
    """Return the text the judge sees and the dimension weights, as fractions."""
    text = path.read_text(encoding="utf-8")
    match = JUDGE_BLOCK.search(text)
    if not match:
        raise ValueError(f"{path} has no judge:begin / judge:end block")

    block = match.group(1).strip()
    if not block:
        raise ValueError(f"{path} judge block is empty")

    weights = {
        dimension_key(label): int(pct) / 100
        for label, pct in WEIGHT_ROW.findall(block)
        if dimension_key(label) not in {"dimension", "---"}
    }
    if not weights:
        raise ValueError(f"{path} judge block has no weight rows")

    total = round(sum(weights.values()), 6)
    if total != 1.0:
        raise ValueError(f"{path} weights sum to {total * 100:.0f}%, expected 100%")

    return block, weights


def build_prompt(case: dict, labelled: dict[str, str], rubric_block: str, weights: dict) -> str:
    """Assemble the grading prompt. Condition names never appear in it."""
    dims = ", ".join(sorted(weights))
    responses = "\n\n".join(
        f"### Response {label}\n\n{text.strip()}" for label, text in sorted(labelled.items())
    )
    criteria = "\n".join(f"- {c}" for c in case["criteria"])

    return f"""You are grading answers to one technical question. Grade blind: you are not told which system produced which response, and you must not guess.

## Rubric

{rubric_block}

## The question that was asked

{case["prompt"]}

## Case-specific criteria

{criteria}

## Responses

{responses}

## Output

Reply with one JSON object and nothing else. No prose, no code fence.

{{
  "scores": {{"<label>": {{{", ".join(f'"{d}": <1-5>' for d in sorted(weights))}}}}},
  "blocker": {{"<label>": true or false}},
  "note": {{"<label>": "<one sentence, the single strongest observation>"}}
}}

Include every label that appears above: {", ".join(sorted(labelled))}.
Dimensions, exactly these keys: {dims}.
Set blocker to true only for the conditions the rubric names as blocking."""


def shuffle_labels(case_id: str, by_condition: dict[str, str], seed: int) -> tuple[dict, dict]:
    """Label responses A, B, C... in an order that depends on the case, not the runner."""
    conditions = sorted(by_condition)
    rng = random.Random(f"{seed}:{case_id}")
    rng.shuffle(conditions)
    labels = [chr(ord("A") + i) for i in range(len(conditions))]
    label_to_condition = dict(zip(labels, conditions))
    labelled = {label: by_condition[cond] for label, cond in label_to_condition.items()}
    return labelled, label_to_condition


def run_judge(runner: dict, prompt: str, timeout: int) -> dict:
    """Invoke the judge command and parse its JSON reply."""
    cmd = [part.replace("{prompt}", prompt) for part in runner["cmd"]]
    stdin = runner.get("stdin", "").replace("{prompt}", prompt) or None

    proc = subprocess.run(
        cmd,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"judge exited {proc.returncode}: {proc.stderr.strip()[:400]}")

    return parse_json_reply(proc.stdout)


def parse_json_reply(raw: str) -> dict:
    """Accept a bare JSON object, or one wrapped in a code fence."""
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"judge returned no JSON object: {raw.strip()[:200]}")
        text = text[start : end + 1]
    return json.loads(text)


def weighted(scores: dict, weights: dict[str, float]) -> float:
    """Weighted mean over the rubric dimensions. Missing dimension is a hard error."""
    missing = set(weights) - set(scores)
    if missing:
        raise ValueError(f"judge omitted dimensions: {sorted(missing)}")
    return round(sum(scores[d] * w for d, w in weights.items()), 4)
