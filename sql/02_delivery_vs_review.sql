-- Q2 配送体验：比预计日期晚到多少天，对评分的影响
-- Q2 Delivery: days late vs estimated date, and its effect on review score
WITH per_order AS (
    SELECT
        d.order_id,
        date_diff('day', d.order_estimated_delivery_date::DATE,
                         d.order_delivered_customer_date::DATE) AS days_late,
        r.review_score
    FROM delivered_orders d
    JOIN (SELECT order_id, AVG(review_score) AS review_score   -- 少数订单有多条评价，取平均
          FROM reviews GROUP BY order_id) r USING (order_id)
)
SELECT
    CASE
        WHEN days_late <= 0  THEN '1 准时或提前 On time/early'
        WHEN days_late <= 3  THEN '2 晚 1-3 天 1-3 days late'
        WHEN days_late <= 7  THEN '3 晚 4-7 天 4-7 days late'
        WHEN days_late <= 14 THEN '4 晚 8-14 天 8-14 days late'
        ELSE                      '5 晚 15 天以上 15+ days late'
    END                                              AS delay_bucket,
    COUNT(*)                                         AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_orders,
    ROUND(AVG(review_score), 2)                      AS avg_review,
    ROUND(100.0 * AVG(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END), 1) AS pct_1_2_star
FROM per_order
GROUP BY 1
ORDER BY 1;
