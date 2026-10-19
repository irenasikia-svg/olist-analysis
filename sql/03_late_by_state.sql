-- Q2b 哪些州晚到最严重（订单数 >= 500 的州）
-- Q2b Late-delivery rate by customer state (states with >= 500 orders)
-- 晚到口径与 02 相同：按日期比较，预计当天送达算准时（预计日期存为 00:00:00，直接比时间戳会把当天送达算成晚到）
-- Same "late" definition as 02: compare dates, so delivery on the estimated day is on time
-- (the estimate is stored at 00:00:00, so a timestamp comparison would count same-day delivery as late)
SELECT
    customer_state,
    COUNT(*) AS orders,
    ROUND(100.0 * AVG(CASE WHEN date_diff('day', order_estimated_delivery_date::DATE,
                                                 order_delivered_customer_date::DATE) > 0
                           THEN 1 ELSE 0 END), 1) AS late_rate_pct,
    ROUND(AVG(date_diff('day', order_purchase_timestamp, order_delivered_customer_date)), 1)
        AS avg_delivery_days
FROM delivered_orders
GROUP BY 1
HAVING COUNT(*) >= 500
ORDER BY late_rate_pct DESC;
