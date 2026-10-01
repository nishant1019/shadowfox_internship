"""Intermediate level: customer & revenue analysis (retention, concentration, RFM, segments, seasonality)."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 130})
BLUE, ORG, GREY = "#1F3864", "#E07B39", "#9AA5B1"

# ---------------- 1. LOAD + CLEAN ----------------
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "output")
CHARTS = os.path.join(OUT, "charts")
os.makedirs(CHARTS, exist_ok=True)

cust = pd.read_csv(os.path.join(DATA, "ecom_customers.csv"), parse_dates=["signup_date"])
orders = pd.read_csv(os.path.join(DATA, "ecom_orders.csv"), parse_dates=["order_date"])
checks = {"duplicate order_ids": int(orders.order_id.duplicated().sum()),
          "orders with unknown customer": int((~orders.customer_id.isin(cust.customer_id)).sum()),
          "missing values": int(orders.isna().sum().sum()),
          "non-positive order values": int((orders.order_value <= 0).sum()),
          "orders before signup": int((orders.merge(cust, on="customer_id").eval("order_date < signup_date")).sum())}
orders = orders.drop_duplicates("order_id")
orders["month"] = orders.order_date.dt.to_period("M")
# Net revenue excludes returned orders (assumption: returned = fully refunded)
orders["net_value"] = np.where(orders.returned, 0, orders.order_value)
df = orders.merge(cust, on="customer_id")

gross, net = orders.order_value.sum(), orders.net_value.sum()
n_orders, n_cust = len(orders), orders.customer_id.nunique()
ret_rate = orders.returned.mean()

# ---------------- 2. SEASONALITY ----------------
m = orders.groupby("month").agg(revenue=("net_value", "sum"), orders=("order_id", "count"))
fig, ax = plt.subplots(figsize=(9, 4)); ax.bar(m.index.astype(str), m.revenue / 1e6, color=BLUE)
ax.set_title("Monthly net revenue (INR million)", loc="left", weight="bold"); ax.tick_params(axis="x", rotation=90); ax.set_ylabel("INR M")
fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "01_monthly_revenue.png")); plt.close()
by_moy = orders.assign(moy=orders.order_date.dt.month).groupby(["moy"]).net_value.sum()
q4_share = by_moy.loc[[10, 11, 12]].sum() / by_moy.sum()
yoy = orders.assign(y=orders.order_date.dt.year).groupby("y").net_value.sum()

# ---------------- 3. REPEAT BEHAVIOUR ----------------
per_c = orders.groupby("customer_id").agg(n=("order_id", "count"), rev=("net_value", "sum"), first=("order_date", "min"), last=("order_date", "max"))
repeat_rate = (per_c.n > 1).mean()
freq = per_c.n.clip(upper=8).value_counts().sort_index()
fig, ax = plt.subplots(figsize=(7, 4)); ax.bar(freq.index.astype(str).str.replace("8", "8+"), freq.values, color=BLUE)
ax.set_title("Customers by number of orders", loc="left", weight="bold"); ax.set_xlabel("Orders placed"); ax.set_ylabel("Customers")
fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "02_order_frequency.png")); plt.close()
gaps = orders.sort_values("order_date").groupby("customer_id").order_date.diff().dt.days.dropna()
median_gap = gaps.median()

# ---------------- 4. COHORT RETENTION ----------------
orders["cohort"] = orders.customer_id.map(per_c["first"]).dt.to_period("Q")
orders["age_m"] = ((orders.order_date.dt.year - orders.customer_id.map(per_c["first"]).dt.year) * 12 +
                   (orders.order_date.dt.month - orders.customer_id.map(per_c["first"]).dt.month))
act = orders.groupby(["cohort", "age_m"]).customer_id.nunique().unstack(fill_value=0)
size = orders.groupby("cohort").customer_id.nunique()
ret = act.div(size, axis=0).iloc[:, :7]
ret = ret[ret.index.astype(str) <= "2025Q2"]  # only cohorts with >=6 months of observable history
fig, ax = plt.subplots(figsize=(8, 3.6)); im = ax.imshow(ret.values, cmap="Blues", vmin=0, vmax=0.5, aspect="auto")
ax.set_xticks(range(ret.shape[1])); ax.set_xticklabels([f"M{i}" for i in ret.columns]); ax.set_yticks(range(len(ret))); ax.set_yticklabels(ret.index.astype(str))
for i in range(ret.shape[0]):
    for j in range(ret.shape[1]): ax.text(j, i, f"{ret.values[i,j]:.0%}", ha="center", va="center", fontsize=8, color="white" if ret.values[i, j] > .3 else "black")
ax.set_title("Cohort retention (% of cohort ordering in month N after first order)", loc="left", weight="bold", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "03_cohort_retention.png")); plt.close()
m1_ret = ret[1].mean(); m3_ret = ret[3].mean()

# ---------------- 5. REVENUE CONCENTRATION (PARETO) ----------------
s = per_c.rev.sort_values(ascending=False).reset_index(drop=True)
cum = s.cumsum() / s.sum(); pct_c = (np.arange(1, len(s) + 1)) / len(s)
top20_share = cum[int(len(s) * .2) - 1]; top10_share = cum[int(len(s) * .1) - 1]
fig, ax = plt.subplots(figsize=(6.5, 4)); ax.plot(pct_c * 100, cum * 100, color=BLUE, lw=2); ax.plot([0, 100], [0, 100], "--", color=GREY)
ax.axvline(20, color=ORG, ls=":"); ax.annotate(f"Top 20% of customers\n= {top20_share:.0%} of revenue", (20, top20_share * 100), (35, 55), arrowprops=dict(arrowstyle="->", color=ORG))
ax.set_xlabel("% of customers (ranked by revenue)"); ax.set_ylabel("Cumulative % of revenue"); ax.set_title("Revenue concentration", loc="left", weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "04_pareto.png")); plt.close()

# ---------------- 6. RFM SEGMENTATION ----------------
snap = orders.order_date.max() + pd.Timedelta(days=1)
rfm = per_c.assign(recency=(snap - per_c["last"]).dt.days, frequency=per_c.n, monetary=per_c.rev)
rfm["R"] = pd.qcut(rfm.recency.rank(method="first", ascending=False), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["F"] = pd.qcut(rfm.frequency.rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["M"] = pd.qcut(rfm.monetary.rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
def seg(r):
    if r.R >= 3 and r.F >= 3 and r.M >= 3: return "Champions"
    if r.R >= 3 and r.F >= 2: return "Loyal / Active"
    if r.R >= 3: return "New / Promising"
    if r.F >= 3 and r.M >= 3: return "At Risk (high value)"
    return "Dormant"
rfm["segment"] = rfm.apply(seg, axis=1)
rs = rfm.groupby("segment").agg(customers=("n", "size"), revenue=("rev", "sum")).assign(rev_share=lambda d: d.revenue / d.revenue.sum()).sort_values("revenue", ascending=False)
fig, ax = plt.subplots(figsize=(7.5, 3.6)); ax.barh(rs.index[::-1], rs.rev_share[::-1] * 100, color=BLUE)
for i, (c, v) in enumerate(zip(rs.customers[::-1], rs.rev_share[::-1] * 100)): ax.text(v + .5, i, f"{v:.0f}% ({c:,} cust.)", va="center", fontsize=8)
ax.set_xlim(0, rs.rev_share.max() * 100 * 1.3); ax.set_title("Revenue share by RFM segment", loc="left", weight="bold"); ax.set_xlabel("% of revenue")
fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "05_rfm.png")); plt.close()

# ---------------- 7. SEGMENT / CHANNEL / CATEGORY ----------------
def cmp(col):
    t = df.groupby(col).agg(customers=("customer_id", "nunique"), orders=("order_id", "count"), rev=("net_value", "sum"))
    t["rev_per_cust"] = t.rev / t.customers; t["orders_per_cust"] = t.orders / t.customers
    t["repeat_rate"] = per_c.assign(k=cust.set_index("customer_id")[col]).groupby("k").n.apply(lambda x: (x > 1).mean())
    return t.sort_values("rev_per_cust", ascending=False)
seg_t, ch_t, reg_t = cmp("segment"), cmp("channel"), cmp("region")
cat_t = df.groupby("category").agg(rev=("net_value", "sum"), orders=("order_id", "count"), ret=("returned", "mean")).sort_values("rev", ascending=False)
cat_t["share"] = cat_t.rev / cat_t.rev.sum()
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
axs[0].bar(ch_t.index, ch_t.rev_per_cust, color=BLUE); axs[0].set_title("Revenue per customer by acquisition channel (INR)", loc="left", fontsize=9, weight="bold"); axs[0].tick_params(axis="x", rotation=25)
axs[1].bar(ch_t.index, ch_t.repeat_rate * 100, color=ORG); axs[1].set_title("Repeat-purchase rate by channel (%)", loc="left", fontsize=9, weight="bold"); axs[1].tick_params(axis="x", rotation=25)
fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "06_channels.png")); plt.close()
fig, ax = plt.subplots(figsize=(7, 3.6)); ax.barh(cat_t.index[::-1], cat_t.share[::-1] * 100, color=BLUE)
ax.set_title("Revenue share by category (%)", loc="left", weight="bold"); fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "07_categories.png")); plt.close()

# ---------------- REPORT ----------------
f = lambda x: f"{x:,.0f}"
def table(t, spec):
    head = "| " + (t.index.name or "") + " | " + " | ".join(h for h, _, _ in spec) + " |\n|---|" + "---|" * len(spec) + "\n"
    return head + "\n".join(f"| {i} | " + " | ".join(fm(r[c]) for _, c, fm in spec) + " |" for i, r in t.iterrows())
pct = lambda x: f"{x:.0%}"
best_ch, worst_ch = ch_t.rev_per_cust.idxmax(), ch_t.rev_per_cust.idxmin()
best_rep = ch_t.repeat_rate.idxmax(); champ = rs.loc["Champions"] if "Champions" in rs.index else None
rep = f"""# Customer & Revenue Analysis - E-commerce (2024-2025)

