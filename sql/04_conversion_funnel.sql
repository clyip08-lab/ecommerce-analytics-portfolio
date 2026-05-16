-- Overall conversion funnel
USE ecommerce_analytics;
SELECT
    event_type,
    COUNT(*)                                        AS events,
    COUNT(DISTINCT user_id)                         AS unique_users,
    ROUND(COUNT(*) * 100.0 /
          SUM(COUNT(*)) OVER (), 2)                 AS pct_of_total
FROM fact_events
GROUP BY event_type
ORDER BY FIELD(event_type, 'view','cart','purchase');