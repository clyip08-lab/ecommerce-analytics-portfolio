-- Hourly traffic + purchase pattern
USE ecommerce_analytics;
SELECT
    d.hour,
    COUNT(*)                                    AS total_events,
    SUM(CASE WHEN f.event_type='purchase'
             THEN 1 ELSE 0 END)                 AS purchases,
    ROUND(SUM(f.revenue), 2)                    AS revenue
FROM fact_events f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.hour
ORDER BY d.hour;