# 🛒 E-Commerce Analytics Portfolio Project
> **End-to-end analytics system built on 42M+ row e-commerce event data**

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

This project simulates a **real-world e-commerce analytics workflow** — from raw data ingestion
to executive dashboards and customer segmentation — using an industry-standard tech stack.

**Dataset:** 42M+ user events (views, cart adds, purchases) from Oct-Nov 2019
**Source:** [eCommerce behavior data from multi-category store](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store)

---

## Architecture
```
Raw CSV (42M rows)
│
▼
Python Sampling          ← Stratified user-based sampling (Phase 1)
│
▼
Data Cleaning            ← Deduplication, nulls, feature engineering (Phase 2)
│
▼
Star Schema Design       ← fact_events + 4 dimension tables (Phase 3)
│
▼
MySQL Database           ← ETL pipeline via SQLAlchemy (Phase 4)
│
▼
KPI Semantic Layer       ← 6 SQL views = single source of truth (Phase 5)
│
├──→ Core Analysis        (trends, cohort, product) (Phase 6)
├──→ Advanced Analytics   (RFM, Pareto, funnel)     (Phase 7)
├──→ Power BI Dashboard   (4-page interactive BI)   (Phase 8)
└──→ Streamlit App        (live web dashboard)      (Phase 9)
```
## 📊 Key Business Findings

| Finding | Actual Number | Insight | Recommendation |
|---|---|---|---|
| **Overall conversion rate** | **11.72%** | 1 in 9 users purchases — healthy for e-commerce | A/B test product pages to push above 15% |
| **View → Cart rate** | **16.73%** | Strong browse-to-intent signal | Improve product imagery + descriptions |
| **Cart → Purchase rate** | **78.79%** | Very high — users who cart mostly buy | Protect checkout UX, minimize friction |
| **Top category** | **Electronics (75.2% of revenue)** | $5.58M of $7.42M total | Heavy concentration risk — diversify categories |
| **Avg Order Value** | **$301.48** | High-ticket purchases dominate | Bundle lower-ticket items to protect AOV |
| **Revenue per User** | **$74.42** | Low vs AOV — most users never buy | Retargeting campaigns for the 88% non-buyers |
| **Retained users** | **307 of 99,658 (0.31%)** | Near-zero cross-month retention | Urgent: launch post-purchase email flow |
| **One-time buyers** | **11,617 users (11.7%)** | Bought once, never returned | Win-back campaign: offer 2nd purchase discount |
| **One-time visitors** | **87,734 users (88%)** | Massive unconverted audience | Retargeting + wishlist feature |
| **Buying Users** | **11,698 of 99,658 (11.7%)** | Small buyer base drives all revenue | Protect + reward existing buyers first |

---

## 🗂️ Project Structure

```
ecommerce-analytics-portfolio/
│
├── data/
│   ├── raw/                          ← Original CSVs (not in Git)
│   ├── processed/                    ← Cleaned dataset
│   ├── samples/                      ← Stratified user sample
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

| Page | Description |
|---|---|
| Executive Overview | Revenue KPIs, orders trend, hourly patterns |
| Product and Brand | Top brands, category treemap, Pareto 80/20 |
| Customer Segments | RFM scoring, segment bars, funnel drop-off |
| Retention and Cohort | Cohort heatmap, retention segments, session depth |

---

## Analytical Methods

- **Stratified User-Based Sampling** - preserves behavioral chains for valid funnel and cohort analysis
- **Star Schema Modeling** - fact and dimension tables for efficient BI querying
- **KPI Semantic Layer** - 6 SQL views as single source of truth across all tools
- **RFM Segmentation** - quintile scoring producing 8 actionable customer segments
- **Cohort Analysis** - monthly retention tracking to measure loyalty
- **Pareto 80/20 Analysis** - product and brand revenue concentration
- **Funnel Analysis** - view to cart to purchase drop-off by category

---

## Sampling Methodology

<details>
<summary>Why user-based sampling? (click to expand)</summary>

**Problem:** Event-type sampling breaks user behavioral chains.
A user\'s view, cart, and purchase scatter across different samples,
making funnel and retention metrics invalid.

**Solution:** User-based sampling - select 50,000 users randomly,
preserve ALL their events intact.

**Result:** Valid cohort analysis, accurate RFM scoring,
trustworthy conversion funnel.

**Lesson:** Design your sample around your analytical objective,
not computational convenience.

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

LinkedIn: https://www.linkedin.com/in/yipcl

---

*Dataset: Kaggle - eCommerce behavior data from multi-category store*
'''
