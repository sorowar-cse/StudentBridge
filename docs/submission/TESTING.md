# StudentBridge test plan and reproduction

Version 4.0.0 corrected pilot · documentation updated 20 October 2026

## Evidence states

The latest local corrected-code suite passed **227 tests in 30.25 seconds**. The owner previously reported **227 passed in 23.03 seconds**, **366/366 offline requests with zero model calls**, **six actual Supabase checks passed**, and **four real Groq synthetic API probes passed**. The owner also confirmed the deployed UI and planning flows worked. See `EVIDENCE_STATUS.md` for the distinction between available console transcriptions and original files still to attach.

The original archive recorded 192 Python tests and 23 PGlite SQL checks. The SQL source is unchanged, but these legacy logs are not new runs on the latest app. Preserve their dates and environment labels. A live cap of 15 configured accounts does not establish simultaneous-user capacity.

Historical release archive SHA256: `41d550e383a832757f9d57ce59f8d5037cc7c86cc8286ddd862739225a4305f8`.

Rates are dated observations. Their supported currencies and publication dates can change. The app validates pair, positive rate and an age of at most ten days. It does not silently switch from failed online retrieval to illustrative offline values.

## 1 Re-run Python regression

From the configured source root:

```powershell
New-Item -ItemType Directory -Force evidence_private
Get-Date -Format o | Set-Content evidence_private/run_started.txt
git rev-parse HEAD | Set-Content evidence_private/reviewed_commit.txt
.\.venv\Scripts\python.exe --version 2>&1 | Tee-Object evidence_private/python_version.txt
.\.venv\Scripts\python.exe -m pytest -q 2>&1 | Tee-Object evidence_private/python_tests.txt
```

Check the final summary and exit status. On the current corrected code the expected suite count is 227. If dependencies/tests change, record the observed count and reason. Do not copy the supplied result into a new run file.

## 2 Optional PostgreSQL tests

Install a supported Node.js LTS separately for this developer suite only. From the repository root:

```powershell
npm ci
npm run test:sql 2>&1 | Tee-Object evidence_private/sql_tests.txt
```

Expected unchanged-v4 output: 23 checks passed. PGlite runs actual PostgreSQL RLS/functions and pgcrypto, but uses a stubbed `auth.uid()` claim. It is not a hosted Supabase JWT test, distributed race test or 15-user load test. No real funds or hosted profile records are changed by this suite.

## 3 Offline request evaluation

The existing corpus has 956 authored synthetic cases: 354 template-training/development, 236 development and 366 test/regression cases. Developers inspected generated cases while fixing behavior. The split is useful for repeatable regression, not blind evaluation or a learned-model training claim. Generation does not train a model.

