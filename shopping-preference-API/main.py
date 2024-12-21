from fastapi import FastAPI
import pandas as pd
import numpy as np

import sklearn
from sklearn.metrics import DistanceMetric

from datetime import datetime
from dateutil.relativedelta import relativedelta
from sentence_transformers import SentenceTransformer

from utils import getRecommendedProducts

import os
from google.cloud import bigquery


# Import google cloud project ID
gcr_project_id = os.getenv('GCR_CLV_PROJECT_ID')
client = bigquery.Client()

# Get orders dataframe
ORDERS_QUERY  = f"""
SELECT
  order_items.user_id,
  users.first_name,
  users.last_name,
  order_items.order_id,
  order_items.product_id,
  products.name as product_name,
  products.brand as product_brand,
  order_items.sale_price,
  order_items.status
FROM `ecommerce-data-project-444616.thelook_ecommerce.order_items` as order_items
LEFT JOIN `ecommerce-data-project-444616.thelook_ecommerce.users` as users
ON order_items.user_id = users.id
LEFT JOIN `ecommerce-data-project-444616.thelook_ecommerce.products` as products
ON order_items.product_id = products.id
ORDER BY order_items.user_id;
"""
df_orders = client.query_and_wait(ORDERS_QUERY).to_dataframe()

# Get products dataframe
PRODUCTS_QUERY  = f"""
SELECT *
FROM `ecommerce-data-project-444616.thelook_ecommerce.products`;
"""
df_products = client.query_and_wait(PRODUCTS_QUERY).to_dataframe()

# Define model & similarity metric
model = SentenceTransformer("all-mpnet-base-v2")
metric = DistanceMetric.get_metric('euclidean')

# Get customers recommended products
customer_id = ?????
getRecommendedProducts(customer_id, model, metric, df_orders, df_products)


# Create fastAPI object
app = FastAPI()

@app.get('/')
def health_check():
    return {'health_check' : 'OK'}

@app.get('/info')
def info():
    return {'name' : 'Product Recommendation', 'Description' : "Search API to identify similar products to a customers previous purchases"}

@app.get('/search')
def search(customer_id : int):
    rec_df = getRecommendedProducts(customer_id, model, metric, df_orders, df_products)
    return rec_df







