# StudentBridge evidence status

This register compiles saved logs and owner-confirmed UI outcomes. It does not execute new tests.

| Record | Result | Evidence | Attachment state |
|---|---|---|---|
| E01 | 227 passed in 28.16 seconds; exit code 0 | evidence/logs/pytest_final.txt; evidence/logs/pytest_metadata.txt | Attached |
| E03 | Six saved checks passed | evidence/logs/hosted_security_sanitized.json | Attached |
| E08 | Owner confirms profile, forecast, conversion and AI working | evidence/screenshots/SS01_profile.png; evidence/screenshots/SS02_forecast.png; evidence/screenshots/SS03_currency.png; evidence/screenshots/SS08_ai_conversion.png; evidence/screenshots/SS08_ai_forecast.png | Attached |
| E09 | One stored execution and audit event; owner confirms replay without second debit | evidence/logs/transfer_execution.csv; evidence/logs/transfer_audit.csv; evidence/screenshots/SS05_replay.png; evidence/screenshots/SS05_wallet_after_replay.png; evidence/pdfs/StudentBridge_Receipt.pdf | Attached |
| E10 | Owner confirms profile and wallet persisted; forecast reproduced | evidence/screenshots/SS07_profile_after_reboot.png; evidence/screenshots/SS07_wallet_after_reboot.png | Attached |
| E11 | Saved six-check result displayed | evidence/screenshots/SS06_security.png; evidence/logs/hosted_security_sanitized.json | Attached |
| E12 | Video remains pending until actually recorded and reviewed | StudentBridge_demo.mp4 or accessible link | Pending |

Earlier evidence retains its original dates and scope: the earlier owner suite reported 227 tests in 23.03 seconds; offline regression reported 366/366 with zero LLM calls; four Groq synthetic probes were reported separately; the 23 isolated SQL checks are historical development evidence.

The ten completed acceptance records are TC02, TC06, TC07, TC09, TC11, TC17, TC23, TC24, TC28 and TC29. Other rows retain their existing status. Targeted hosted role/expiry/tamper/limit tests, concurrent load and network races have no new passing result here.

Exact pytest/checker/initial-execution timestamps come from their saved artifacts. Exact manual replay/reboot times were not recorded and are not invented. The UI rows identify the owner's reviewed code baseline; pytest_metadata.txt identifies the actual Git HEAD tested.
