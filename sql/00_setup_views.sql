-- 把原始 CSV 注册成视图，后面的查询直接用表名
-- Register raw CSVs as views so later queries can use table names
CREATE OR REPLACE VIEW orders      AS SELECT * FROM read_csv_auto('data/raw/olist_orders_dataset.csv');
CREATE OR REPLACE VIEW customers   AS SELECT * FROM read_csv_auto('data/raw/olist_customers_dataset.csv');
CREATE OR REPLACE VIEW order_items AS SELECT * FROM read_csv_auto('data/raw/olist_order_items_dataset.csv');
CREATE OR REPLACE VIEW reviews     AS SELECT * FROM read_csv_auto('data/raw/olist_order_reviews_dataset.csv');
CREATE OR REPLACE VIEW products    AS SELECT * FROM read_csv_auto('data/raw/olist_products_dataset.csv');
CREATE OR REPLACE VIEW category_en AS SELECT * FROM read_csv_auto('data/raw/product_category_name_translation.csv');

-- 分析口径：2017-01 至 2018-08 的已送达订单（首尾月份数据不完整）
-- Scope: delivered orders purchased 2017-01 .. 2018-08 (edge months are incomplete)
CREATE OR REPLACE VIEW delivered_orders AS
SELECT o.*, c.customer_unique_id, c.customer_state
FROM orders o
JOIN customers c USING (customer_id)
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp <  '2018-09-01';
