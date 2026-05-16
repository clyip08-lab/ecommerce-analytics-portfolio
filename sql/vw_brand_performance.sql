USE ecommerce_analytics;

CREATE OR REPLACE VIEW vw_brand_performance AS
SELECT
    p.brand,
    p.category_l1,
    COUNT(DISTINCT f.product_id)                    AS unique_products,
    SUM(CASE WHEN f.event_type='view'
             THEN 1 ELSE 0 END)                     AS total_views,
    SUM(CASE WHEN f.event_type='cart'
             THEN 1 ELSE 0 END)                     AS total_carts,
    SUM(CASE WHEN f.event_type='purchase'
             THEN 1 ELSE 0 END)                     AS total_purchases,
    ROUND(SUM(f.revenue), 2)                        AS total_revenue,
    ROUND(AVG(CASE WHEN f.event_type='purchase'
             THEN f.price END), 2)                  AS avg_selling_price,
    ROUND(SUM(CASE WHEN f.event_type='purchase'
             THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(SUM(CASE WHEN f.event_type='view'
             THEN 1 ELSE 0 END),0), 2)              AS conversion_rate
FROM fact_events f
JOIN dim_products p ON f.product_id = p.product_id
WHERE p.brand != 'unknown'
GROUP BY p.brand, p.category_l1
ORDER BY total_revenue DESC