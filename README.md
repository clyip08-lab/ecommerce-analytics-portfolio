# 🛒 E-Commerce Analytics Portfolio Project
> **End-to-end analytics system built on 110M+ row e-commerce event data**

> **Showcasing data engineering, SQL analytics, BI dashboarding, and product analytics thinking.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![PowerBI](https://img.shields.io/badge/Power%20BI-F2C811?style=flat&logo=powerbi&logoColor=black)

---

## Live Demo

**[View Live Streamlit Dashboard](https://clyip08-lab-ecommerce-analytics-portfol-streamlit-appapp-g6xeev.streamlit.app)**

---

## Project Overview

This is my first **AI-assisted end-to-end e-commerce analytics learning project**.
It was created to practise the workflow from data preparation and analytical
modelling to SQL metrics, dashboards, validation, and business interpretation.

**Raw Dataset:** Approximately 109.9M events across October and November 2019

**Analytical Sample:** 99,693 unique users and approximately 1.6M events

**Sampling Method:** 50,000 users were selected independently within each month
using monthly user-level random sampling. Events belonging to the selected users
were retained within that sampled month.

**Sampling Purpose:** User-level sampling preserves within-month event histories
for selected users better than random event-row sampling.

**Important Limitation:** Because October and November users were sampled
independently, the current dataset cannot support a reliable cross-month retention
rate or complete full-period RFM analysis. The current stage analysis is also
directional rather than a strict sequential funnel.

**Source:** [eCommerce behavior data from multi-category store](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store)

---

## Exploratory Business Questions

The project explores several e-commerce questions using the analytical sample.
The results should be interpreted together with the documented methodological limitations.

### Purchase Activity and Product Performance

> **Q1: How did observed purchase activity change from October to November?**
>
> The analytical sample contains approximately $7.4M in observed purchase value
> across 24,602 purchase events.
>
> Because the dataset does not contain an `order_id`, purchase events are used
> as a proxy and should not be described as confirmed orders.

> **Q2: Which products and categories contributed most to observed purchase value?**
>
> Electronics accounted for approximately 75.2% of observed purchase value
> in the analytical sample.
>
> The top 489 products, around 7.6% of products with observed purchases in
> the sample, accounted for 80% of observed purchase value.
>
> This indicates concentration within the sample but does not represent
> the complete platform catalogue.

### Customer Behaviour

> **Q3: Where is the largest stage-participation gap?**
>
> Monthly distinct-user counts show the largest numerical gap between viewing
> and cart activity.
>
> However, the current calculation does not enforce a same-session,
> same-product and time-ordered journey.
>
> It therefore creates a hypothesis to investigate product discovery,
> traffic relevance, offer attractiveness and price, rather than confirming
> a sequential conversion bottleneck.

> **Q4: When were purchase events most frequently observed?**
>
> Purchase-event activity was highest between approximately 10am and 2pm UTC.
>
> This may support a campaign-timing hypothesis only after customer time zones
> are confirmed and the timing is tested through a controlled experiment.

### Customer Analysis

> **Q5: Can the current sample measure cross-month retention?**
>
> No. October and November users were sampled independently, so cross-month
> overlap mainly reflects the sampling design rather than a reliable retention rate.
>
> A redesigned cross-month user sample is required.

> **Q6: What does the RFM analysis show?**
>
> The project contains exploratory RFM segmentation based on observed purchase behaviour.
>
> Because the dataset covers only two months and users were sampled independently
> by month, the segments should be validated before they are used for targeting
> or campaign decisions.

---

## Architecture

```text
Raw CSV
Approximately 110M events across October and November 2019
│
▼
Monthly User-Level Random Sampling
50,000 users selected independently per month
│
▼
Data Cleaning and Feature Engineering
Deduplication, null review, timestamp and event features
│
▼
Star-Schema Learning Model
fact_events plus supporting dimension tables
│
▼
MySQL Database
AI-assisted ETL workflow using SQLAlchemy
│
▼
Reusable KPI Views
Lightweight SQL views for selected metric logic
│
├──→ Purchase and Product Analysis
├──→ Exploratory RFM and Pareto Analysis
├──→ Directional Stage-Participation Analysis
├──→ Power BI Learning Dashboard
└──→ Streamlit Exploratory Dashboard
```

---

## 📊 Key Observations and Next Analytical Steps

| Observation | Sample Result | Appropriate Interpretation | Next Analytical Step |
|---|---:|---|---|
| Observed purchase value | Approximately $7.4M | Sum of values recorded on purchase events in the analytical sample | Reconcile against full-data aggregates if available |
| Purchase events | 24,602 | Purchase-event rows, not confirmed orders because the dataset has no `order_id` | Define an order-level rule if session and timestamp data allow |
| Average purchase-event value | $301.48 | Average value recorded per purchase event; not confirmed AOV | Analyse variation by month, category and product |
| Monthly buyer-to-viewer ratio | 11.72% | Directional ratio of distinct monthly buyers to viewers | Build a same-session, same-product and time-ordered funnel |
| Monthly cart-to-viewer ratio | 16.73% | The largest numerical stage-participation gap appears before cart | Segment by product, traffic source, price and customer type |
| Monthly buyer-to-carter ratio | 78.79% | Buyer and carter totals are not verified as one sequential journey | Validate event order within the same session and product |
| Electronics share | 75.2% of observed purchase value | High category concentration within the analytical sample | Review margin, supply, seasonality and full-population data before action |
| Product concentration | 489 products account for 80% of observed purchase value | Concentration among products with observed purchases in the sample | Monitor availability and product-page performance, then validate stability across periods |

---

## Analytical Implications and Next Steps

| Area | What the Current Analysis Suggests | What Is Needed Before Action |
|---|---|---|
| Stage participation | The largest numerical difference appears between viewing and cart activity | Build a same-session, same-product and time-ordered funnel, then segment the result |
| Traffic and offer quality | Weak pre-cart participation may relate to traffic relevance, product information, reviews, value perception, availability or price | Compare performance by traffic source, product, customer type, device and price segment |
| Category concentration | Electronics contributes a large share of observed purchase value in the analytical sample | Review margin, supply risk, business strategy, seasonality and full-population data before action |
| Product concentration | A relatively small group of products contributes most observed purchase value | Monitor availability and product-page performance, then test whether the concentration is stable across periods |
| Retention | The independently sampled monthly user sets cannot provide a reliable cross-month retention estimate | Sample users once across the combined period and retrieve all of their cross-month events |
| RFM | The current segments provide an exploratory view of observed buyer behaviour | Validate the scoring rules, observation period and complete user histories before targeting |
| Hourly activity | UTC purchase-event patterns may help generate campaign-timing hypotheses | Confirm customer time zones and run a controlled send-time test |

---

## 🗂️ Project Structure

```
ecommerce-analytics-portfolio/
│
├── data/
│   ├── raw/                          ← Original CSVs (not in Git)
│   ├── processed/                    ← Cleaned dataset
│   ├── samples/                      ← Monthly user-level random sample
│   └── exports/                      ← Star schema + analysis CSVs
│
├── notebooks/
│   ├── phase1_data_understanding.ipynb
│   ├── phase2_cleaning_features.ipynb
│   ├── phase3_star_schema.ipynb
│   ├── phase4_mysql_load.ipynb
│   ├── phase5_kpi_semantic_layer.ipynb
│   ├── phase6_core_analysis.ipynb
│   └── phase7_advanced_analytics.ipynb
│
├── sql/
│   ├── 01_schema_check.sql
│   ├── 02_revenue_by_month.sql
│   ├── 03_top_brands.sql
│   ├── 04_conversion_funnel.sql
│   ├── 05_hourly_pattern.sql
│   ├── vw_monthly_revenue.sql
│   ├── vw_conversion_funnel.sql
│   ├── vw_product_performance.sql
│   ├── vw_user_retention.sql
│   ├── vw_daily_kpis.sql
│   └── vw_brand_performance.sql
│
├── streamlit_app/
│   ├── app.py
│   ├── db.py
│   └── views/
│       ├── executive.py
│       ├── product_brand.py
│       ├── customer_segments.py
│       └── retention_cohort.py
│
├── dashboard/
│   └── ecommerce_dashboard.pbix
│
├── reports/
│   └── figures/                      ← 15 exported HTML charts
│
├── .gitignore
├── requirements.txt
└── README.md
```
---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python (pandas, numpy) | Data cleaning and feature engineering |
| Plotly | Interactive visualizations |
| MySQL 9.x | Relational database and star schema |
| SQLAlchemy | ETL pipeline (Python to MySQL) |
| Power BI | Executive BI dashboard |
| Streamlit | Live web analytics app |

---

## Dashboard Pages

| Live Streamlit Page | Purpose |
|---|---|
| Executive Overview | Observed purchase-value metrics, purchase-event trends, UTC activity patterns and directional monthly stage participation |
| Product and Brand | Observed purchase-value comparisons, brand-level ratios, category concentration and Pareto analysis |
| Customer Segments | Exploratory RFM segment distribution and directional category stage-participation ratios |

The original retention page has been removed from the live navigation pending
a redesign of the cross-month sampling methodology.

---

## Analytical Methods

- **Monthly User-Level Random Sampling** — preserves within-month events for selected users; independently sampled months limit cross-month analysis.

- **Star-Schema Learning Model** — separates the event-level fact table from descriptive product, user, session and date dimensions.

- **Reusable KPI Views** — lightweight SQL views that centralise selected metric logic; they are not a complete enterprise semantic layer or automatic guarantee of correctness.

- **Exploratory RFM Segmentation** — groups customers based on observed purchase behaviour, subject to sampling and observation-period limitations.

- **Retention Prototype** — retained as a learning exercise, but the current monthly sampling method cannot support a reliable retention conclusion.

- **Pareto Analysis** — measures concentration of observed purchase value among products with purchase events in the analytical sample.

- **Directional Stage-Participation Analysis** — compares monthly distinct-user counts across view, cart and purchase stages; it is not a strict sequential funnel.

---

## Limitations

| Area | Current Limitation | Required Improvement |
|---|---|---|
| Cross-month retention | October and November users were sampled independently, so user overlap cannot be interpreted as a reliable retention rate | Sample users once from the combined cross-month population and retrieve all of their events across both months |
| RFM analysis | Independent monthly sampling may omit some users' activity from the other month, affecting recency, frequency and monetary values | Use complete cross-month user histories and a longer observation period |
| Funnel analysis | Current metrics compare monthly distinct-user stage counts and do not enforce a same-session, same-product and time-ordered journey | Build sequential `view → cart → purchase` paths using user, product, session and timestamp fields |
| Order metrics | The dataset has no formal `order_id`, so purchase events are used as an order proxy | Report purchase-event counts and average purchase-event value, or define a defensible order-level rule |
| Sampling representativeness | Similar event-type proportions do not prove that all user, product, category and purchase-value distributions are unbiased | Compare additional distributions, repeated samples and full-data aggregates where possible |
| Product concentration | Pareto results cover products with observed purchases in the analytical sample, not the complete platform catalogue | Validate the concentration using full-population product and purchase data |
| Time coverage | The dataset covers only October and November 2019 and includes major shopping events such as 11.11 and Black Friday | Use a longer period to evaluate seasonality and normal performance patterns |
| Time zone | Event timestamps are recorded in UTC, so hourly patterns may not reflect users' local time | Map events to customer time zones before making campaign-timing decisions |
| Local processing | Monthly files were read in chunks but later combined in memory | Use a two-pass chunked workflow or an analytical engine such as DuckDB for more memory-efficient processing |

---
## Sampling Methodology

<details>
<summary>Why use monthly user-level sampling? (click to expand)</summary>

**Problem with random event-row sampling:**

Randomly selecting individual event rows can exclude other events belonging
to the same user. This can fragment the user's observed behaviour and weaken
user-level exploratory analysis.

**Current approach:**

The project selected 50,000 users independently within October and November
and retained the events belonging to those selected users within each sampled month.

The two monthly samples were then combined, producing 99,693 unique users
and approximately 1.6 million events.

**What this approach preserves:**

- It preserves the within-month events observed for selected users better than random event-row sampling.
- It supports exploratory analysis of within-month user activity.

**What this approach does not preserve:**

- It does not guarantee complete user histories across both months.
- It cannot support a reliable cross-month retention estimate.
- It may understate full-period RFM frequency, recency and monetary values.
- It does not make the current stage-participation analysis a sequential funnel.
- Similar event-type proportions do not prove that every user, product, category or purchase-value distribution is unbiased.

**How I would redesign it:**

- For retention and full-period RFM, select users once from the combined cross-month population and retrieve all their events across both months.
- For a strict funnel, create a session-level dataset and enforce same-user, same-product and timestamp-ordered `view → cart → purchase` sequences.
- For a more memory-efficient workflow, use a two-pass chunked process: first identify sampled user IDs, then scan the files again and retain only matching rows.
- Compare repeated samples or full-data aggregates where possible to test whether the main findings are stable.

**Key learning:**

The appropriate sampling method depends on the analytical question.
One sampling design does not automatically support every type of analysis.

</details>

---

## Local Setup

<details>
<summary>Click to expand setup instructions</summary>

1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\\Scripts\\activate` (Windows) or `source venv/bin/activate` (Mac)
4. Install: `pip install -r requirements.txt`
5. Create `.env` file with MySQL credentials
6. Run notebooks Phase 1-4 in order to load data
7. Run: `streamlit run streamlit_app/app.py`

</details>

---

## About

Built by **YIP CHEN LENG**

Targeting: BI Analyst / Data Analyst / E-Commerce Analyst roles

Email: clyip08@gmail.com

LinkedIn: [linkedin.com/in/yipcl](https://www.linkedin.com/in/yipcl)

---

*Dataset: Kaggle - eCommerce behavior data from multi-category store*
'''
