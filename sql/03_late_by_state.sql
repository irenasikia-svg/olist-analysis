-- Q2b 哪些州晚到最严重（订单数 >= 500 的州）
-- Q2b Late-delivery rate by customer state (states with >= 500 orders)
SELECT
    customer_state,
    COUNT(*) AS orders,
    ROUND(100.0 * AVG(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date
                           THEN 1 ELSE 0 END), 1) AS late_rate_pct,
    ROUND(AVG(date_diff('day', order_purchase_timestamp, order_delivered_customer_date)), 1)
        AS avg_delivery_days
FROM delivered_orders
GROUP BY 1
HAVING COUNT(*) >= 500
ORDER BY late_rate_pct DESC;
