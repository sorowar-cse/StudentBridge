# Competition alignment — Topic C

Sources: [CMU announcement](https://ird.oou.cmu.ac.th/2026-shenzhen-international-fintech-competition/) and its linked [International Track problem/rules brief](https://drive.scmc.cmu.ac.th/s/2jKErkTJpFmcxYF), accessed 16 October 2026. Organizer rules and final instructions are authoritative; this mapping is our engineering assessment, not organizer approval.

Topic C concerns cross-border/student finance. The brief scores task completion 40%, security/compliance 30%, and innovation/interaction 30%. Its separate on-chain bonus applies to Topic F; StudentBridge does not claim that bonus.

| Requirement area | StudentBridge implementation | Evidence / owner action |
|---|---|---|
| Student finance task | User profile, actual tuition schedule, living costs, multi-currency forecast, funding and timing gaps | Run your own synthetic student walkthrough and download PDFs |
| Cross-border management | Supported published FX pairs, CNY/RMB alias, sensitivity scenarios, fee comparison | Latest dated FX output; fictional transfer providers explicitly labeled |
| Financial participation | Reviewed plans and exact tools; signed sandbox quote, explicit execution and receipt | Wallet/Audit logs and repeated-quote single-debit evidence |
| Permission tiers | Viewer, planner, executor; own-row RLS; immutable direct-write grants | SQL verification, role walkthrough, hosted two-account checker |
| Safety / explanations | Bounded model output, consent, fixed hosts, deterministic money and source validation, anomaly gate | Security design and Python/PostgreSQL tests; known risks disclosed |
| Interaction | English default, Bangla/Chinese/Malay, red/gold UI, guide and PDF exports | User/developer walkthrough and browser checks |
| Source / reproducibility | Python source, schema, requirements, README, setup/deployment guides, synthetic cases | Upload sanitized GitHub repository and insert its real URL |

## Submission items still requiring team finalization

The brief lists technical documentation, a presentation of at most 10 minutes, source with README/repository/deployment instructions/test cases, a security self-assessment and execution evidence. The general demo-video item is called optional (at most 5 minutes), while the non-on-chain execution-evidence item also mentions sandbox logs and demo video. Plan to supply a short video with execution evidence to cover that wording.

This v4 package provides application code, setup guidance, security design and test evidence. It does **not** claim that the final presentation, final security assessment, recorded video, registration or submission has been completed. Those deliverables follow the user's final project review.

Team action: replace `XXXXYYYY` member fields, check student/team eligibility and registration, configure your accounts, execute hosted checks, record the reviewed final app and supply actual GitHub/app links. The announced deadline is **20 October 2026, 23:59 UTC+8** (same local time in Malaysia). No email or submission is sent by this package.
