USE ecommerce_analytics;

CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    f.product_id,
    p.brand,
    p.category_l1,
    p.category_l2,
    p.avg_price,
    COUNT(*)                                        AS total_events,
    SUM(CASE WHEN f.event_type='view'
             THEN 1 ELSE 0 END)                     AS views,
    SUM(CASE WHEN f.event_type='cart'
             THEN 1 ELSE 0 END)                     AS carts,
    SUM(CASE WHEN f.event_type='purchase'
             THEN 1 ELSE 0 END)                     AS purchases,
    ROUND(SUM(f.revenue), 2)                        AS total_revenue,
    ROUND(SUM(CASE WHEN f.event_type='purchase'
             THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(SUM(CASE WHEN f.event_type='view'
             THEN 1 ELSE 0 END), 0), 2)             AS view_to_purchase_rate
FROM fact_events f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY
    f.product_id, p.brand,
    p.category_l1, p.category_l2, p.avg_price