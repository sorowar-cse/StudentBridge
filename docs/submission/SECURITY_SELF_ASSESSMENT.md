# StudentBridge Security Self Assessment

Competition pilot assessment

2026 Shenzhen International FinTech Competition International Track

Topic C

Application version 4.0.0

Assessment owner: Md. Sorowar Mahabub Rabby

Team member: Dr. Hasniza bt Hambali

Assessment date: 20 October 2026

Reviewed repository: https://github.com/sorowar-cse/StudentBridge

Reviewed commit: ca161fbfdee8ef9594a577e767d1e7e0836fe242

Hosted environment: https://studentbridge.streamlit.app/



## 1 Assessment conclusion

StudentBridge implements controlled student-finance planning and simulated transfer execution with separate model, application and database authority. The current record combines 227 passing local Python tests, historical isolated SQL checks, the owner's six passing actual Supabase checks and four passing Groq synthetic API probes. The owner also confirmed the deployed planning interface worked. The assessment does not include an independent penetration test, a concurrent-user load test or a recorded deployed ledger-race test.

The release supports a controlled competition demonstration. The team must attach the remaining execution evidence in Section 6 before claiming those specific checks passed. This conclusion does not authorize real payment processing or unrestricted public registration. A 15-account enrollment cap is an access control rather than a measured concurrent-user capacity claim.

### 1.1 Assessment method

We reviewed the implementation modules, database grants and RPCs, synthetic request provenance, 227 passing current Python tests and 23 historical PostgreSQL checks on the unchanged SQL implementation. The PostgreSQL tests execute real RLS and pgcrypto in PGlite but stub the Auth claim. They do not test the cloud provider's actual JWT verification or multi-process network races. The owner-supplied console excerpts and deployed acceptance confirmations extend that evidence. Original hosted log files, exact run timestamps and the reviewed commit still need to accompany the submission.

| Evidence state | Meaning |
|---|---|
| Verified in development | A recorded test exercises the stated control within its defined scope |
| Owner service result reported | Owner supplied console output or manual confirmation; attach the corresponding source file or capture |
| Implemented awaiting targeted hosted evidence | Local tests exist, but that particular deployed operation still needs a recording |
| Operator procedure | A person must configure or perform the control correctly |
| Residual limitation | A known boundary remains outside the release claim |

### 1.2 Assets and trust boundary

Protected assets include account sessions, private student profiles, saved plans, API/master keys, simulated balances, signed quote payloads and account audit history. The ordinary-user threat model includes malicious prompts, direct REST calls, altered IDs, repeated execution attempts and role escalation.

Supabase Auth, the app runtime, secret store and database administrator remain trusted. An operator with both code/secret access and database privileges can defeat these controls. No claim of protection against that operator or a fully compromised host is made.

## 2 Permission tiers

| Capability | Viewer | Planner | Executor |
|---|---|---|---|
| Read own data and calculate | Allowed | Allowed | Allowed |
| Save or delete own planning profile | Allowed | Allowed | Allowed |
| Compare fictional transfer options | Allowed | Allowed | Allowed |
| Create signed executable quote | Denied | Allowed | Allowed |
| Execute sandbox transfer | Denied | Denied | Allowed after gates |
| Add simulated funds | Denied | Denied | Allowed |
| Change application role | Denied | Denied | Denied |

The owner assigns roles in public.sb_members. Roles do not come from user-editable profile fields. The app uses a publishable key with the authenticated user's JWT. Table grants permit own-row reads through RLS, while all ordinary writes use bounded security-definer functions. Those functions check auth.uid(), current membership, role and operation-specific limits. UI disabling is a convenience, not the primary security boundary.

Public signup must remain disabled. The team creates confirmed pilot accounts. This confirmation does not independently prove email ownership. An owner-only account-management utility prompts for a separate privileged Auth key outside the app runtime and does not save it.

## 3 Control register

