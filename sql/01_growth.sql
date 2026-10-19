-- Q1 增长：每月 GMV、订单数、客单价
-- Q1 Growth: monthly GMV, orders, average order value (GMV = item price + freight)
WITH order_value AS (
    SELECT order_id, SUM(price + freight_value) AS order_gmv
    FROM order_items
    GROUP BY order_id
)
SELECT
    date_trunc('month', d.order_purchase_timestamp)::DATE AS month,
    COUNT(*)                                             AS orders,
    ROUND(SUM(v.order_gmv), 0)                           AS gmv_brl,
    ROUND(AVG(v.order_gmv), 2)                           AS aov_brl
FROM delivered_orders d
JOIN order_value v USING (order_id)
GROUP BY 1
ORDER BY 1;
