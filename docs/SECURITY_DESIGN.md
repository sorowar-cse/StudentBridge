# StudentBridge v4 — Security design and operational limits

This document describes implemented boundaries and the limits of the evidence. It is operational documentation, not a certification or a claim of perfect security.

## Threat boundary

An ordinary authenticated student may supply malicious questions, call public REST endpoints directly, alter IDs, retry execution, race requests, or attempt role escalation. Another student must not receive their private profile or ledger. The app operator, cloud runtime, Supabase administrator and secret store remain trusted. A fully compromised host/database owner is outside the protection claim.

## SAGE-FX composition

The six integrated ideas are source retrieval, structured two-model plan/review, deterministic Decimal tools, Isolation Forest with split-conformal anomaly ranks, HMAC-signed capabilities with atomic execution, and protected storage/audit. It is a named engineering integration, not proof that a new cryptographic or research algorithm has been invented. AI planning has no reference to an execution capability.

| Control | Enforcement | Verification |
|---|---|---|
| Authentication | Supabase verifies email/password and `/auth/v1/user`; app has a 30-minute absolute session; tokens remain in one Streamlit session | Adapter/session tests; own hosted login still required |
| Controlled enrollment | Public signup disabled by owner; confirmed dashboard-created accounts; SQL enrollment mutex/cap 15 | SQL cap, re-enrollment and unconfirmed-user checks |
| Own-row reads | RLS on every `sb_*` app table; publishable key + user JWT, no service-role key in app | PostgreSQL RLS tests; live two-account checker provided |
| Write authority | App users have SELECT-only table grants; security-definer RPCs validate `auth.uid()`, role and bounds; helper schema inaccessible | Direct write/role/key-access denial tests |
| Profiles | AES-256-GCM with fresh nonce and AAD binding user ID/document kind; master key stays in app secrets | Cross-user/kind decryption and ciphertext tests |
| Role tiers | Viewer/planner/executor live in owner-controlled membership table, not editable profile/JWT user metadata | SQL role checks and disabled UI actions |
| Quotes | Python signs canonical payload with derived HMAC-SHA256 key; SQL checks signature/owner/scope/expiry; no direct quote inserts | Signature tampering, ownership, expiry tests |
| Execution | Per-member PostgreSQL row mutex; debit/credit/receipt/audit in one transaction; quote ID unique | Single-debit replay and rollback checks; hosted multi-process race/load test not claimed |
| Approval | Checkbox plus final six characters before a fresh execution | SQL/UI checks; these are confirmation, not MFA |
| Amount limits | USD 2,000 equivalent/transfer, USD 5,000/day UTC, max 5 completed transfers/30 minutes; risk block cannot be overridden | SQL fixed-limit tests |
| AI quota | Atomic task reservations across accounts; default 20/user/day, 100/global/day, 3/global/minute; no question text stored | Global allowance test; provider may impose lower limits |
| Audit | Per-user HMAC chain plus owner-controlled head/sequence; chain verified before state-changing RPCs | Event corruption and blocked mutation tests |
| Input/model gates | Typed plans, source IDs, bounded question/output, fixed API hosts, no arbitrary URL/shell/eval tool | Existing adversarial and adapter tests |
| Truthful rates | Validate positive rate, pair and observation date; no silent synthetic fallback; date-consistency gate for composites | FX validation/regression tests and opt-in HTTP smoke |
| PDFs | Read-only generation from validated facts; English brand/header/footer; simulation/estimate status retained | PDF text checks and visual review |
| Account switch | New login clears old result/quote state and consent; logout clears local tokens even if provider unavailable | UI account-switch test |

## Privacy details

Profiles and saved plans are encrypted before upload. Sandbox balances, signed quote payloads and minimal operational event details are not application-encrypted; RLS protects account access to these rows. Do not claim that the entire database is ciphertext or that the operator cannot read data. Supabase Auth manages password storage; the application does not store cloud passwords in its tables.

Profile-based AI review passes selected numeric totals and generic institution context only. Other free-text assistant questions apply basic identifier masking and secret-pattern rejection, but this is not a complete anonymization guarantee. Users should not supply sensitive identifiers. Model responses are constrained action/plan data and never a source of exchange-rate facts or executable authority.

Owner-created, confirmed pilot accounts do not independently establish email ownership. This design intentionally avoids SMTP/signup callbacks for a small controlled trial. Forgotten-password recovery is an operator task; public self-service recovery is not present. Password changes inside the app require reauthentication with the current password.

The separate local `cloud_account_admin.py` utility may create/reset controlled accounts using an owner-entered privileged Auth key. It is never imported by the application, does not save that key, and is not an app-user role. The ordinary app continues to reject privileged API keys and uses the user's JWT for RLS.

Profile deletion removes saved encrypted student/plan documents. Ledger, audit and Auth account remain until an operator performs full account deletion. Own-data PDFs are personal exports, not public application assets.

## Known risks and limitations

- Free providers can sleep, pause, throttle or fail. No uptime or unlimited concurrent-AI guarantee is made.
- Paid service upgrades alone do not turn this into a production banking system or prove load capacity.
- Stable encryption/master key preservation is essential. Losing the key can make saved ciphertext unreadable. Secret rotation for existing encrypted data needs a migration plan.
- The quote/audit subkeys live in a restricted database schema. A database administrator remains trusted and can alter records/functions/keys. A signed audit head alone does not establish independent immutable storage. Keep external checkpoints for comparisons.
- Audit verifies recorded per-user events and their head; it does not prove every SQL row or every rejected request was independently observed. Rejected SQL statements roll back; denial evidence is in test outputs/provider logs, not guaranteed durable app events.
- Existing access JWTs may remain valid until provider expiry after logout/reset. App state is cleared immediately, but do not claim instantaneous global JWT revocation.
- Refresh/new-tab login persistence is not implemented as a permanent browser cookie. Tokens must never be placed in URL/query parameters.
- Current forecast uses monthly buckets, income-before-bills assumption, declared billing interval and user-provided values. It does not model intraday liquidity, taxes in the personal profile forecast, future fee changes or actual bank FX execution prices. The separate University Planner retains an explicit tax assumption.
- University references are curated and dated; fees/living costs require user confirmation. Historical/synthetic reference data must not be represented as newly verified official fees.
- Anomaly screening uses synthetic normal/calibration sets. It is not a real-world fraud classifier or fraud probability, and no claim of legal/compliance clearance is made.
- The app's six-character approval is a user confirmation step, not a second authentication factor.
- Optional local mode uses private local SQLite and its local key; it does not gain hosted persistence/RLS. The configured cloud mode fails closed without silently switching to local storage.
- No live Supabase/Groq account or published app is supplied in the ZIP. Hosted setup tests require the owner's keys and accounts. PostgreSQL WASM tests exercise actual SQL/RLS with a stubbed Auth claim, not a real provider token-validation test or independent penetration test.

## Before broader public use

Add verified signup/recovery and abuse controls, independent security review, migration/backup/restore practice, monitoring and retention, realistic load tests, provider-budget controls and incident handling. Actual regulated financial execution requires separately authorized integrations and operational review.
