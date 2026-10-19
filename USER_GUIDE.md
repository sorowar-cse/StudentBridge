# StudentBridge v4 — Guide for User

StudentBridge helps international students organize tuition and living costs, understand currency conversion, and review simulated cross-border transfers. English is the default interface. Choose বাংলা, 中文 or Bahasa Melayu in the sidebar; calculations and permissions are unchanged by language.

## Sign in

Use the email/password assigned by the project team. Public registration is closed for this controlled pilot. Sessions last up to 30 minutes, and a browser refresh or new tab may require another sign-in. Ask the team for account/password recovery. Never share passwords or API keys in the assistant.

## Set up My Student Profile

Enter your university, campus, department/faculty, programme, study mode and location. The university reference list is a starting point; your own current fee and billing terms determine your personal plan.

Enter:

- Tuition amount/currency (including any applicable invoiced tax), fee period and next **unpaid** due date. The personal forecast does not add a separate tax rate.
- Actual billing interval in months for recurring tuition. A semester is not assumed to have the same duration at every university. A programme total or single invoice is counted once.
- Monthly rent, food, transport, utilities and other costs.
- One-time expenses, available savings, confirmed monthly income and confirmed funding.
- Planning start date, horizon and budget/report currency.
- Optional reserve buffer, living-cost growth and extra cost of foreign expenses.

Confirm the inputs and save. All values are user provided; confirmation does not mean StudentBridge independently verified an invoice or a university fee. A missing expense entered as zero makes the estimate incomplete. Edit the profile when costs change. Do not enter passport, bank-account or payment-card details.

The form groups tuition, living costs, one-time expenses and resources into separate currencies. The data model can hold per-category currencies; the current form uses one currency for all five living categories and one for the three resource fields. Use the relevant group currency consistently.

## Read My Forecast

Select **Calculate from my saved profile**. The app uses deterministic Decimal arithmetic, your billing schedule and the selected exchange-rate source. It displays:

- Estimated costs and declared resources.
- Overall funding gap over the full horizon.
- Largest monthly cash shortfall and the first shortfall period.
- Monthly tuition dates, costs, income and closing balances.

A final surplus can still hide an early tuition shortage. Check both gap metrics. Income is assumed available before bills in each monthly bucket; exact day-by-day liquidity is not modeled. Funding and savings are assumed available at the beginning. Buffer is a reserve, not a paid expense.

Growth is the declared annual percentage divided by 12 and compounded monthly on living costs. FX stress increases foreign-currency expenses relative to the budget currency; it does not predict future exchange rates or increase income. Future tuition increases are not invented. Reference dates and assumptions are shown.

Download the forecast/profile PDF if needed. PDFs have English labels. English institution/programme names provide consistent typography with the bundled font. Keep financial exports private.

## Currency Converter

Choose the source/target and amount. RMB is treated as CNY; CNH is separate when supported. Reverse direction if needed.

**Published reference rates** retrieves the latest available Frankfurter observation. Read its source and date: publication gaps/weekends are possible. These are reference prices; actual banks/remittance services can add fees/spreads. Available currency pairs depend on the provider.

**Illustrative reference rates** is an explicitly synthetic offline dataset. It supports repeatable offline calculation tests and must not be presented as today's market rate. Failed online requests never silently become synthetic results. Composite forecasts/quotes reject inconsistent observation dates.

The converter also shows ±5% and ±10% sensitivity scenarios. These are assumptions, not predictions.

## AI Assistant

Guide for User → Connections & calculation settings controls the engine:

- Built-in assistant: deterministic interpretation and tools, no LLM request.
- Groq cloud: model-assisted planning/review after consent.
- Ollama local: optional local LLM, available for PC use; not offered by the cloud configuration.

Use clear amounts/codes, such as `Convert 12000 BDT to RMB`. Other examples are collected in Guide for User. The profile-budget button opens your personal forecast. Its AI priority review sends numeric totals and generic study context; it excludes the university name, department, email and private note. Free-text questions should still contain no sensitive identifiers.

