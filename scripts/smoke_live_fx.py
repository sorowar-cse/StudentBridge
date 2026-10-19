"""Opt-in real HTTP check; failures are evidence, not replaced with demo rates."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dataclasses import asdict
from datetime import datetime, timezone
import json
from studentbridge.fx import FXService

ROOT = Path(__file__).resolve().parents[1]
fx = FXService("live")
evidence = {
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "provider": "Frankfurter v2",
    "results": [],
}
try:
    codes = fx.currencies()
    evidence["catalogue_count"] = len(codes)
except Exception as exc:
    evidence["catalogue_error"] = str(exc)
for source, target in [
    ("BDT", "CNY"),
    ("CNY", "BDT"),
    ("MYR", "CNY"),
    ("CNY", "MYR"),
    ("JPY", "CNY"),
    ("CNY", "KWD"),
]:
    try:
        evidence["results"].append(
            {
                "source": source,
                "target": target,
                "status": "ok",
                "reference": asdict(fx.rate(source, target)),
            }
        )
    except Exception as exc:
        evidence["results"].append(
            {"source": source, "target": target, "status": "unavailable", "reason": str(exc)}
        )
out = ROOT / "evaluation"
out.mkdir(exist_ok=True)
(out / "live_fx_smoke.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
print(json.dumps(evidence, indent=2))
