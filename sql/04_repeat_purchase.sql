-- Q3 复购：每个真实客户（customer_unique_id）下了几单
-- Q3 Retention: orders per real customer (customer_unique_id, not customer_id)
WITH per_customer AS (
    SELECT customer_unique_id, COUNT(*) AS n_orders
    FROM delivered_orders
    GROUP BY 1
)
SELECT
    COUNT(*)                                                      AS customers,
    SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END)                AS repeat_customers,
    ROUND(100.0 * AVG(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END), 2) AS repeat_rate_pct
FROM per_customer;
