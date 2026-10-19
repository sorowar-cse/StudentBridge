# StudentBridge v4

**2026 Shenzhen International FinTech Competition, International Track · Topic C: Cross-border & Student Finance Assistant**

StudentBridge brings student-entered fees, monthly cash flow, published currency references and explicitly approved simulated transfers into one Streamlit application. It targets an invite-only pilot of at most 15 enrolled accounts.

**Application:** [StudentBridge-Live](https://studentbridge.streamlit.app/) 
 
**Release:** 4.0.0 · documentation prepared 19 October 2026


## What it does

- Saves an encrypted student profile with university, department, programme, location, actual tuition amount and billing schedule.
- Forecasts up to 96 monthly buckets using living costs, savings, confirmed income, reserve, growth and optional FX stress. Shows both total funding gap and early timing shortfall.
- Converts supported currencies to/from CNY and other supported pairs using dated Frankfurter reference observations. Coverage is discovered from the provider. Offline illustrative anchors are clearly labeled.
- Retrieves curated programme references with source URLs and checked dates.
- Uses optional Groq planner/reviewer models with typed plans and deterministic validation. Calculations remain Python tools.
- Simulates fee comparisons and signed, expiring transfers with approval, roles, limits, atomic database updates, replay protection and audit verification.
- Starts in English and supports Bangla, Simplified Chinese and Malay. Downloads English-labeled planning and receipt PDFs.

## Scope

**No real money moves.** Wallet balances and the Campus, Value and Swift providers are fictional. FX data is a published reference, not an executable bank quote. University entries are curated reference material; personal fees are user-provided. Forecasts depend on declared assumptions and do not predict future FX or university policy.

SAGE-FX is our name for the composition of source retrieval, constrained planning/review, exact tools, anomaly screening and controlled execution. It uses established algorithms and cryptographic libraries. It is not a newly invented cipher or a validated real-world fraud detector.

## Architecture

| Layer | Implementation |
|---|---|
| Interface and application | Python 3.12, Streamlit |
| Optional hosted language models | Groq, openai/gpt-oss-20b planner and openai/gpt-oss-120b reviewer |
| Exchange references | Frankfurter v2, daily published observations, no API key |
| Identity and persistence | Supabase Auth and PostgreSQL RLS/RPCs |
| Calculation and protection | Decimal, Pydantic, AES-GCM, HMAC-SHA256, synthetic Isolation Forest |

No Docker, local PostgreSQL or model download is required for this recommended setup. Internet and the team's own service accounts are required. Node.js is only for the optional SQL test suite.

## First run on Windows

Install Python 3.12 and open the project folder in VS Code. Then:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\setup_local.py
```

Complete the Supabase project and Groq prompts. In Supabase SQL Editor run `supabase/schema.sql`, then your generated private `runtime/setup_private.sql`. Disable public signup and create confirmed pilot accounts. Then:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

For full setup, later runs, account management, deployment and troubleshooting, read [DEPLOYMENT.md](docs/submission/DEPLOYMENT.md) and the existing [DEVELOPER_GUIDE_BN.md](DEVELOPER_GUIDE_BN.md). User operations are in [USER_GUIDE.md](USER_GUIDE.md).

## Tests and evidence

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\doctor.py
.\.venv\Scripts\python.exe scripts\doctor.py --login
```

Optional SQL checks:

```bash
npm ci
npm run test:sql
```

The supplied release records 192 passing Python tests, 23 PGlite PostgreSQL checks and 366/366 authored offline regression cases with zero LLM calls. PGlite uses real RLS/pgcrypto with a stubbed Auth claim. These results are not hosted integration, blind generalization or concurrent-load evidence. A dated FX smoke check observed six usable pairs and 165 catalogue entries; current support can change.

See [TESTING.md](docs/submission/TESTING.md), [TEST_CASES.csv](docs/submission/TEST_CASES.csv) and `evaluation/VERIFICATION.md`. Re-run relevant checks after changing code. Run the two-account hosted checker only on two dedicated blank synthetic accounts; it creates and deletes test documents.

## Security and configuration

Keep `.env`, `runtime/`, real credentials, private exports, local databases and virtual environments out of Git. The app uses a publishable Supabase key and each user's JWT. It rejects a privileged service key as an app key. The owner-only account utility requests administrative credentials privately outside the app runtime.

Preserve the same generated master key across PC and deployment. Losing or changing it can make stored documents unreadable. The database administrator and app host remain trusted. Public signup must stay disabled for this pilot. The 15-account limit is an enrollment cap, not measured simultaneous AI capacity.

Read [SECURITY_SELF_ASSESSMENT.md](docs/submission/SECURITY_SELF_ASSESSMENT.md) for permission tiers, known risks and pending hosted checks.

## Deployment and public link

Deploy `app.py` on Streamlit Community Cloud using the sanitized GitHub repository, Python 3.12 and the generated cloud secrets. Saved profiles reside in Supabase rather than the hosting container's local disk. Follow [DEPLOYMENT.md](docs/submission/DEPLOYMENT.md), verify persistence and replace the live-link field above. Add the same real URL to GitHub **About → Website**.

## Team

- **Leader:** Md. Sorowar Mahabub Rabby, MSc Research Mode (pursuing), Faculty of Engineering & Built Environment, Universiti Kebangsaan Malaysia. Email: sorowar.cse1@gmail.com.
- **Member 2:**  Dr. Hasniza bt Hambali, PhD (Year 3), Faculty: Faculty of Engineering & Built Environment (FKAB), University: Universiti Kebangsaan Malaysia (UKM).


## License and acknowledgments

Keep the repository's existing `LICENSE`, `THIRD_PARTY_NOTICES.md` and font license. Acknowledge Groq, Frankfurter, Supabase and upstream open-source components. The submission documents describe this implementation and its measured scope; they do not certify regulatory or production readiness.
