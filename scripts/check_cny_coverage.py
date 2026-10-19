"""One batch HTTP request to measure current CNY reference-rate coverage.

Catalogues describe currencies, not guaranteed pair availability. We keep every
observed date and report rejected stale rows instead of promising all pairs.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datetime import datetime, timezone
import json
from studentbridge.fx import FXService, Rate
from studentbridge.money import FinanceError

ROOT = Path(__file__).resolve().parents[1]
fx = FXService("live")
result = {
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "provider": "Frankfurter v2",
    "note": "Outbound CNY batch observations. Inbound direct quotes are checked separately when requested. This is reference planning coverage, not payment corridor coverage.",
}
try:
    rows = fx._get("/rates", {"base": "cny"})
    if not isinstance(rows, list):
        raise FinanceError("Unexpected rate batch response.")
    accepted = []
    rejected = []
    for row in rows:
        try:
            if str(row["base"]).upper() != "CNY":
                raise FinanceError("Base mismatch")
            rate = Rate(
                "CNY",
                str(row["quote"]).upper(),
                str(row["rate"]),
                row["date"],
                "Frankfurter v2",
                "live",
                result["checked_at"],
            ).validate()
            accepted.append({"currency": rate.quote, "rate": rate.rate, "as_of": rate.as_of})
        except (FinanceError, KeyError, ValueError) as exc:
            rejected.append({"row": row, "reason": str(exc)})
    result.update(
        usable_quote_currencies=len({r["currency"] for r in accepted}),
        rejected_observations=len(rejected),
        accepted=accepted,
        rejected=rejected,
    )
except Exception as exc:
    result["error"] = str(exc)
out = ROOT / "evaluation"
out.mkdir(exist_ok=True)
(out / "live_cny_coverage.json").write_text(
    json.dumps(result, indent=2, default=str), encoding="utf-8"
)
print(json.dumps({k: v for k, v in result.items() if k not in {"accepted", "rejected"}}, indent=2))