| ID | Implemented control | Development evidence | Hosted status |
|---|---|---|---|
| SC01 | Session-scoped Auth client and 30-minute app lifetime | Token separation, refresh and expiry tests | Hosted login reported working; expiry/refresh behavior not separately recorded |
| SC02 | Atomic enrollment cap of 15 | Account 16 rejected in isolated SQL | Configuration cap confirmed as 15; live cap-exhaustion test not claimed |
| SC03 | Own-row RLS and denied direct writes | SQL cross-account and role-update denials | Owner checker passed cross-account REST, anonymous denial and direct role-update denial |
| SC04 | AES-GCM document encryption with user/kind AAD | Cross-user/kind authentication failures | Owner checker passed encrypted own-document round trip |
| SC05 | Server-signed canonical quotes | Invalid and altered signatures rejected | Targeted deployed tamper evidence pending |
| SC06 | Role, expiry and explicit approval | SQL role, expiry and confirmation checks | Targeted viewer/planner/expiry evidence pending |
| SC07 | Atomic ledger and unique quote receipt | One debit on retry; rollback on failure | Owner-confirmed deployed replay and matching CSVs; concurrent network-race test pending |
| SC08 | Per-transfer, daily and frequency limits | SQL limit checks | Dedicated hosted limit tests pending |
| SC09 | Per-user HMAC audit chain | Event alteration detected in isolated tests | Owner checker verified both users' audit chains |
| SC10 | Typed plans and grounded tool inputs | Schema, amount, direction and adversarial tests | Four Groq schema probes passed; app assistant and review owner-confirmed |
| SC11 | Bounded shared AI reservations | Global/minute and daily SQL checks | Hosted quota-exhaustion and concurrency not measured |
| SC12 | Account-switch clearing and profile deletion | UI/SQL isolation and deletion tests | Saved checker confirms deletion isolation; owner confirms reboot persistence |

The implemented risk model adds a synthetic-distribution anomaly gate to the fixed limits. Its output is not a fraud probability. The six-character approval is user confirmation and is not MFA. Model agreement supplements deterministic validation but cannot establish financial truth by itself.

## 4 Data protection and secrets

Student profile and saved-plan documents are encrypted before upload. Each AES-GCM encryption uses a fresh nonce and associated data tied to user and document kind. The stable master key stays in application secrets. Different derived keys serve profile encryption, quote signing and audit functions. The private SQL installs signing/audit subkeys in a schema inaccessible to ordinary app users.

Sandbox ledger amounts, signed quote payloads and minimal event details remain readable to their owner through RLS. They are not all application-encrypted. A profile-based AI priority review sends selected numeric totals and generic study context, excluding university name, department, email and private note. Free-text masking is limited and is not a guarantee of complete anonymization. Narrow personal-tuition questions use an authenticated profile lookup without sending that profile to Groq. The lookup does not allow an account ID from the question.

Secrets belong in the local .env or Streamlit Cloud Secrets. The Git repository excludes .env, runtime files, databases and real exports. An accidental secret commit requires revocation/rotation; deleting the latest file alone does not remove Git history. Rotating a lost/leaked master key for existing documents requires a planned re-encryption migration or matching recovery backup.

The app's profile-delete action removes profile/plan documents only. The account, sandbox ledger and event history remain until the owner performs full account deletion. The database foreign keys cascade app-record removal when the Auth account is deleted. Existing JWTs can remain valid until provider expiry; local app state clears immediately on sign-out.

## 5 Known risk register

Likelihood and impact are qualitative estimates for this controlled pilot. High means a plausible event can expose secrets, private data or financial authority within the simulation. Medium means meaningful disruption or incorrect planning. Low means limited impact under the stated controls. These are team judgments, not measured incident rates.

| ID | Risk | Current mitigation | Residual rating |
|---|---|---|---|
| R01 | App secrets or master key leak | Private files, owner-only administrative path, no keys in prompts | High if host/owner is compromised |
| R02 | Master key lost or changed | Preserve matching original .env and Cloud Secrets | High availability impact without recovery |
| R03 | Public signup enabled by later operator changes | Owner reported closed signup; enrollment cap remains | Medium configuration-drift risk |
| R04 | Model invents or misreads a request | Typed plans, source/direction checks, reviewer gate, read-only tools | Medium for unseen language/adversarial cases |
| R05 | User inputs wrong fee or period | Explicit confirmation, billing interval and provenance labels | Medium planning error risk |
| R06 | Old or unavailable exchange data | Date/pair validation, source labels, no silent fallback | Medium service/publication-gap risk |
| R07 | Transfer replay or cross-account request | Signed quote, ownership, member lock and unique receipt | Low in tested scope; hosted race test pending |
| R08 | Free-provider throttling or sleep | App allowances, deterministic tools, pre-demo service checks | Medium availability risk |
| R09 | Audit rollback or privileged tampering | HMAC chain, owner-controlled head and optional external checkpoint | High for malicious administrator |
| R10 | Synthetic risk model does not generalize | Fixed limits remain authoritative, synthetic scope disclosed | Medium; real-world fraud use unsupported |
| R11 | Session refresh/logout expectations | Absolute app lifetime, token clearing, new-login state reset | Medium while JWT/provider lifetime remains |
| R12 | Monthly forecast hides exact bill timing | Show due dates and timing gap; document income-before-bills assumption | Medium for intra-month shortages |

