# Retail Sales Dashboard (Beginner Level)

ShadowFox Data Analyst Internship: Beginner Level task.
A spreadsheet-based analysis of 2025 retail sales: cleaning, key metrics, trend analysis, charts and a dashboard.

## Deliverable
`output/Beginner_Sales_Dashboard.xlsx`

| Sheet | Contents |
|---|---|
| Dashboard | 6 KPI cards, 4 charts (monthly trend, category, product, region), key findings |
| Analysis | Monthly, category, product and region tables (all formulas) |
| Insights | Cleaning log, metric choices, dashboard structure, findings, recommendations |
| Clean Data | 1,194 cleaned orders (Month, Sales, Profit are formulas) |
| Raw Data | Original messy data (before cleaning) |

## Dataset
Synthetic retail office-products dataset (Jan to Dec 2025; 4 regions, 4 categories, 12 products; currency in INR).
It was generated with a fixed random seed (`scripts/build_dashboard.py`) and deliberately includes data-quality problems so the cleaning steps can be demonstrated.

## Data cleaning
| Step | Rows affected |
|---|---|
| Exact duplicate rows removed | 30 |
| Rows dropped: missing Quantity | 6 |
| Missing Unit Price filled (product's standard price) | 15 |
| Region labels standardised (spaces / casing) | 140 |
| Text dates converted to real dates | 300 |
| **Final clean records** | **1,194** |

## Metrics
- **Sales** = Quantity x Unit Price x (1 - Discount)
- **Profit** = Sales - Quantity x Unit Cost; **Margin** = Profit / Sales
- Orders, Average Order Value, month-over-month growth, share of sales

## Key findings
- Sales peak in December; Nov + Dec deliver 23% of annual sales (strong seasonality), with a slow June to August.
- Standing Desk is the top product; Desk Organizer is the weakest.
- Furniture has the largest sales share but the lowest margin (27%); Accessories has the best margin (39%).
- South is the strongest region (31% of sales); East is the weakest (15%).
- Discounted orders earn a 28.4% margin vs 37.4% for full-price orders.

## Reproduce
```bash
pip install -r requirements.txt
python scripts/build_dashboard.py
```
Run from the repository root. This regenerates the workbook and the CSV files in `data/`.
(Open the workbook in Excel or LibreOffice; formulas recalculate on open.)

## Tools
Excel (formulas: SUMIFS, COUNTIFS, RANK, INDEX/MATCH, native charts), Python (pandas, openpyxl) for data generation and cleaning.
