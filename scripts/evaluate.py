"""Offline default; opt-in model runs produce raw observations, not fabricated scores."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import csv
import json
import os
import time
from dotenv import load_dotenv
from studentbridge.agent import FinanceAgent
from studentbridge.fx import FXService
from studentbridge.llm import ModelConfig
from studentbridge.university import UniversityCatalog
from studentbridge.risk import RiskEngine

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
parser = argparse.ArgumentParser()
parser.add_argument("--provider", choices=["offline", "groq", "ollama"], default="offline")
parser.add_argument("--planner", default=None)
parser.add_argument("--reviewer", default=None)
parser.add_argument(
    "--single", action="store_true", help="Single-planner baseline; deterministic gates still apply"
)
parser.add_argument(
    "--allow-cloud",
    action="store_true",
    help="Explicit consent to send synthetic questions/public data to Groq",
)
parser.add_argument("--max-cases", type=int, default=None)
parser.add_argument("--split", choices=["train", "dev", "test"], default="test")
parser.add_argument(
    "--pause",
    type=float,
    default=5,
    help="Seconds between opt-in live requests; account token limits still apply",
)
args = parser.parse_args()
if args.provider == "groq" and not args.allow_cloud:
    parser.error("Groq evaluation requires --allow-cloud.")
if args.provider != "offline" and not args.max_cases:
    parser.error("Set --max-cases to bound real provider calls. Start with 5.")
config = ModelConfig(
    args.provider,
    args.planner or os.getenv("PLANNER_MODEL", "openai/gpt-oss-20b"),
    args.reviewer or os.getenv("REVIEWER_MODEL", "openai/gpt-oss-120b"),
)
if args.provider == "ollama":
    config = ModelConfig(
        "ollama",
        args.planner or os.getenv("OLLAMA_PLANNER_MODEL", "qwen3:4b"),
        args.reviewer or os.getenv("OLLAMA_REVIEWER_MODEL", "gemma3:4b"),
    )
agent = FinanceAgent(FXService("demo"), UniversityCatalog(), config)
source = ROOT / "data/test_set.jsonl"
if not source.exists():
    parser.error("Run python scripts/generate_test_set.py first.")
cases = [
    json.loads(line)
    for line in source.read_text(encoding="utf-8").splitlines()
    if json.loads(line)["split"] == args.split
]
if args.max_cases:
    cases = cases[: max(0, args.max_cases)]
observations = []
for index, case in enumerate(cases):
    start = time.monotonic()
    try:
        result = agent.answer(
            case["question"], cloud_consent=args.allow_cloud, dual=not args.single
        )
    except Exception as exc:
        result = {"status": "error", "message": type(exc).__name__, "calls": []}
    if case["kind"] == "conversion":
        got = result.get("facts", {}).get("converted")
        passed = (
            result["status"] == "ok"
            and result.get("kind") == "conversion"
            and got == case["expected"]
        )
    else:
        got = result.get("kind", result["status"])
        desired = case["expected_status"]
        passed = (
            result["status"] == desired
            or (desired == "guidance" and result.get("kind") == "guidance")
            or (
                desired == "ambiguous_university"
                and (result["status"] == "clarify" or result.get("kind") == "guidance")
            )
        )
    observations.append(
        {
            "id": case["id"],
            "kind": case["kind"],
            "question": case["question"],
            "expected": case["expected"],
            "expected_status": case["expected_status"],
            "observed": got,
            "status": result["status"],
            "pass": passed,
            "seconds": round(time.monotonic() - start, 4),
            "calls": len(result.get("calls", [])),
            "model_evidence": json.dumps(result.get("calls", [])),
            "message": result.get("message", ""),
        }
    )
    if args.provider != "offline":
        print(f"{index + 1}/{len(cases)} {case['id']}: {result['status']}", flush=True)
        # Stop on provider failure so a bad key/rate limit doesn't waste the whole quota.
        if (
            result["status"] == "error"
            or "request failed" in result.get("message", "").lower()
            or "rate limit" in result.get("message", "").lower()
        ):
            break
        if index + 1 < len(cases):
            time.sleep(max(0, min(args.pause, 60)))
kind = "offline" if args.provider == "offline" else "live_" + args.provider
suffix = "single" if args.single else "dual"
out = ROOT / "evaluation"
out.mkdir(exist_ok=True)
raw = out / f"{kind}_{args.split}_{suffix}_observations.csv"
with raw.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(observations[0]) if observations else ["id"])
    writer.writeheader()
    writer.writerows(observations)
conversions = [r for r in observations if r["kind"] == "conversion"]
attacks = [r for r in observations if r["kind"] == "adversarial"]
summary = {
    "provider": args.provider,
    "planner": config.planner if args.provider != "offline" else None,
    "reviewer": config.reviewer if args.provider != "offline" and not args.single else None,
    "dataset": "Synthetic demo FX; grouped authored question templates",
    "split": args.split,
    "cases_run": len(observations),
    "planned_cases": len(cases),
    "task_completion": sum(r["pass"] for r in observations) / len(observations)
    if observations
    else None,
    "exact_conversion_rate": sum(r["pass"] for r in conversions) / len(conversions)
    if conversions
    else None,
    "adversarial_expected_response_rate": sum(r["pass"] for r in attacks) / len(attacks)
    if attacks
    else None,
    "actual_model_calls": sum(r["calls"] for r in observations),
    "mean_seconds": sum(r["seconds"] for r in observations) / len(observations)
    if observations
    else None,
    "risk_synthetic_holdout": RiskEngine().evaluate(),
    "limits": "Generated test cases were used during debugging: this is a regression benchmark, not blind generalization. Offline results are deterministic router/tool checks, not real LLM accuracy. Adversarial response checks do not measure production attack resistance. See pytest for state-change security tests.",
}
summary_file = out / f"{kind}_{args.split}_{suffix}_summary.json"
summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
print("Raw observations:", raw.name)
