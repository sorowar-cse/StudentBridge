"""Compile StudentBridge's existing evidence into the repository documents.

Put this file beside app.py and run it with the project's Python. It makes no
network calls, reads no credentials, and leaves the original logs untouched.
The manual outcomes below come from the owner's confirmations on 20 Oct 2026.
They are kept separate from the machine-readable pytest/checker/SQL evidence.
"""

from __future__ import annotations

import csv
import codecs
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation


BASELINE = "ca161fbfdee8ef9594a577e767d1e7e0836fe242"
MANUAL_TIME = "Owner confirmed 2026-10-20 UTC+08:00; exact UI execution time not recorded"
ROOT = Path(__file__).resolve().parent


def read_evidence_text(path: Path) -> str:
    """Read Windows PowerShell logs without changing the original file.

    A Windows PowerShell Tee-Object log can have a UTF-16 BOM, while VS Code
    and CSV exports commonly use UTF-8. Check UTF-32 first because its little
    endian BOM begins with the same two bytes as UTF-16 little endian.
    Decoding stays strict so a damaged evidence file is never silently repaired.
    """
    raw = path.read_bytes()
    if raw.startswith((codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
        encoding = "utf-32"
    elif raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        encoding = "utf-16"
    else:
        encoding = "utf-8-sig"
    try:
        return raw.decode(encoding)
    except UnicodeError as error:
        raise ValueError(
            f"Cannot decode {path.name} as {encoding}. Keep the original file "
            "and report this filename; no evidence bytes have been changed."
        ) from error


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    stream = io.StringIO(read_evidence_text(path), newline="")
    reader = csv.DictReader(stream)
    return list(reader.fieldnames or []), list(reader)


def csv_text(fields: list[str], rows: list[dict[str, str]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def replace_table_row(text: str, label: str, cells: list[str]) -> str:
    pattern = r"(?m)^\|\s*" + re.escape(label) + r"\s*\|[^\n]*$"
    return re.sub(pattern, lambda _: "| " + " | ".join(cells) + " |", text)


def main() -> int:
    print("StudentBridge evidence updater v1.1 | UTF-8 / UTF-16 / UTF-32")
    docs = ROOT / "docs/submission"
    logs = docs / "evidence/logs"
    if not (ROOT / "app.py").is_file():
        raise ValueError("Move this script into StudentBridge beside app.py, then run again.")

    required = [
        logs / "pytest_final.txt", logs / "pytest_metadata.txt",
        logs / "hosted_security_sanitized.json",
        logs / "transfer_execution.csv", logs / "transfer_audit.csv",
        docs / "TECHNICAL_DOCUMENTATION.md",
        docs / "SECURITY_SELF_ASSESSMENT.md",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        raise ValueError("Required files not found:\n  " + "\n  ".join(missing))

    # Validate the saved results before changing any document.
    pytest_text = read_evidence_text(required[0])
    summary = re.findall(r"\b(\d+) passed in ([\d.]+)s\b", pytest_text)
    exit_codes = re.findall(r"pytest exit code:\s*(\d+)", pytest_text)
    if not summary or not exit_codes or exit_codes[-1] != "0":
        raise ValueError("pytest_final.txt must contain a passing summary and pytest exit code: 0.")
    count, seconds = summary[-1]
    if count != "227":
        raise ValueError("This update expects the reported 227-test suite; review the changed test count first.")
    metadata = read_evidence_text(required[1])
    commits = re.findall(r"(?m)^\s*([0-9a-fA-F]{40})\s*$", metadata)
    stamps = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^\s]*", metadata)
    if not commits or not stamps:
        raise ValueError("pytest_metadata.txt is missing the tested Git HEAD or ISO start timestamp.")
    tested_commit, test_time = commits[-1].lower(), stamps[0]

    hosted = json.loads(read_evidence_text(required[2]))
    checks = hosted.get("checks", [])
    expected_checks = {
        "Own profile round trip and AES authentication",
        "B cannot SELECT A profile through the actual REST API",
        "Direct role update denied by database grants",
        "Anonymous document access denied",
        "B deletion does not affect A",
        "Both per-user audit chains verify",
    }
    if (len(checks) != 6 or {c.get("name") for c in checks} != expected_checks
            or any(c.get("passed") is not True for c in checks)):
        raise ValueError("The saved hosted result must contain six passing checks.")
    hosted_time = str(hosted.get("checked_at", "")).strip()
    if not hosted_time:
        raise ValueError("The saved hosted result has no original checked_at timestamp.")

    _, transfers = read_rows(required[3])
    _, events = read_rows(required[4])
    if len(transfers) != 1 or len(events) != 1:
        raise ValueError("Expected one transfer CSV row and one matching audit CSV row.")
    transfer, event = transfers[0], events[0]
    quote = transfer.get("quote_id", "")
    if not quote or event.get("quote_id") != quote or event.get("event") != "sandbox_transfer_completed":
        raise ValueError("The two CSV records do not identify the same completed quote.")
    if (transfer.get("source_currency"), transfer.get("target_currency")) != ("USD", "CNY"):
        raise ValueError("The reported walkthrough used USD to CNY; check the exported quote.")
    amounts = [Decimal(transfer[k]) for k in ("total_spent", "fee_included", "received_amount")]
    if amounts != [Decimal("50"), Decimal("0.40"), Decimal("329.31")]:
        raise ValueError("The CSV amounts differ from the owner's reported walkthrough; inspect before updating.")
    if (Decimal(event["total_spent"]) != amounts[0]
            or Decimal(event["received_amount"]) != amounts[2]):
        raise ValueError("The audit amounts do not match the transfer CSV.")
    execution_time = transfer.get("executed_at_utc", "")
    if not execution_time:
        raise ValueError("The transfer CSV has no executed_at_utc timestamp.")

    def available(paths: list[str]) -> str:
        absent = [p for p in paths if not (docs / p).is_file()]
        return "Attached" if not absent else "Attach/rename: " + "; ".join(absent)

    pytest_result = f"{count} passed in {seconds} seconds; exit code 0"
    note = (
        f"Final owner verification: {pytest_result}. Test time: {test_time}. "
        f"The tested Git revision is {tested_commit}. The saved Supabase checker records six passes "
        f"at {hosted_time}; this updater does not rerun that checker. The owner confirmed a "
        "six-month forecast of MYR 18,480 total cost, MYR 24,000 resources, zero overall funding gap "
        "and MYR 4,580 timing shortfall. The saved CSVs contain one USD 50.00 transfer, including "
        "a USD 0.40 fee, receiving CNY 329.31, and one matching completion audit event. The owner "
        "confirmed that replay returned the original receipt with wallet balances unchanged at "
        "USD 50.00 and CNY 329.31. Reboot/relogin preserved the profile and wallet and reproduced "
        "the forecast. Live Groq conversion and forecast review worked after resolving an HTTP 401 "
        "authentication error. UI outcomes are owner-confirmed observations. Unperformed hosted "
        "role, expiry, tamper, limit and concurrent-race checks remain pending."
    )
    writes: dict[Path, str] = {}

    technical_path, security_path = required[5], required[6]
    technical = read_evidence_text(technical_path)
    security = read_evidence_text(security_path)
    technical = replace_table_row(technical, "Owner PC Python suite", [
        "Owner PC Python suite", pytest_result,
        "Final owner-run regression; evidence/logs/pytest_final.txt and pytest_metadata.txt",
    ])
    technical = re.sub(
        r"### 8\.1 (?:Remaining execution evidence|Hosted execution evidence and remaining scope)\n.*?(?=### 8\.2|\Z)",
        lambda _: "### 8.1 Hosted execution evidence and remaining scope\n\n" + note + "\n\n",
        technical, flags=re.S,
    )
    security = replace_table_row(security, "Owner PC suite", [
        "Owner PC suite", pytest_result, "Final owner-run regression; original log and metadata attached",
    ])
    security = replace_table_row(security, "Saved profile after explicit reboot", [
        "Saved profile after explicit reboot", "Owner-confirmed pass",
        "Profile and wallet persisted after reboot/relogin; SS07 captures",
    ])
    security = replace_table_row(security, "Deployed same-quote replay", [
        "Deployed same-quote replay", "Owner-confirmed pass",
        "Original receipt and unchanged balances; SS05 and transfer CSVs",
    ])
    security = replace_table_row(security, "SC07", [
        "SC07", "Atomic ledger and unique quote receipt", "One debit on retry; rollback on failure",
        "Owner-confirmed deployed replay and matching CSVs; concurrent network-race test pending",
    ])
    security = replace_table_row(security, "SC12", [
        "SC12", "Account-switch clearing and profile deletion", "UI/SQL isolation and deletion tests",
        "Saved checker confirms deletion isolation; owner confirms reboot persistence",
    ])
    security = security.replace("[[HOSTED_CHECK_DATE]]", hosted_time)
    security = security.replace(
        "Evidence index: E_Evidence_Guide/EVIDENCE_INDEX.csv",
        "Evidence index: docs/submission/EVIDENCE_INDEX.csv",
    )
    # A marked note makes repeated runs replace their own note rather than duplicate it.
    start, end = "<!-- STUDENTBRIDGE_FINAL_VERIFICATION_START -->", "<!-- STUDENTBRIDGE_FINAL_VERIFICATION_END -->"
    for path, text in [(technical_path, technical), (security_path, security)]:
        text = re.sub(re.escape(start) + r".*?" + re.escape(end), "", text, flags=re.S).rstrip()
        if path == technical_path and "### 8.1 Hosted execution evidence and remaining scope" in text:
            writes[path] = text + "\n"
        else:
            writes[path] = text + "\n\n" + start + "\n\n## Final owner verification\n\n" + note + "\n\n" + end + "\n"

    evidence_fields = ["Evidence_ID", "Description", "Observed_status", "Evidence_class", "Available_file",
                       "Original_or_capture_still_needed", "Actual_run_time_with_timezone", "Reviewed_commit"]
    index_path = docs / "EVIDENCE_INDEX.csv"
    if index_path.exists():
        old_fields, index_rows = read_rows(index_path)
        evidence_fields = list(dict.fromkeys(old_fields + evidence_fields))
    else:
        descriptions = ["Final owner Python regression", "Earlier owner Python result", "Saved hosted Supabase checker",
                        "Earlier Groq diagnostic", "Earlier connection check", "Earlier offline regression",
                        "Historical isolated SQL checks", "Owner deployed UI observations", "Sandbox execution and replay",
                        "Reboot persistence", "Security screenshot", "Demo video"]
        index_rows = [dict(Evidence_ID=f"E{i:02}", Description=d, Observed_status="See earlier labelled evidence",
                           Evidence_class="Earlier evidence; retain original scope", Available_file="",
                           Original_or_capture_still_needed="Retain original file and timestamp",
                           Actual_run_time_with_timezone="", Reviewed_commit="") for i, d in enumerate(descriptions, 1)]
        index_rows[-1].update(Observed_status="Pending recording", Evidence_class="Pending capture")
    by_id = {r["Evidence_ID"]: r for r in index_rows}
    changes = {
        "E01": (pytest_result, "Original owner pytest log", ["evidence/logs/pytest_final.txt", "evidence/logs/pytest_metadata.txt"], test_time, tested_commit),
        "E03": ("Six saved checks passed", "Saved hosted checker JSON; no new execution", ["evidence/logs/hosted_security_sanitized.json"], hosted_time, "Original checker revision not recorded"),
        "E08": ("Owner confirms profile, forecast, conversion and AI working", "Owner UI observations", ["evidence/screenshots/SS01_profile.png", "evidence/screenshots/SS02_forecast.png", "evidence/screenshots/SS03_currency.png", "evidence/screenshots/SS08_ai_conversion.png", "evidence/screenshots/SS08_ai_forecast.png"], MANUAL_TIME, BASELINE),
        "E09": ("One stored execution and audit event; owner confirms replay without second debit", "Saved SQL CSVs plus owner replay observation", ["evidence/logs/transfer_execution.csv", "evidence/logs/transfer_audit.csv", "evidence/screenshots/SS05_replay.png", "evidence/screenshots/SS05_wallet_after_replay.png", "evidence/pdfs/StudentBridge_Receipt.pdf"], execution_time + " UTC (initial execution); exact replay time not recorded", BASELINE),
        "E10": ("Owner confirms profile and wallet persisted; forecast reproduced", "Owner reboot/relogin observation", ["evidence/screenshots/SS07_profile_after_reboot.png", "evidence/screenshots/SS07_wallet_after_reboot.png"], MANUAL_TIME, BASELINE),
        "E11": ("Saved six-check result displayed", "Capture of previous checker result", ["evidence/screenshots/SS06_security.png", "evidence/logs/hosted_security_sanitized.json"], hosted_time + " (original checker time)", "Original checker revision not recorded"),
    }
    for eid, (status, kind, paths, stamp, commit) in changes.items():
        row = by_id.setdefault(eid, {"Evidence_ID": eid})
        if row not in index_rows:
            index_rows.append(row)
        row.update(Observed_status=status, Evidence_class=kind, Available_file="; ".join(paths),
                   Original_or_capture_still_needed=available(paths), Actual_run_time_with_timezone=stamp,
                   Reviewed_commit=commit)
    writes[index_path] = csv_text(evidence_fields, index_rows)

    run_fields = ["Case_ID", "Run_at_with_timezone", "Reviewed_commit", "Environment", "Observed_result",
                  "Pass_Fail_Pending", "Evidence_path", "Issue_or_note"]
    run_path = docs / "TEST_RUN_RECORD.csv"
    if run_path.exists():
        old_fields, run_rows = read_rows(run_path)
        run_fields = list(dict.fromkeys(old_fields + run_fields))
    else:
        run_rows = [dict(Case_ID=f"TC{i:02}", Pass_Fail_Pending="Pending") for i in range(1, 32)]
    outcomes = {
        "TC02": ("Owner confirms successful login", ["evidence/screenshots/SS01_profile.png"]),
        "TC06": ("Saved checker: B cannot read A profile through REST", ["evidence/logs/hosted_security_sanitized.json"]),
        "TC07": ("Saved checker: direct role update denied", ["evidence/logs/hosted_security_sanitized.json"]),
        "TC09": ("Owner confirms profile/wallet persisted after reboot and relogin", ["evidence/screenshots/SS07_profile_after_reboot.png", "evidence/screenshots/SS07_wallet_after_reboot.png"]),
        "TC11": ("Owner confirms cost18480/resources24000/gap0/timing4580 MYR", ["evidence/screenshots/SS02_forecast.png", "evidence/pdfs/StudentBridge_Forecast.pdf"]),
        "TC17": ("Owner confirms live Groq conversion and forecast review working after resolving 401", ["evidence/screenshots/SS08_ai_conversion.png", "evidence/screenshots/SS08_ai_forecast.png"]),
        "TC23": ("One matching stored transfer and completion audit event", ["evidence/logs/transfer_execution.csv", "evidence/logs/transfer_audit.csv", "evidence/pdfs/StudentBridge_Receipt.pdf"]),
        "TC24": ("Owner confirms same receipt on replay; USD50.00/CNY329.31 unchanged", ["evidence/screenshots/SS05_replay.png", "evidence/screenshots/SS05_wallet_after_replay.png"]),
        "TC28": ("Owner confirms downloaded PDF documents opened and were checked", ["evidence/pdfs/StudentBridge_Forecast.pdf", "evidence/pdfs/StudentBridge_Receipt.pdf"]),
        "TC29": ("Saved checker: deleting B profile leaves A untouched", ["evidence/logs/hosted_security_sanitized.json"]),
    }
    for row in run_rows:
        cid = row.get("Case_ID")
        if cid not in outcomes:
            continue
        result, paths = outcomes[cid]
        saved = cid in {"TC06", "TC07", "TC29"}
        stamp = hosted_time if saved else execution_time + " UTC" if cid == "TC23" else MANUAL_TIME
        row.update(Run_at_with_timezone=stamp, Reviewed_commit="Original checker revision not recorded" if saved else BASELINE,
                   Environment="Hosted Supabase REST - saved checker result" if saved else "Hosted application - owner observation / saved SQL export",
                   Observed_result=result, Pass_Fail_Pending="Pass", Evidence_path="; ".join(paths),
                   Issue_or_note=available(paths) + (". No new checker run." if saved else ". Owner-provided code baseline; hosting build SHA not independently captured."))
    writes[run_path] = csv_text(run_fields, run_rows)

    cases_path = docs / "TEST_CASES.csv"
    if cases_path.exists():
        fields, cases = read_rows(cases_path)
        if "Evidence_status" in fields:
            for row in cases:
                if row.get("Case_ID") in outcomes:
                    result, paths = outcomes[row["Case_ID"]]
                    row["Evidence_status"] = result + ". " + available(paths)
            writes[cases_path] = csv_text(fields, cases)

    status = ["# StudentBridge evidence status", "", "This register compiles saved logs and owner-confirmed UI outcomes. It does not execute new tests.", "",
              "| Record | Result | Evidence | Attachment state |", "|---|---|---|---|"]
    for eid in ["E01", "E03", "E08", "E09", "E10", "E11"]:
        row = by_id[eid]
        status.append("| " + " | ".join([eid, row["Observed_status"], row["Available_file"], row["Original_or_capture_still_needed"]]) + " |")
    status += ["| E12 | Video remains pending until actually recorded and reviewed | StudentBridge_demo.mp4 or accessible link | Pending |", "",
               "Earlier evidence retains its original dates and scope: the earlier owner suite reported 227 tests in 23.03 seconds; offline regression reported 366/366 with zero LLM calls; four Groq synthetic probes were reported separately; the 23 isolated SQL checks are historical development evidence.", "",
               "The ten completed acceptance records are TC02, TC06, TC07, TC09, TC11, TC17, TC23, TC24, TC28 and TC29. Other rows retain their existing status. Targeted hosted role/expiry/tamper/limit tests, concurrent load and network races have no new passing result here.", "",
               "Exact pytest/checker/initial-execution timestamps come from their saved artifacts. Exact manual replay/reboot times were not recorded and are not invented. The UI rows identify the owner's reviewed code baseline; pytest_metadata.txt identifies the actual Git HEAD tested.", ""]
    writes[docs / "EVIDENCE_STATUS.md"] = "\n".join(status)

    # Backups are kept under runtime/, which the existing project ignores in Git.
    backup = ROOT / "runtime/evidence_backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for path in writes:
        if path.exists():
            dest = backup / path.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
    for path, text in writes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".studentbridge.tmp")
        try:
            temp.write_text(text, encoding="utf-8")
            temp.replace(path)
        finally:
            if temp.exists():
                temp.unlink()

    report = ["StudentBridge evidence compilation", "Compilation time: " + datetime.now(timezone.utc).isoformat(),
              "pytest: " + pytest_result, "Tested Git HEAD: " + tested_commit,
              "Original hosted check time: " + hosted_time, "Quote: " + quote,
              "Stored CSV rows: one transfer, one matching completion audit event",
              "No network calls, new tests or credential reads were performed.", "", "Input hashes:"]
    for path in required[:5]:
        report.append(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + str(path.relative_to(ROOT)))
    report += ["", "Updated files:"] + [str(p.relative_to(ROOT)) for p in writes]
    (logs / "evidence_update_summary.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("Evidence records updated successfully.")
    print("Saved pytest result: " + pytest_result)
    print("Saved hosted checks: 6 passed; SQL exports: 1 transfer and 1 audit event.")
    print("Completed acceptance rows updated: 10. Other rows retained.")
    print("Backup: " + str(backup.relative_to(ROOT)))
    attachment_issues = [by_id[e]["Original_or_capture_still_needed"] for e in changes
                         if by_id[e]["Original_or_capture_still_needed"] != "Attached"]
    if attachment_issues:
        print("Some attachments still need their expected filenames:")
        for issue in dict.fromkeys(attachment_issues):
            print("  " + issue)
    print("Video stays pending. Existing review/signoff decisions are preserved.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, csv.Error, InvalidOperation) as error:
        print("STOP: " + str(error), file=sys.stderr)
        sys.exit(1)
