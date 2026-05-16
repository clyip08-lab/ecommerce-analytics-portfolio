-- Top 10 brands by revenue
USE ecommerce_analytics;
SELECT
    p.brand,
    COUNT(*)                    AS purchases,
    ROUND(SUM(f.revenue), 2)    AS revenue,
    ROUND(AVG(f.price), 2)      AS avg_price
FROM fact_events f
JOIN dim_products p ON f.product_id = p.product_id
WHERE f.event_type = 'purchase'
  AND p.brand != 'unknown'
GROUP BY p.brand
ORDER BY revenue DESC
LIMIT 10;