> Data: synthetic e-commerce dataset (`data/ecom_orders.csv`, `data/ecom_customers.csv`) - {n_cust:,} customers, {n_orders:,} orders.
> Replace with a real dataset (e.g. Online Retail II) and re-run `analysis.py`; the report numbers regenerate automatically.

## 1. Business questions
1. Is revenue seasonal, and how large is the peak?
2. Do customers come back? How quickly do cohorts decay?
3. How concentrated is revenue among a few customers?
4. Which customer groups (RFM), segments and acquisition channels create the most value?
5. What should the business do differently?

## 2. Data preparation
- Joined orders to customers on `customer_id`; parsed dates; built `month`, cohort and RFM fields.
- Quality checks: {checks}. No rows needed removal; all checks passed unless a non-zero count is listed.
- **Assumption:** returned orders ({ret_rate:.1%} of orders) are fully refunded, so *net revenue* excludes them. Gross INR {f(gross)} -> net INR {f(net)}.

## 3. Findings
### 3.1 Seasonality
![monthly](charts/01_monthly_revenue.png)

Oct-Dec produce **{q4_share:.0%}** of revenue (25% if demand were flat) - a modest seasonal lift, not a dramatic spike. Part of the rising line also reflects a growing customer base: net revenue 2024 = INR {f(yoy.get(2024,0))}, 2025 = INR {f(yoy.get(2025,0))}.

