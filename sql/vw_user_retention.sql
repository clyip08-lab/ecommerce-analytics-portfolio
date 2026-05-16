USE ecommerce_analytics;

CREATE OR REPLACE VIEW vw_user_retention AS
SELECT
    u.user_id,
    u.user_has_purchased,
    u.total_events,
    u.total_purchases,
    u.total_sessions,
    u.total_revenue,
    u.active_months,
    u.avg_order_value,
    DATEDIFF(u.last_seen, u.first_seen)             AS days_active,
    CASE
        WHEN u.active_months >= 2 THEN 'retained'
        WHEN u.active_months  = 1
         AND u.total_purchases > 0 THEN 'one_time_buyer'
        WHEN u.active_months  = 1
         AND u.total_purchases = 0 THEN 'one_time_visitor'
        ELSE 'unknown'
    END                                             AS retention_segment
FROM dim_users u