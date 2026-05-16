USE ecommerce_analytics;

CREATE OR REPLACE VIEW vw_conversion_funnel AS
WITH event_counts AS (
    SELECT
        month,
        COUNT(DISTINCT CASE WHEN event_type = 'view'
              THEN user_id END)             AS viewers,
        COUNT(DISTINCT CASE WHEN event_type = 'cart'
              THEN user_id END)             AS carters,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase'
              THEN user_id END)             AS buyers,
        COUNT(DISTINCT CASE WHEN event_type = 'view'
              THEN CONCAT(user_id,session_id) END) AS view_sessions,
        COUNT(DISTINCT CASE WHEN event_type = 'cart'
              THEN CONCAT(user_id,session_id) END) AS cart_sessions,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase'
              THEN CONCAT(user_id,session_id) END) AS purchase_sessions
    FROM fact_events
    GROUP BY month
)
SELECT
    month,
    viewers,
    carters,
    buyers,
    ROUND(carters   * 100.0 / NULLIF(viewers,0), 2) AS view_to_cart_rate,
    ROUND(buyers    * 100.0 / NULLIF(carters,0), 2) AS cart_to_purchase_rate,
    ROUND(buyers    * 100.0 / NULLIF(viewers,0), 2) AS overall_conversion_rate,
    view_sessions,
    cart_sessions,
    purchase_sessions
FROM event_counts
ORDER BY month