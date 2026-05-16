USE ecommerce_analytics;

CREATE OR REPLACE VIEW vw_daily_kpis AS
SELECT
    d.full_date,
    d.day_of_week,
    d.is_weekend,
    d.year_month,
    COUNT(*)                                        AS total_events,
    COUNT(DISTINCT f.user_id)                       AS unique_users,
    COUNT(DISTINCT f.session_id)                    AS unique_sessions,
    SUM(CASE WHEN f.event_type='view'
             THEN 1 ELSE 0 END)                     AS views,
    SUM(CASE WHEN f.event_type='cart'
             THEN 1 ELSE 0 END)                     AS carts,
    SUM(CASE WHEN f.event_type='purchase'
             THEN 1 ELSE 0 END)                     AS purchases,
    ROUND(SUM(f.revenue), 2)                        AS daily_revenue,
    ROUND(AVG(CASE WHEN f.event_type='purchase'
             THEN f.price END), 2)                  AS daily_aov
FROM fact_events f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY
    d.full_date, d.day_of_week,
    d.is_weekend, d.year_month
ORDER BY d.full_date