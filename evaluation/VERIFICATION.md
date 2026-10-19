# v4 verification scope

- Python: **192 passed**, including original regression tests, four-language UI flows, profile/forecast cases, adapter/session checks and owner-utility validation.
- SQL: **23 checks passed** using PGlite PostgreSQL, pgcrypto and real RLS/RPCs. Auth claims are stubbed. This is not hosted Supabase token validation or a multi-process load test.
- Synthetic offline benchmark: **366/366** regression cases completed; zero model calls. Generated/debugged cases are not blind generalization evidence.
- Live FX: six public pair checks returned usable dated observations; 165 catalogue entries were observed. This is a historical check, not a permanent coverage or same-day publication promise.
- Browser: local sign-in, dashboard, saved profile and forecast/PDF button; no observed page errors. PDF pages were rendered and visually reviewed.
- Ruff static checks passed.

No actual Groq inference, hosted Supabase account integration, public deployment, independent security audit or 15-concurrent-user load test was performed: the owner's accounts/credentials and hosted verification are still required. Run doctor.py --login and check_cloud_security.py after setup.

Raw results are alongside this file. Do not relabel synthetic metrics as real-world financial accuracy, fraud detection performance or production penetration-test results.