No finding here grants regulatory approval. Real remittance execution, credit scoring and production identity verification remain outside scope. Standard algorithms and libraries retain their upstream licenses; the team must acknowledge third-party components and preserve source attribution.

## 6 Security verification record

| Check family | Observed result | Interpretation |
|---|---|---|
| Latest local Python regression and UI | 227 passed in 30.25 seconds | Corrected final local code with UI/team changes |
| Owner PC suite | 227 passed in 28.16 seconds; exit code 0 | Final owner-run regression; original log and metadata attached |
| Original PostgreSQL RLS/RPC tests | 23 passed | Historical isolated SQL checks with a stubbed Auth claim |
| Owner offline request regression | 366 of 366 completed | Authored synthetic questions, zero model calls |
| Actual hosted Supabase checker | Six passes in owner console | Round trip, cross-account denial, direct-role denial, anonymous denial, independent deletion and both audit chains |
| Groq synthetic diagnostic | Four passes in owner console | Forecast/assistant planner and reviewer, HTTP 200 with valid structured responses |
| Deployed application acceptance | Owner confirms checks OK | Login, saved profile, planning/AI, conversion, PDF and translated interface |
| Saved profile after explicit reboot | Owner-confirmed pass | Profile and wallet persisted after reboot/relogin; SS07 captures |
| Deployed same-quote replay | Owner-confirmed pass | Original receipt and unchanged balances; SS05 and transfer CSVs |

E OWNER_REPORTED_VERIFICATION contains labelled console transcriptions. Attach the original sanitized files and screenshots before treating them as a complete evidence bundle. Exact run dates and the reviewed commit must come from the owner records rather than being inferred from this documentation date.

### 6.1 Release gates before submission

- Record GitHub URL and reviewed commit.
- Verify signup is disabled, project keys match, and the master key is preserved.
- Retain the completed doctor and two-account checker outputs; rerun only when configuration changes, evidence is missing or a new targeted test requires it.
- Attach the completed A/B document-isolation result. Add a separate wallet-isolation observation if claiming that hosted case.
- Confirm viewer/planner restrictions and an actual successful sandbox transfer.
- Show a repeated quote returns the original receipt with no second debit.
- Attach the passing Groq diagnostic and an actual consented app result with model/provider labels.
- Reboot the deployed app and confirm the saved profile persists.
- Inspect exports and video for secrets, account identifiers and unsupported claims.

### 6.2 Team completion record

Review owner: Md. Sorowar Mahabub Rabby

Second reviewer: Dr. Hasniza bt Hambali

Hosted check date and timezone: 2026-10-19T16:23:16.219157+00:00

Reviewed commit: [[COMMIT_SHA]]

Evidence index: docs/submission/EVIDENCE_INDEX.csv

Decision after completing the gates: [[TEAM_REVIEW_DECISION]]

This is the team's self-assessment. It is not an independent audit or certification. The team must update pending fields with observed results rather than assuming a successful deployment.

### 6.3 Supporting references

StudentBridge v4 source modules, supabase/schema.sql, tests and evaluation artifacts are the primary implementation evidence. A Technical Documentation explains architecture and algorithm details. C TESTING provides reproduction commands and case mapping. E Evidence Guide defines capture and disclosure procedures.

External background: Supabase RLS https://supabase.com/docs/guides/database/postgres/row-level-security and authenticated encryption https://cryptography.io/en/latest/hazmat/primitives/aead/. Accessed 20 October 2026. These references explain mechanisms; the implementation/test artifacts determine the claims in this assessment.

<!-- STUDENTBRIDGE_FINAL_VERIFICATION_START -->

## Final owner verification

Final owner verification: 227 passed in 28.16 seconds; exit code 0. Test time: 2026-10-20T03:11:50.6067086+08:00. The tested Git revision is 8cde4e49ca5e6f76f513d6e5de351073bf67ec0f. The saved Supabase checker records six passes at 2026-10-19T16:23:16.219157+00:00; this updater does not rerun that checker. The owner confirmed a six-month forecast of MYR 18,480 total cost, MYR 24,000 resources, zero overall funding gap and MYR 4,580 timing shortfall. The saved CSVs contain one USD 50.00 transfer, including a USD 0.40 fee, receiving CNY 329.31, and one matching completion audit event. The owner confirmed that replay returned the original receipt with wallet balances unchanged at USD 50.00 and CNY 329.31. Reboot/relogin preserved the profile and wallet and reproduced the forecast. Live Groq conversion and forecast review worked after resolving an HTTP 401 authentication error. UI outcomes are owner-confirmed observations. Unperformed hosted role, expiry, tamper, limit and concurrent-race checks remain pending.

<!-- STUDENTBRIDGE_FINAL_VERIFICATION_END -->
