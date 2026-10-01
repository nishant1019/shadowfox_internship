# Customer & Revenue Analysis (Intermediate Level)

ShadowFox Data Analyst Internship: Intermediate Level task.
Customer, revenue and segment analysis on a synthetic e-commerce dataset (2024-2025): data cleaning, exploratory analysis, trend identification, RFM segmentation, and insight-driven recommendations.

## Deliverable
`output/report.md` (with supporting charts in `output/charts/`)

| Section | Contents |
|---|---|
| Business questions | 5 questions the analysis answers |
| Data preparation | Join, quality checks, assumptions |
| Findings | Seasonality, repeat purchase behaviour, cohort retention, revenue concentration (Pareto), RFM segments, channel/segment/category comparison |
| Interpretation | Why the patterns likely occur, with explicit caveats on correlation vs causation |
| Recommendations | 5 concrete, data-linked actions |
| Limitations | What the synthetic data and analysis can't tell you |

## Dataset
Synthetic e-commerce orders and customers (`data/ecom_customers.csv`, `data/ecom_orders.csv`): 3,000 customers, ~6,200 orders across 2024-2025, with signup date, segment, region, acquisition channel, order category, value and returns.
Generated with a fixed random seed so results are reproducible. **Replace with a real dataset** (e.g. Kaggle "Online Retail II") with matching column names before final submission, and re-run `scripts/analysis.py` — the report regenerates automatically from whatever data is in `data/`.

## How to run
```bash
pip install -r requirements.txt
python scripts/analysis.py
```
This writes `output/report.md` and 7 PNG charts to `output/charts/`.

## Methodology notes
- **Net revenue** excludes returned orders (assumption: a return is a full refund) — see report section 2.
- **Cohort retention** uses the customer's first-order quarter as the cohort and only reports cohorts with at least 6 months of observable history, so recent cohorts aren't penalized for not yet having had time to re-order.
- **RFM segmentation** uses quartile scoring on Recency, Frequency and Monetary value, then maps the 4x4x4 combinations to five human-readable segments (Champions, Loyal/Active, New/Promising, At Risk (high value), Dormant).
