-- Q3b 首单体验是否影响复购：按首单评分分组看复购率
-- Q3b Does the first-order experience drive repeat purchase?
WITH ranked AS (
    SELECT d.customer_unique_id, d.order_id, d.order_purchase_timestamp,
           ROW_NUMBER() OVER (PARTITION BY d.customer_unique_id
                              ORDER BY d.order_purchase_timestamp, d.order_id) AS rn,
           COUNT(*)     OVER (PARTITION BY d.customer_unique_id)   AS n_orders
    FROM delivered_orders d
),
first_orders AS (
    SELECT r.customer_unique_id, r.n_orders, rv.review_score
    FROM ranked r
    JOIN (SELECT order_id, ROUND(AVG(review_score)) AS review_score
          FROM reviews GROUP BY order_id) rv USING (order_id)
    WHERE r.rn = 1
)
SELECT
    review_score::INT AS first_order_review,
    COUNT(*)          AS customers,
    ROUND(100.0 * AVG(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END), 2) AS repeat_rate_pct
FROM first_orders
GROUP BY 1
ORDER BY 1;
