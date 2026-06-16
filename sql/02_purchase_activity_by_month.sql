-- Monthly observed purchase activity

USE ecommerce_analytics;

SELECT
    month,
    COUNT(*) AS purchase_events,
    ROUND(SUM(revenue), 2) AS observed_purchase_value,
    ROUND(AVG(price), 2) AS avg_purchase_event_value
FROM fact_events
WHERE event_type = 'purchase'
GROUP BY month
ORDER BY month;
