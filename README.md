# ShadowFox Data Analyst Internship

Work completed for the ShadowFox Data Analyst Internship, organised by task level.

| Level | Project | Deliverable | Tools |
|---|---|---|---|
| Beginner | [Retail Sales Dashboard](beginner-sales-dashboard/) | `Beginner_Sales_Dashboard.xlsx` | Excel (formulas, charts), Python (pandas, openpyxl) |
| Intermediate | [Customer & Revenue Analysis](intermediate-customer-analysis/) | `output/report.md` + 7 charts | Python (pandas, numpy, matplotlib) |

## Beginner: Retail Sales Dashboard
Cleaning, key metrics, trend analysis and an Excel dashboard on 2025 retail sales data (1,194 clean orders after removing duplicates and fixing missing or inconsistent values).

## Intermediate: Customer & Revenue Analysis
Seasonality, repeat purchase behaviour, cohort retention, revenue concentration, RFM segmentation, and channel/segment/category comparison, ending in five data-linked recommendations.

## Running the projects
Each project is self-contained with its own README, data and requirements:

```bash
cd beginner-sales-dashboard        # or intermediate-customer-analysis
pip install -r requirements.txt
python scripts/build_dashboard.py  # beginner
python scripts/analysis.py         # intermediate
```

Both projects use synthetic datasets generated with fixed random seeds, so results are reproducible.
