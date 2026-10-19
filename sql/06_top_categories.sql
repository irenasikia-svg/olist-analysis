-- 补充：GMV 前 10 品类及其评分
-- Extra: top 10 categories by GMV and their review score
WITH item_cat AS (
    SELECT oi.order_id, oi.price + oi.freight_value AS item_gmv,
           COALESCE(ce.product_category_name_english, p.product_category_name, 'unknown') AS category
    FROM order_items oi
    JOIN products p USING (product_id)
    LEFT JOIN category_en ce USING (product_category_name)
)
SELECT
    ic.category,
    COUNT(DISTINCT ic.order_id)   AS orders,
    ROUND(SUM(ic.item_gmv), 0)    AS gmv_brl,
    ROUND(AVG(r.review_score), 2) AS avg_review
FROM item_cat ic
JOIN delivered_orders d USING (order_id)
LEFT JOIN (SELECT order_id, AVG(review_score) AS review_score FROM reviews GROUP BY order_id) r USING (order_id)
GROUP BY 1
ORDER BY gmv_brl DESC
LIMIT 10;
