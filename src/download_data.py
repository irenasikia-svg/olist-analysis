"""
Download the Olist public dataset (Kaggle: olistbr/brazilian-ecommerce) into data/raw/.
下载 Olist 公开数据集到 data/raw/。

Source of truth is Kaggle; this script pulls an unmodified GitHub mirror so no Kaggle login is needed.
原始来源是 Kaggle；这里用未修改的 GitHub 镜像，免登录。
"""
from pathlib import Path
from urllib.request import urlretrieve

MIRROR = "https://raw.githubusercontent.com/nabeel-io/olist_database_analysis/HEAD/olist_data"
FILES = [
    "olist_customers_dataset.csv", "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv", "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv", "olist_products_dataset.csv",
    "olist_sellers_dataset.csv", "product_category_name_translation.csv",
]

raw = Path(__file__).resolve().parents[1] / "data" / "raw"
raw.mkdir(parents=True, exist_ok=True)
for name in FILES:
    target = raw / name
    if target.exists():
        print(f"skip  {name}")
        continue
    print(f"fetch {name}")
    urlretrieve(f"{MIRROR}/{name}", target)
print("done")
