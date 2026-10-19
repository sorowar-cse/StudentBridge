# StudentBridge evidence status

Documentation updated 20 October 2026. Exact run timestamps must come from the original files.

| Record | Existing observation | Remaining artifact |
|---|---|---|
| Current local automated suite | 227 passed in 30.25 seconds after UI and team updates | Owner current-code log and reviewed commit |
| Owner earlier corrected suite | 227 passed in 23.03 seconds, console supplied | Reviewed sanitized owner_pytest_run.txt |
| Owner offline regression | 366/366, zero calls, authored synthetic data | owner_offline_run.txt and matching summary/CSV |
| Owner actual Supabase check | All six checks passed, console supplied | Reviewed cloud_security_private.json copied under a sanitized public filename |
| Owner Groq diagnostic | Four HTTP 200/schema passes | Reviewed synthetic diagnostic console recording/file |
| Owner doctor check | Configuration/Auth/FX/catalogue checks passed | owner_connection_check.txt |
| Deployed acceptance | Owner reports login, saved profile, assistant, conversion, forecast, PDF, language/UI and member details OK | SS01 to SS06 as applicable and actual video |
| Deployed replay | No specific balance/receipt recording supplied | Same quote, same receipt, unchanged balances on retry |
| Explicit reboot persistence | Profile visible online, no reboot record supplied | Reboot, relogin and same profile capture |
| Concurrent load | No result supplied | Future work, not a submission success claim |

The submission pack's E_Evidence_Guide folder includes labelled console transcriptions and historical v4 raw development logs. Transcriptions are not original machine log files. Preserve failures, dates and scope. A blank row in TEST_RUN_RECORD is a new capture template, not a denial of the earlier observed results. Complete each current-revision row only after observing that case.
