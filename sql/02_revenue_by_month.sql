-- Monthly revenue trend
USE ecommerce_analytics;
SELECT
    month,
    COUNT(*)                    AS total_purchases,
    ROUND(SUM(revenue), 2)      AS total_revenue,
    ROUND(AVG(price), 2)        AS avg_order_value
FROM fact_events
WHERE event_type = 'purchase'
GROUP BY month
ORDER BY month;