# StudentBridge deployment instructions

Version 4.0.0 · Windows-first procedure · prepared 20 October 2026

This procedure configures the recommended **Streamlit + Groq + Frankfurter + Supabase Auth/PostgreSQL** path. It complements the detailed Bengali `DEVELOPER_GUIDE_BN.md` already included with v4. Account dashboards can change labels; use the linked official documentation when a control moves.

## Current team deployment

Application: https://studentbridge.streamlit.app/

Repository: https://github.com/sorowar-cse/StudentBridge

The owner has completed account configuration, database installation, GitHub upload and Community Cloud deployment. Login, saved profile, UI, conversion, AI review and PDF checks were owner-confirmed. Existing users should use Section 7 for later runs and the GitHub push workflow for updates. Sections 1 to 6 document a fresh reproduction; do not recreate working accounts, rerun private setup SQL or generate a replacement master key for a routine code update.

## 1 Prerequisites and account order

1. Install Python **3.12**, VS Code and Git. Node.js is optional and only needed for SQL developer tests.
2. Extract the supplied v4 source to a normal writable folder, for example `C:\Projects\StudentBridge`.
3. Create/sign in to [Supabase](https://supabase.com/dashboard), [Groq Console](https://console.groq.com/) and [GitHub](https://github.com/). Use [Streamlit Community Cloud](https://share.streamlit.io/) for the final hosted application.
4. For a short pilot, start on the available free plans. Check their current quotas/availability in each account. Fifteen enrolled users does not imply unlimited or simultaneous AI use.

Frankfurter requires no account or API key. The hosted Groq models are not downloaded to your PC. An optional local model path exists, but is not required or covered by this deployment procedure.

## 2 Configure Supabase

Create a new project in the intended region and keep its database password privately. Wait until the project is available. Open its API/settings panel and copy the project URL and **publishable** API key. Do not use a secret/service-role key for the app.

In Authentication settings, **disable new public signups**. The owner will create the small set of pilot accounts. Preserve this setting after deployment. Do not put a database password in app settings; the application uses HTTPS Auth/REST and bounded RPCs.

## 3 Create Groq key

In Groq Console, open API Keys and create a key for this project. Save it privately. The current v4 defaults are `openai/gpt-oss-20b` and `openai/gpt-oss-120b`; consult the [model catalogue](https://console.groq.com/docs/models) for account availability. You do not train or download these models.

The built-in assistant and deterministic financial tools can operate without inference. Real Groq verification must nevertheless be completed before claiming the multi-model feature works in your account. An unavailable model or quota error is a failed/pending check, not a successful AI result.

## 4 First PC setup

Open a VS Code terminal in the source folder. Use explicit Python paths so PowerShell activation policy is not a blocker.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\setup_local.py
```

Choose Supabase, enter its URL and publishable key, then the Groq key. The wizard generates:

| File | Use | Share publicly |
|---|---|---|
| `.env` | PC configuration and stable master key | No |
| `runtime/setup_private.sql` | Installs derived signing/audit subkeys | No |
| `runtime/cloud_secrets.toml` | Streamlit deployment secrets | No |
| `.env.example` | Empty public configuration template | Yes |

**Preserve the generated master key.** Keep a matching protected backup of `.env`. Use the same original key on your PC and cloud app. Running setup again can retain existing values; deleting `.env` and creating a new random key will not decrypt old documents.

## 5 Install database schema in order

In Supabase SQL Editor:

1. Open `supabase/schema.sql` locally, paste its complete contents into a query, and run it.
2. Open your generated `runtime/setup_private.sql`, paste it into a separate private query, and run it.

The first installs tables, RLS, grants, bounded RPCs, member limits and the atomic simulation ledger. The second installs matching signing/audit subkeys. Do not disable RLS or grant ordinary users direct writes to make an error disappear. SQL Editor history containing the private setup is sensitive administrative material.

A key mismatch deliberately fails. Recover the matching original configuration rather than overwriting a working database's keys. A future schema change needs a reviewed SQL migration; a Git push alone does not execute it.

## 6 Create and test pilot users

In Authentication → Users create two confirmed **synthetic** accounts, with strong distinct passwords. This is owner provisioning, not independent proof of email ownership. Each account enrolls on its first successful app login. Default role is executor for simulation only; the database permits at most 15 enrolled members.

The optional owner utility is:

```powershell
.\.venv\Scripts\python.exe scripts\cloud_account_admin.py create
.\.venv\Scripts\python.exe scripts\cloud_account_admin.py reset-password
```

It privately prompts for the separate privileged Auth key. Never put that key in `.env`, the generated SQL/TOML, Streamlit Secrets, GitHub or screenshots. Prefer the dashboard if unsure.

To demonstrate roles, first let a test user sign in. Then change that user's `role` in the owner-controlled `public.sb_members` row to `viewer` or `planner`. Never accept a requested role from a student's editable profile. Restore an intended test role after capturing evidence.

## 7 Local run and later runs

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Open the local URL printed by Streamlit. Sign in, save a synthetic profile, sign out/in and confirm it is still there. Stop the server with Ctrl+C. On later days, reopen the folder and run the same command, or double-click `run_windows.bat`. You do not repeat account creation, SQL installation or model setup.

On macOS/Linux use `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install -r requirements.txt`, `.venv/bin/python scripts/setup_local.py`, and `.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1`.

## 8 Verify configuration before publishing

```powershell
.\.venv\Scripts\python.exe scripts\doctor.py
.\.venv\Scripts\python.exe scripts\doctor.py --login
.\.venv\Scripts\python.exe -m pytest -q
```

Doctor checks configuration/services and model catalogue access; it is **not** a real Groq inference test. The login option can enroll the account. Follow `TESTING.md` for the hosted two-account checker and manual model, role, replay and persistence tests. Resolve failures or label them honestly before recording the video.

## 9 Prepare sanitized GitHub contents

The source upload is the team's task. Merge the contents of `C_Repository_Update/` into the repository root. It places README at root and the public guides in `docs/submission/`, so the README links work. Optionally place A/B/D artifacts under that folder too. Retain the existing source tests, `requirements.txt`, `supabase/schema.sql`, `.env.example`, `LICENSE` and third-party notices.

Include source, public catalogue, translations, team assets approved for publication, tests and **sanitized** evidence. Exclude `.env`, `runtime/`, `.venv/`, local databases, `node_modules/`, private account exports, actual student data and unreviewed screenshots/logs. Do not replace the existing `.gitignore` with a shorter one.

Before every commit:

```powershell
git status --short
git check-ignore .env runtime/cloud_secrets.toml runtime/setup_private.sql
```

The second command should identify private paths as ignored. If Git already tracks a secret, ignoring it is insufficient: revoke/rotate it and remove it from history before publishing. Inspect the staged diff manually. Never put keys in a command argument or paste them into the README.

Initialize/upload using GitHub's repository instructions or VS Code Source Control. Keep the reviewed revision stable while collecting evidence. Record the full commit:

```powershell
git rev-parse HEAD
```

The real repository/live links and member details are populated. Insert `[[COMMIT_SHA]]` from the reviewed executable-code revision; record any later documentation-only commit separately.

## 10 Deploy on Streamlit Community Cloud

1. Sign in to Community Cloud and connect the intended GitHub account/repository.
2. Create an app using the reviewed repository, chosen branch and main file `app.py`.
3. Select Python **3.12** in the available deployment settings. Dependencies come from `requirements.txt`.
4. In the app's private Secrets settings paste your generated `runtime/cloud_secrets.toml`. Keep the **original master key**. Confirm the deployment setting is the intended cloud setting from that generated file.
5. Deploy and inspect the app's private build/runtime logs. Never expose a secrets panel in the recording.
6. Open the public app in a fresh browser session and log in using a pilot account. Cloud mode must use Supabase; it must not substitute SQLite on error.
7. Save a synthetic profile, restart/reboot the app, log in again and confirm persistence. Re-run the hosted role/isolation/replay/model checks.
8. Keep https://studentbridge.streamlit.app/ in GitHub **About → Website**, README and submission documents. A public app URL can still require pilot login.

Streamlit may sleep and service quotas may throttle. Test the app before the judging session. Do not rely on the hosting container's local files for student persistence. Do not store real private evidence in the public repository.

## 11 Acceptance checklist

- [ ] Public signup disabled, two dedicated test accounts verified.
- [ ] Correct public/publishable app key, no privileged key in runtime.
- [ ] Same stable master key and matching database subkeys.
- [ ] Python suite passed on reviewed revision.
- [ ] Hosted two-account RLS/role check passed and sanitized evidence retained.
- [ ] One consented real Groq task completed, actual outcome/model IDs recorded.
- [ ] One successful approved simulated transfer and replay single-debit check recorded.
- [ ] Saved profile survives app restart; account B sees only its own state.
- [ ] All links, dates, second member and screenshot placeholders completed.
- [ ] Video and public files contain no credentials or private student data.

## 12 Common failures

| Symptom | Action |
|---|---|
| Login fails | Check confirmed account, project status, matching URL/key, both SQL steps and member cap |
| Profile cannot decrypt | Restore original matching master key; do not generate a replacement at random |
| Signature mismatch | Confirm private SQL and app come from the same original setup |
| Groq unavailable | Check actual model access/key/quota; use deterministic tools with their true status label |
| Live rate unavailable | Report failure or explicitly choose illustrative offline mode; never relabel it live |
| Cloud changes disappear | Verify Supabase backend and matching project; hosting disk is temporary |
| HTTP/RPC authorization error | Recheck schema/grants/role; do not weaken RLS |

Official references: [Streamlit deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud), [Supabase Auth](https://supabase.com/docs/guides/auth), [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Groq models](https://console.groq.com/docs/models), [Frankfurter](https://frankfurter.dev/). Consult current account pages for pricing and quotas. No paid plan is automatically enabled by this application.
