# StudentBridge

**2026 Shenzhen International FinTech Competition, International Track**  
**Topic C: Cross-border & Student Finance Assistant**

StudentBridge helps international students record tuition schedules and living costs, inspect monthly cash shortfalls, convert supported currencies and approve controlled sandbox transfers. The pilot uses Python 3.12, Streamlit, Groq, Frankfurter and Supabase Auth/PostgreSQL, with at most 15 enrolled accounts.

**Live application:** https://studentbridge.streamlit.app/  
**Source repository:** https://github.com/sorowar-cse/StudentBridge  
**Version:** corrected v4 pilot. Documentation updated 20 October 2026.  
**Reviewed executable-code commit:** `ca161fbfdee8ef9594a577e767d1e7e0836fe242`

The live app requires an owner-provisioned pilot login. Public signup stays closed.

## Student workflow

1. Save your institution, programme, location, tuition amount/currency and next unpaid due date. Add living costs, savings and confirmed resources.
2. Review the monthly forecast, including the total funding gap and the deepest monthly timing shortfall.
3. Ask a personal tuition question to retrieve your recorded bill privately, or use an optional reviewed Groq request for supported financial tools.
4. Inspect dated FX observations and fictional provider fees. An executor may approve and execute a signed sandbox quote.
5. Download StudentBridge planning and receipt PDFs. English is the default interface, with Bangla, Chinese and Malay options.

## Financial and algorithm scope

Wallet balances, transfers and provider fee models are simulated. The app moves no real money. FX values are published references, not executable bank prices. Personal tuition and costs are user-provided; curated university references retain source URLs and checked dates. A forecast is a scenario calculation, not a prediction of future FX or verified university fees.

SAGE-FX is the project's integration of source retrieval, typed model planning and review, exact Decimal tools, synthetic anomaly screening and controlled execution. It uses established algorithms and security primitives. The contribution is the student workflow and bounded authority, without a claim of a new cipher or validated real-world fraud detection.

## Architecture

| Layer | Implementation |
|---|---|
| Interface | Streamlit, four languages, PDF exports |
| Interpretation | Optional Groq GPT-OSS 20B planner and 120B reviewer |
| Private tuition route | Authenticated saved-profile lookup, no LLM call |
| Financial tools | Python Decimal, currency precision and dated FX validation |
| Identity and persistence | Supabase Auth, user JWT, PostgreSQL RLS and bounded RPCs |
| Protection | AES-256-GCM documents, HMAC quotes/audit, roles, limits and atomic replay control |

Model agreement is not independent proof. The model has no ledger-execution tool. The app host and database administrator remain trusted.

## Run on Windows

Install Python 3.12, VS Code and Git. A fresh setup requires your own Supabase project and Groq key. Frankfurter needs no API key. No model download, local PostgreSQL or Docker is required.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\setup_local.py
```

Complete the wizard, disable public signup, run `supabase/schema.sql` then your generated private `runtime/setup_private.sql`, and provision pilot accounts. Follow the full [deployment guide](docs/submission/DEPLOYMENT.md) for these steps and Community Cloud deployment.

For an already configured PC, start directly:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Keep the same original master key across the PC and deployed app. Routine code updates do not require rerunning setup SQL or recreating accounts.

## Tests and evidence

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\doctor.py
.\.venv\Scripts\python.exe scripts\evaluate.py --provider offline
```

| Record | Result and scope |
|---|---|
| Latest local corrected-code suite | 227 passed, including UI, financial and security fixtures |
| Owner offline regression | 366/366 authored synthetic cases, zero LLM calls |
| Owner Supabase checker | Six actual service checks passed; document isolation, grants, encryption round trip and audit |
| Owner Groq diagnostic | Four synthetic API/schema checks passed, HTTP 200 |
| Original SQL suite | 23 historical PGlite checks, real SQL with a stubbed Auth claim |
| Live acceptance | Owner confirmed login, saved profile, AI, conversion, forecast, PDF and translated UI |

Owner results are console reports until the original sanitized files are attached. The offline result is not LLM accuracy. Deployed same-quote replay, reboot persistence, targeted role/limit evidence and measured concurrency remain separate checks. A 15-account enrollment cap is not a 15-concurrent-user benchmark.

See [testing](docs/submission/TESTING.md), [test cases](docs/submission/TEST_CASES.csv), [evidence status](docs/submission/EVIDENCE_STATUS.md), [technical documentation](docs/submission/TECHNICAL_DOCUMENTATION.md) and the [security self-assessment](docs/submission/SECURITY_SELF_ASSESSMENT.md). The original [developer guide](DEVELOPER_GUIDE_BN.md) and [user guide](USER_GUIDE.md) remain available.

## Security and publishing

Use the Supabase publishable key and the user's JWT. Never put a service-role key in the app. Keep `.env`, `.streamlit/secrets.toml`, `runtime/`, `.venv/`, databases, keys, private evidence and real student exports out of GitHub. Retain the existing `.gitignore` and review staged changes. Losing the master key can make encrypted documents unreadable.

Public signup stays disabled. Only the owner assigns roles. The quote suffix is explicit confirmation, not MFA. No independent audit, regulatory approval or production payment readiness is claimed.

## Team

- **Leader:** Md. Sorowar Mahabub Rabby, Master of Science in Research Mode, pursuing, Faculty of Engineering & Built Environment, Universiti Kebangsaan Malaysia. Email: sorowar.cse1@gmail.com.
- **Member:** Dr. Hasniza bt Hambali, PhD, Year 3, Faculty of Engineering & Built Environment, Universiti Kebangsaan Malaysia. Email: p145746@siswa.ukm.edu.my.


## License and acknowledgments

Retain `LICENSE`, `THIRD_PARTY_NOTICES.md` and the included font license. Acknowledge Groq, Frankfurter, Supabase and the upstream open-source libraries. See the [competition announcement](https://ird.oou.cmu.ac.th/2026-shenzhen-international-fintech-competition/) for the official topic and submission rules.