See the actual parser options first:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate.py --help
```

Run the unchanged offline test split (this writes `evaluation/offline_test_dual_*`; retain the supplied copies separately first):

```powershell
.\.venv\Scripts\python.exe scripts\evaluate.py --provider offline --split test 2>&1 | Tee-Object evidence_private/offline_regression.txt
Copy-Item evaluation/offline_test_dual_summary.json evidence_private/
Copy-Item evaluation/offline_test_dual_observations.csv evidence_private/
```

The source dataset is included. Only regenerate it if intentionally changing/versioning the corpus. The existing 366/366 result uses no LLM calls. A real Groq benchmark requires new explicit consent, provider quota and its own result label. Never label offline success as LLM accuracy.

For genuinely new checks, author 20–30 unseen requests manually before running them. Include ambiguous direction, misplaced decimals, unsupported precision, mixed languages, missing billing periods, source invention, adversarial instructions and requests to bypass approval. Freeze expected outcomes first and keep these cases separate from the already exposed corpus. Report both correct answers and safe clarification/rejection outcomes, with a documented denominator.

## 4 Synthetic student profiles

`data/profile_test_cases.json` contains 15 invented profiles, with independently tabulated outputs in `data/profile_test_expected.csv`. The Python suite validates these expected values. Their tuition amounts are invented and do not establish university fees.

Optional loader:

```powershell
.\.venv\Scripts\python.exe scripts\load_pilot_profile.py --case P01
```

Use a dedicated blank synthetic account. Read the script's prompt and overwrite behavior before continuing. It is optional and is not needed to execute the unit tests. See `DEMO_SCENARIO.md` for a small manually entered, deterministic six-month example.

## 5 Hosted configuration and two-account security

Run:

```powershell
.\.venv\Scripts\python.exe scripts\doctor.py
.\.venv\Scripts\python.exe scripts\doctor.py --login
.\.venv\Scripts\python.exe scripts\check_cloud_security.py
```

Doctor checks configuration/catalogue; it does not execute a Groq inference. The hosted checker requires two different **blank dedicated test accounts** and the confirmation `SYNTHETIC`. It writes a profile marker, verifies own round-trip, B's actual REST inability to select A's profile, denied direct role update, anonymous denial, independent deletion and both audit chains. It then deletes test profile documents. It leaves account membership/audit events. Existing saved data causes an early stop; never use your real student accounts.

Output is `evaluation/cloud_security_private.json`. It excludes emails/passwords/JWTs, but inspect the file and terminal recording before sharing. Review cleanup on any network failure. The checker does not test every ledger limit or hosted concurrency.

## Personal tuition lookup and API diagnostics

The assistant now answers narrow personal fee/date questions from the signed-in saved profile, with no LLM call or cloud consent. This is separate from a real reviewed Groq conversion request. Check the displayed route/source label so the private lookup is not counted as a model inference.

The owner previously ran the separately supplied `scripts/check_groq.py` diagnostic: all four synthetic forecast/assistant planner/reviewer checks passed. Preserve that script in the submitted source if using its output as evidence. It must never print `.env` or private configuration. Its four calls validate access/schema compatibility for those prompts and do not constitute an LLM accuracy benchmark.

## 6 Manual hosted acceptance

Record each case in `TEST_RUN_RECORD.csv`; use `TEST_CASES.csv` as the acceptance matrix. Do not prefill passes. Important checks:

1. Start a fresh browser session. Confirm English default and all three translation options. Login as A and save the synthetic profile.
2. Restart the app, login again and confirm the profile persists. Login as B and confirm A's results and consent are absent.
3. Convert one supported pair, preserving source, direction and observation date. Separately show explicit illustrative mode if used.
4. With AI consent enabled, ask a simple exact-direction question and record the actual planner/reviewer IDs, outcome, time and any provider error. Do not record the key or raw Auth traffic.
5. In an executor account add only simulated funds, create a small quote and approve it with the checkbox and required suffix. Record wallet balances before/after and receipt ID. Repeat the same quote and verify the same receipt and unchanged balances. Do this before generating another quote.
6. Assign a separate pilot account `viewer`; demonstrate quote/execute denial. A planner may quote but may not execute. Restore intended roles afterward.
7. Demonstrate invalid suffix/expired quote/insufficient funds without changing the original records. Negative tests must never be labeled successful transfers.
8. Export PDF and verify StudentBridge header, receipt fields and the computer-generated footer. Ensure the PDF contains no secret or unrelated account data.

Use the existing SQL checks for scenarios that are awkward to trigger safely in the UI, such as audit alteration and member-cap rejection. Do not tamper with the live project's audit history solely to make a video.

## 7 Result interpretation

- An expected denial is a pass for its specific negative case, not proof of universal security.
- The rank-based anomaly screen uses synthetic Isolation Forest calibration. Its held-out synthetic normal flag rate was 2.2% on 500 cases; 100 deliberately extreme cases were all flagged. These are not real fraud sensitivity/specificity.
- No independent penetration test or 15-concurrent-user benchmark is claimed. Owner-run Supabase/Groq results now exist, but the original sanitized artifacts and targeted deployed replay/reboot evidence still need to be attached.
- The 15-member SQL cap and AI allowance limits are controls, not throughput measurements.
- Unexpected failures must be preserved with a brief issue reference and rerun status. A missing hosted test remains pending.

## 8 Submission evidence hygiene

Keep raw outputs outside the repository in a private evidence folder. If using the example `evidence_private/` commands within the repository, first exclude that folder in `.git/info/exclude`; do not stage it. Publish only reviewed sanitized copies in `docs/submission/evidence/`. Record UTC or Malaysia time with timezone, backend, app version, reviewed commit and exact command. A sanitized copy may conceal identifiers/secrets, but must preserve the true result, monetary values and timestamps needed to evaluate the test. E EVIDENCE_GUIDE explains the index and video procedure.