### 3.2 Repeat purchase behaviour
![freq](charts/02_order_frequency.png)

**{repeat_rate:.0%}** of customers ordered more than once; the median gap between consecutive orders is **{median_gap:.0f} days**.

### 3.3 Cohort retention
![cohort](charts/03_cohort_retention.png)

On average only **{m1_ret:.0%}** of a cohort orders again in month 1 and **{m3_ret:.0%}** in month 3 - retention decays quickly, meaning most value must be won in the first weeks.

### 3.4 Revenue concentration
![pareto](charts/04_pareto.png)

The top 10% of customers generate **{top10_share:.0%}** of revenue and the top 20% generate **{top20_share:.0%}**. Losing a few high-value accounts would hurt disproportionately.

### 3.5 RFM segments
![rfm](charts/05_rfm.png)

{table(rs.rename_axis("Segment"), [("Customers","customers",lambda x:f"{x:,}"),("Revenue (INR)","revenue",f),("Revenue share","rev_share",pct)])}

### 3.6 Segments, channels, categories
![channels](charts/06_channels.png)

{table(ch_t.rename_axis("Channel"), [("Customers","customers",lambda x:f"{x:,}"),("Rev / customer","rev_per_cust",f),("Orders / customer","orders_per_cust",lambda x:f"{x:.2f}"),("Repeat rate","repeat_rate",pct)])}

{table(seg_t.rename_axis("Segment"), [("Customers","customers",lambda x:f"{x:,}"),("Rev / customer","rev_per_cust",f),("Repeat rate","repeat_rate",pct)])}

![cats](charts/07_categories.png)

{table(cat_t.rename_axis("Category"), [("Net revenue","rev",f),("Share","share",pct),("Return rate","ret",pct)])}

## 4. Interpretation (why might this happen?)
- **Seasonal lift** is consistent with festive-season buying, but it is modest; the customer base also grows over time, so not all growth is seasonal.
- **Fast retention decay** suggests weak post-purchase engagement: after the first order there is no reason to return.
- **Concentration** is typical of e-commerce where a small group buys frequently and in higher-value categories/segments.
- **Channel differences**: {best_ch} brings the highest revenue per customer, {worst_ch} the lowest; {best_rep} has the best repeat rate. Cost data is not in the dataset, so channel *profitability* cannot be judged - only value per customer.
- Correlation is not causation: differences between channels/segments may reflect who is targeted, not channel quality.

## 5. Recommendations
1. **Onboarding & win-back flows**: trigger emails at ~day {int(median_gap)} (the median reorder gap) with category-relevant offers to lift month-1/3 retention.
2. **Protect top customers**: create a loyalty / account-manager tier for the top 10-20% and "At Risk (high value)" RFM group.
3. **Shift acquisition spend** toward {best_ch}/{best_rep}-type channels after checking cost per acquisition; review {worst_ch}.
4. **Prepare for Q4**: pre-build inventory and campaigns from September; run a low-season promotion to smooth demand.
5. **Reduce returns** in the highest-return category (see table) through better product info and sizing/fit guidance.

## 6. Limitations
Synthetic data; no cost/margin data; returns assumed fully refunded; cohort retention limited to cohorts with >=6 months of history.
"""
open(os.path.join(OUT, "report.md"), "w").write(rep)
print(checks); print(f"gross {gross:,.0f} net {net:,.0f} ret {ret_rate:.3f} repeat {repeat_rate:.2f} gap {median_gap} q4 {q4_share:.2f} m1 {m1_ret:.2f} m3 {m3_ret:.2f} top10 {top10_share:.2f} top20 {top20_share:.2f}")
print(rs); print(ch_t.round(2)); print(seg_t.round(2)); print(cat_t.round(3)); print(ret.round(2))
