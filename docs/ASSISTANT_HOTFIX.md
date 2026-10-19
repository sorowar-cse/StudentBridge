# StudentBridge v4 — Assistant correction

Prepared 20 October 2026 (Malaysia time) for the existing v4 project.

## What changed

- Model amounts in equivalent representations, such as `1e2`, `100.0000000000000` and `100 MYR`, no longer fail merely because of model formatting. The model's value must equal the one explicit amount in the original question, and any currency unit must match the source. The calculator receives the canonical amount derived from the validated original input. The strict user/ledger parser, currency precision, source grounding and currency-direction checks remain enforced.
- Provider authentication, access, quota and structured-response failures are classified separately from questions that need clarification. Raw provider response bodies, prompts and credentials are not shown.
- A narrow personal tuition question, such as `How much money i need to pay next semester fee and when to pay?`, reads the signed-in account's saved Student Profile. It displays the recorded amount/currency, fee period, billing interval and next unpaid due date. This local lookup makes no LLM call, uses no cloud AI allowance and sends no profile information to Groq. Labels support English, Bangla, Chinese and Malay.
- A new request clears the previous answer before processing, so a failed request cannot leave an older result displayed as its answer.
- The Guide for User examples and USER_GUIDE.md describe the personal fee lookup.

Personal answers are user-declared records, not an official invoice check. The lookup does not predict a later semester's fee, automatically advance an unpaid date, or record payment completion. Forecast questions continue to use My Forecast. No database migration is needed.

## Apply to an existing Windows installation

1. Stop Streamlit with Ctrl+C in its terminal.
2. Extract the patch ZIP to a temporary folder.
3. Copy the extracted contents into the existing StudentBridge repository root, where app.py is located. Merge folders and replace matching files. This is a patch, not a replacement for the complete project folder.
4. Run the focused regression checks from the repository root:

   ```powershell
   .\.venv\Scripts\python.exe -m pytest -q tests\test_assistant_hotfix.py tests\test_agent_budget.py tests\test_llm_adapter.py
   ```

5. Start Streamlit:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
   ```

6. Sign in and enable Groq cloud consent in Guide for User for model-assisted requests. Test `Convert 100 MYR to CNY`, then test the personal tuition question with a saved profile. Compare the displayed fee and date to My Student Profile. Retry forecast AI review as well.

The archive contains no .env, runtime folder, master key, API key or database. Preserve the existing local configuration and stored profiles. Dependencies are unchanged.

## Validation and limits

The complete Python suite passed: **227 tests**. This includes **35 new regression cases** covering model number formats, invented amounts/units, currency precision, classified provider errors, missing profiles, own-account lookup and four-language Streamlit rendering. The focused three-file run passed **61 tests**.

These new model outputs are controlled fixtures. They reproduce a plausible route to the reported parser message; the original failing live response was not captured, so its exact amount string is unknown. Live Groq conversion with this patch must still be checked on the owner's PC. The owner's earlier four successful synthetic API probes verified access/JSON responses before this patch; they do not establish end-to-end model accuracy.

The existing SQL/RLS design was not modified. This update is not an independent security audit or concurrency benchmark. Before the hosted two-account checker, use two dedicated blank accounts; keep the already saved personal profile intact.

## GitHub

The patched source, regression tests and these guides may be committed after review. Continue excluding .env, runtime/, .venv/, .streamlit/secrets.toml, private exports and raw cloud test reports. The patch does not replace the existing .gitignore.
