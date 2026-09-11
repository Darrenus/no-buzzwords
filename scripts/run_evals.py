#!/usr/bin/env python3
"""Run, grade, and report the no-buzzwords evals.

    python3 scripts/run_evals.py validate            # check cases and rubric, no model calls
    python3 scripts/run_evals.py run --trials 3      # generate responses for every runner
    python3 scripts/run_evals.py judge               # blind-grade what run produced
    python3 scripts/run_evals.py report              # weighted scores and the release gate

`validate` is standard library only and needs no credentials, so CI runs it on
every push. The other three shell out to whatever `evals/runners.json` names.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge as judging  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
CASES = REPO / "evals" / "cases.jsonl"
SKILL = REPO / "skills" / "no-buzzwords" / "SKILL.md"
OUT = REPO / "evals" / "out"
RESPONSES = OUT / "responses.jsonl"
SCORES = OUT / "scores.jsonl"
DEFAULT_RUNNERS = REPO / "evals" / "runners.json"

REQUIRED_FIELDS = {"id", "category", "prompt", "risk", "criteria"}
VALID_RISK = {"low", "medium", "high"}
FRONTMATTER = re.compile(r"^---[^\S\r\n]*\r?\n.*?\r?\n---[^\S\r\n]*(?:\r?\n|$)", re.S)


# --- loading ----------------------------------------------------------------


def load_cases(path: Path = CASES) -> list[dict]:
    cases, seen = [], set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{lineno} is not valid JSON: {exc}") from exc

        missing = REQUIRED_FIELDS - set(case)
        if missing:
            raise ValueError(f"{path.name}:{lineno} is missing {sorted(missing)}")
        if case["risk"] not in VALID_RISK:
            raise ValueError(f"{path.name}:{lineno} risk must be one of {sorted(VALID_RISK)}")
        if not isinstance(case["criteria"], list) or not case["criteria"]:
            raise ValueError(f"{path.name}:{lineno} needs a non-empty criteria list")
        if case["id"] in seen:
            raise ValueError(f"{path.name}:{lineno} duplicate case id {case['id']!r}")

        seen.add(case["id"])
        cases.append(case)

    if not cases:
        raise ValueError(f"{path} has no cases")
    return cases


def load_runners(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(
            f"No runner config at {path.relative_to(REPO)}.\n"
            f"Start from the example:\n"
            f"  cp evals/runners.example.json evals/runners.json"
        )
    runners = json.loads(path.read_text(encoding="utf-8"))
    for name, cfg in runners.items():
        if not isinstance(cfg.get("cmd"), list) or not cfg["cmd"]:
            raise ValueError(f"runner {name!r} needs a non-empty cmd list")
    return runners


def skill_body() -> str:
    """SKILL.md with the YAML frontmatter removed."""
    return FRONTMATTER.sub("", SKILL.read_text(encoding="utf-8")).strip()


def invoke(cfg: dict, substitutions: dict[str, str], timeout: int) -> str:
    def fill(text: str) -> str:
        for key, value in substitutions.items():
            text = text.replace("{" + key + "}", value)
        return text

    cmd = [fill(part) for part in cfg["cmd"]]
    stdin = fill(cfg["stdin"]) if cfg.get("stdin") else None

    proc = subprocess.run(
        cmd, input=stdin, capture_output=True, text=True, timeout=timeout, cwd=REPO
    )
    if proc.returncode != 0:
        raise RuntimeError(f"exited {proc.returncode}: {proc.stderr.strip()[:400]}")
    return proc.stdout.strip()


# --- subcommands ------------------------------------------------------------


def cmd_validate(args) -> int:
    cases = load_cases()
    block, weights = judging.load_rubric()

    by_category = defaultdict(int)
    for case in cases:
        by_category[case["category"]] += 1

    print(f"{len(cases)} cases across {len(by_category)} categories")
    for category, count in sorted(by_category.items()):
        print(f"  {category}: {count}")
    print(f"rubric: {len(weights)} dimensions, weights sum to 100%")
    for dim, w in sorted(weights.items(), key=lambda kv: -kv[1]):
        print(f"  {dim}: {w:.0%}")

    guards = [c["id"] for c in cases if c["category"] == "break-the-rules"]
    if not guards:
        print("\nWARNING: no break-the-rules cases. Nothing is checking for overcorrection.")
    else:
        print(f"\novercorrection guards: {', '.join(guards)}")
    return 0


def cmd_run(args) -> int:
    cases = load_cases()
    runners = load_runners(Path(args.runners))
    conditions = {n: c for n, c in runners.items() if n != "judge"}
    if not conditions:
        raise SystemExit("runner config has no conditions (everything but 'judge')")

    OUT.mkdir(parents=True, exist_ok=True)
    skill = skill_body()
    records, failures = [], 0

    for case in cases:
        for name, cfg in sorted(conditions.items()):
            for trial in range(1, args.trials + 1):
                label = f"{case['id']} / {name} / trial {trial}"
                try:
                    text = invoke(cfg, {"prompt": case["prompt"], "skill": skill}, args.timeout)
                except (RuntimeError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
                    print(f"  FAIL {label}: {exc}", file=sys.stderr)
                    failures += 1
                    continue
                records.append(
                    {
                        "case_id": case["id"],
                        "category": case["category"],
                        "condition": name,
                        "trial": trial,
                        "response": text,
                    }
                )
                print(f"  ok   {label}  ({len(text)} chars)")

    RESPONSES.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8"
    )
    print(f"\n{len(records)} responses -> {RESPONSES.relative_to(REPO)}")
    if failures:
        print(f"{failures} invocations failed", file=sys.stderr)
        return 1
    return 0


def cmd_judge(args) -> int:
    if not RESPONSES.exists():
        raise SystemExit(f"No {RESPONSES.relative_to(REPO)}. Run `run` first.")

    runners = load_runners(Path(args.runners))
    if "judge" not in runners:
        raise SystemExit("runner config needs a 'judge' entry")

    block, weights = judging.load_rubric()
    cases = {c["id"]: c for c in load_cases()}

    grouped: dict[tuple[str, int], dict[str, str]] = defaultdict(dict)
    for line in RESPONSES.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            grouped[(rec["case_id"], rec["trial"])][rec["condition"]] = rec["response"]

    results, failures = [], 0
    for (case_id, trial), by_condition in sorted(grouped.items()):
        if len(by_condition) < 2:
            print(f"  skip {case_id} trial {trial}: only one condition present", file=sys.stderr)
            continue

        labelled, label_to_condition = judging.shuffle_labels(
            f"{case_id}:{trial}", by_condition, args.seed
        )
        prompt = judging.build_prompt(cases[case_id], labelled, block, weights)

        try:
            verdict = judging.run_judge(runners["judge"], prompt, args.timeout)
        except Exception as exc:  # noqa: BLE001 - one bad case must not kill the run
            print(f"  FAIL {case_id} trial {trial}: {exc}", file=sys.stderr)
            failures += 1
            continue

        for label, condition in label_to_condition.items():
            scores = verdict.get("scores", {}).get(label)
            if not scores:
                print(f"  FAIL {case_id} trial {trial}: judge skipped {label}", file=sys.stderr)
                failures += 1
                continue
            results.append(
                {
                    "case_id": case_id,
                    "trial": trial,
                    "condition": condition,
                    "scores": {k: scores[k] for k in weights if k in scores},
                    "weighted": judging.weighted(scores, weights),
                    "blocker": bool(verdict.get("blocker", {}).get(label, False)),
                    "note": verdict.get("note", {}).get(label, ""),
                }
            )
        print(f"  ok   {case_id} trial {trial}")

    SCORES.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in results), encoding="utf-8"
    )
    print(f"\n{len(results)} scores -> {SCORES.relative_to(REPO)}")
    return 1 if failures else 0


def cmd_report(args) -> int:
    if not SCORES.exists():
        raise SystemExit(f"No {SCORES.relative_to(REPO)}. Run `judge` first.")

    _, weights = judging.load_rubric()
    rows = [json.loads(l) for l in SCORES.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not rows:
        raise SystemExit("scores file is empty")

    by_condition: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_condition[row["condition"]].append(row)

    def mean(values: list[float]) -> float:
        return round(sum(values) / len(values), 3) if values else 0.0

    summary = {}
    for condition, entries in sorted(by_condition.items()):
        summary[condition] = {
            "n": len(entries),
            "cases": {e["case_id"] for e in entries},
            "weighted": mean([e["weighted"] for e in entries]),
            "dims": {d: mean([e["scores"][d] for e in entries if d in e["scores"]]) for d in weights},
            "blockers": [e for e in entries if e["blocker"]],
        }

    width = max(len(c) for c in summary)
    header = f"{'condition':<{width}}  {'n':>4}  {'weighted':>9}  " + "  ".join(
        f"{d[:12]:>12}" for d in weights
    )
    print(header)
    print("-" * len(header))
    for condition, s in summary.items():
        dims = "  ".join(f"{s['dims'][d]:>12.2f}" for d in weights)
        print(f"{condition:<{width}}  {s['n']:>4}  {s['weighted']:>9.3f}  {dims}")

    baseline = summary.get(args.baseline)
    candidate = summary.get(args.candidate)
    if not baseline or not candidate:
        print(f"\nNo gate: need both {args.baseline!r} and {args.candidate!r} in the scores.")
        return 0

    print(f"\nRelease gate: {args.candidate} against {args.baseline}")
    checks = []

    blockers = candidate["blockers"]
    checks.append(("no blocking findings", not blockers))
    for b in blockers:
        print(f"    blocker in {b['case_id']} trial {b['trial']}: {b['note']}")

    delta_correct = candidate["dims"]["correctness"] - baseline["dims"]["correctness"]
    checks.append((f"correctness within 0.1 (delta {delta_correct:+.2f})", delta_correct >= -0.1))

    delta_weighted = candidate["weighted"] - baseline["weighted"]
    checks.append((f"weighted beats baseline (delta {delta_weighted:+.3f})", delta_weighted > 0))

    same_shape = baseline["cases"] == candidate["cases"] and baseline["n"] == candidate["n"]
    checks.append(("same cases and trial count", same_shape))

    for label, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {label}")

    shipped = all(passed for _, passed in checks)
    print(f"\n{'SHIP' if shipped else 'DO NOT SHIP'}")
    return 0 if shipped else 1


# --- entry point ------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="check cases and rubric; no model calls")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("run", help="generate responses for every condition")
    p.add_argument("--runners", default=str(DEFAULT_RUNNERS))
    p.add_argument("--trials", type=int, default=3)
    p.add_argument("--timeout", type=int, default=300)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("judge", help="blind-grade the responses")
    p.add_argument("--runners", default=str(DEFAULT_RUNNERS))
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--seed", type=int, default=1, help="label shuffle seed; change it to re-blind")
    p.set_defaults(func=cmd_judge)

    p = sub.add_parser("report", help="weighted scores and the release gate")
    p.add_argument("--baseline", default="baseline")
    p.add_argument("--candidate", default="candidate")
    p.set_defaults(func=cmd_report)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
