-- =====================================================
-- MONTHLY REVENUE
-- =====================================================

CREATE OR REPLACE TABLE monthly_revenue AS

SELECT

    DATE_TRUNC('month', event_time) AS month,

    COUNT(*) AS total_purchases,

    SUM(price) AS revenue,

    AVG(price) AS avg_order_value

FROM clean_events

WHERE event_type = 'purchase'

GROUP BY 1

ORDER BY 1;

-- =====================================================
-- FUNNEL METRICS
-- =====================================================

CREATE OR REPLACE TABLE funnel_metrics AS

SELECT

    COUNT(
        CASE
            WHEN event_type = 'view'
            THEN 1
        END
    ) AS total_views,

    COUNT(
        CASE
            WHEN event_type = 'cart'
            THEN 1
        END
    ) AS total_carts,

    COUNT(
        CASE
            WHEN event_type = 'purchase'
            THEN 1
        END
    ) AS total_purchases

FROM clean_events;

-- =====================================================
-- USER PURCHASE SUMMARY
-- =====================================================

CREATE OR REPLACE TABLE user_purchase_summary AS

SELECT

    user_id,

    MIN(event_time) AS first_purchase_date,

    MAX(event_time) AS last_purchase_date,

    COUNT(*) AS total_orders,

    SUM(price) AS total_spent

FROM clean_events

WHERE event_type = 'purchase'

GROUP BY user_id;

-- =====================================================
-- RFM TABLE
-- =====================================================

CREATE OR REPLACE TABLE rfm_table AS

WITH snapshot AS (

    SELECT
        MAX(event_time) AS snapshot_date
    FROM clean_events

),

rfm_base AS (

    SELECT

        u.user_id,

        DATE_DIFF(
            'day',
            u.last_purchase_date,
            s.snapshot_date
        ) AS recency,

        u.total_orders AS frequency,

        u.total_spent AS monetary

    FROM user_purchase_summary u
    CROSS JOIN snapshot s

)

SELECT *

FROM rfm_base;

-- =====================================================
-- COHORT TABLE
-- =====================================================

CREATE OR REPLACE TABLE cohort_table AS

WITH first_purchase AS (

    SELECT

        user_id,

        DATE_TRUNC(
            'month',
            MIN(event_time)
        ) AS cohort_month

    FROM clean_events

    WHERE event_type = 'purchase'

    GROUP BY user_id

),

activity AS (

    SELECT

        ce.user_id,

        DATE_TRUNC(
            'month',
            ce.event_time
        ) AS activity_month

    FROM clean_events ce

    WHERE ce.event_type = 'purchase'

),

cohort_data AS (

    SELECT

        fp.cohort_month,

        a.activity_month,

        DATE_DIFF(
            'month',
            fp.cohort_month,
            a.activity_month
        ) AS month_number,

        a.user_id

    FROM first_purchase fp

    JOIN activity a
        ON fp.user_id = a.user_id

)

SELECT

    cohort_month,

    month_number,

    COUNT(DISTINCT user_id) AS active_users

FROM cohort_data

GROUP BY

    cohort_month,
    month_number

ORDER BY

    cohort_month,
    month_number;