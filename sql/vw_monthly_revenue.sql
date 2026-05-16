USE ecommerce_analytics;

CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
    month,
    COUNT(*)                                AS total_events,
    SUM(CASE WHEN event_type = 'purchase'
             THEN 1 ELSE 0 END)             AS total_orders,
    COUNT(DISTINCT user_id)                 AS unique_users,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase'
             THEN user_id END)              AS buying_users,
    ROUND(SUM(revenue), 2)                  AS total_revenue,
    ROUND(AVG(CASE WHEN event_type = 'purchase'
             THEN price END), 2)            AS avg_order_value,
    ROUND(SUM(revenue) /
          NULLIF(COUNT(DISTINCT user_id),0)
          , 2)                              AS revenue_per_user
FROM fact_events
GROUP BY month
ORDER BY month