# Reproducible synthetic walkthrough

These values are invented for a competition scenario. They are not UKM tuition facts. Use a dedicated synthetic account; do not record your actual fees, passwords or email.

## Forecast case

Choose MYR as the budget, tuition, living, resource and one-time currency. Select a future planning start date and set the tuition due date to that same date. Keep all dates in the same first monthly bucket. Use a six-month horizon and a one-time tuition invoice/programme total, not a repeating semester fee.

| Field | Input |
|---|---|
| University | UKM, with programme/department labeled synthetic if entered |
| Tuition | MYR 5,000 |
| Fee interval | Once / invoice total, interval 0 |
| Rent per month | MYR 700 |
| Food per month | MYR 600 |
| Transport per month | MYR 200 |
| Utilities per month | MYR 100 |
| Other living per month | MYR 200 |
| One-time expenses | MYR 1,000 |
| Reserve buffer | 10% |
| Confirmed income per month | MYR 4,000 |
| Savings and upfront funding | MYR 0 |
| Annual living-cost growth and FX stress | 0% |
| Note/source | SYNTHETIC competition scenario; not an official fee |

Expected total cost is MYR **18,480** and resources MYR **24,000**. Overall funding gap is zero, but the timing shortfall is MYR **4,580**. Monthly costs are 8,580 then 1,980 for each remaining month. Monthly closing balances are −4,580; −2,560; −540; 1,480; 3,500; 5,520. Income is assumed available before each bucket's bills. The important result is the early shortage despite a positive final balance.

If output differs, check horizon, first due date, recurring versus one-time fee, zero savings, reserve and growth assumptions. Do not alter a screenshot to match the expected number.

## Currency case

Use a modest exact-direction question such as “Convert 100 MYR to CNY.” In published mode retain the actual rate source and observation date; the answer varies with provider data. In illustrative offline mode disclose that fact. The forecast case above needs no foreign exchange service.

## Transfer case

Use the executor role and only simulated funds. Choose a small supported pair/amount, for example USD 50 to CNY, and a clearly synthetic recipient. Review the actual risk result before continuing. If it is blocked, preserve that result and create a different permitted small test after investigating; do not bypass the risk gate.

Record initial wallets, quote ID, approval, receipt and final wallets. Execute the **same** quote again before generating a replacement. Expected replay behavior is the original receipt with no further debit. A new quote is a new transaction and is not a replay test. The suffix is confirmation, not MFA. No bank payment is made.