You can also ask `How much is my tuition fee and when should I pay?` after saving My Student Profile. This narrow personal lookup reads only the signed-in account's saved tuition amount, currency, fee period, billing interval and next unpaid due date. It uses no LLM and sends no profile data to Groq. Labels are available in English, Bangla, Chinese and Malay. It displays the recorded next unpaid bill; it does not independently verify an invoice, infer a later semester's amount, or mark a payment as completed. Update the profile when your actual invoice changes. Missing profiles prompt you to save the required details first.

For model-assisted conversions, equivalent model number formatting is accepted only after an exact Decimal comparison with the single amount in your original question. The amount used by the calculator is rebuilt from your validated input. Currency direction, currency precision, source checks and planner/reviewer agreement still apply. API authentication, quota and structured-response failures are displayed as request errors rather than as an unclear question.

The assistant has no transfer execution capability. A model cannot authorize payments or bypass confirmation. Structured outputs, exact tools and permission gates remain authoritative.

Cloud AI requests share bounded app allowances and provider limits. A reviewed task may call two models. If unavailable or limited, use the built-in assistant and calculators. There is no automatic provider or paid-plan switch.

## University Planner

Browse the 10-university reference catalogue, including UKM, UM, UTM, IIUC, IIUM and five Chinese universities. Read the source URL, checked date and fee classification. Living costs are editable assumptions, not guaranteed city prices.

This page is a standalone reference scenario. **My Student Profile / My Forecast** is the separate personal workflow. Saving a reference scenario does not overwrite your full student profile. The planning invoice is an unpaid estimate, not a university-issued invoice or proof of payment.

## Transfers, Wallet & Audit

All balances and transfers are simulated. Providers Campus, Value and Swift are fictional fee models, even when the reference exchange rate is online.

1. Add explicit simulated funds in Wallet if your executor role allows it.
2. Compare transfer options.
3. Create a signed quote and inspect amount, fees, source date and risk screening.
4. Before expiry, tick approval and type the quote's final six characters.
5. Execute once and download the receipt.

Quotes expire after 180 seconds. A retry of a completed quote returns the original receipt with a replay indicator; it does not debit again. Per-transfer, daily and frequency limits remain enforced. Statistical screening is trained/calibrated on synthetic data and is not a validated real-world fraud probability.

| Role | Compare / personal planning | Create quote | Execute / top up |
|---|---|---|---|
| Viewer | Yes | No | No |
| Planner | Yes | Yes | No |
| Executor | Yes | Yes | Yes, sandbox only |

Wallet & Audit exports your own activity. The cloud audit chain covers your account; it does not disclose other students' events. Save an exported head separately if comparing checkpoints later.

## Account & Privacy

Saved student profiles and plans use application-level authenticated encryption. Cloud tables restrict reads to the authenticated owner, and direct table writes are disabled for app users. Operators who control the app's secrets and database administration remain trusted.

Change a cloud account password using the current password. If forgotten, contact the team. **Delete my saved profiles and plan** removes the encrypted profile/plan documents; it retains the login account, sandbox ledger and operation history. Ask the team for full account deletion if needed.

Sign out before another person uses the browser. A new login clears previous account results and consent. Never distribute private financial PDFs or screenshots as public code assets.

## If something fails

- Cloud unavailable: retry later; the app does not create a replacement local account/database.
- FX unavailable: retry or deliberately choose illustrative offline references in Guide. Check the label before interpreting results.
- AI allowance/model problem: use built-in tools or contact the team; no real transaction was made.
- Profile integrity error: contact the developer; matching encryption keys must be restored.
- Unexpected fee: verify your own invoice and fee period; update your profile before recalculating.

The complete installation/deployment instructions are in `DEVELOPER_GUIDE_BN.md`. Source code and tests are included in the project.
