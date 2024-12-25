from fastapi import FastAPI
import pandas as pd
import numpy as np

import sklearn
from sklearn.metrics import DistanceMetric

from datetime import datetime
from dateutil.relativedelta import relativedelta
from sentence_transformers import SentenceTransformer

from .utils import getRecommendedProducts

import os
from google.cloud import bigquery



# Connect to BigQuery
print(f"Connecting to BigQuery...")
start_time = datetime.now()
gcr_project_id = os.getenv('GCR_CLV_PROJECT_ID')
client = bigquery.Client()
end_time = datetime.now()
print(f"Successfully connected to BigQuery - Time Taken = {end_time - start_time}s")

# Get orders dataframe
print(f"Collecting orders data from BigQuery...")
start_time = datetime.now()
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
end_time = datetime.now()
print(f"Successfully collected orders data from BigQuery - Time Taken = {end_time - start_time}s")

# Get products dataframe
print(f"Collecting products data from BigQuery...")
start_time = datetime.now()
PRODUCTS_QUERY  = f"""
SELECT *
FROM `ecommerce-data-project-444616.thelook_ecommerce.products`;
"""
df_products = client.query_and_wait(PRODUCTS_QUERY).to_dataframe()
end_time = datetime.now()
print(f"Successfully collected products data from BigQuery - Time Taken = {end_time - start_time}s")


# Define model & similarity metric
print(f"Loading LLM...")
time_start = datetime.now()
model = SentenceTransformer("all-mpnet-base-v2")
time_end = datetime.now()
print(f"Model loading time : {time_end - time_start}s")

metric = DistanceMetric.get_metric('euclidean')

# Create fastAPI object
app = FastAPI()

print(f"Initiating 'health check' function")
start_time = datetime.now()
@app.get('/')
def health_check():
    return {'health_check' : 'OK'}
end_time = datetime.now()
print(f"'health check' function was successfully initiated - Time Taken = {time_end-time_start}s")

print(f"Initiating 'info' function")
start_time = datetime.now()
@app.get('/info')
def info():
    return {'name' : 'Product Recommendation', 'Description' : "Search API to identify similar products to a customers previous purchases"}
end_time = datetime.now()
print(f"'info' function was successfully initiated - Time Taken = {time_end-time_start}s")

print(f"Initiating 'recommend products' function")
start_time = datetime.now()
@app.get('/recommend_products')
def recommendProducts(customer_id : int):
    df_rec= getRecommendedProducts(customer_id, model, metric, df_orders, df_products)
    response = df_rec[['id','name','sku']].to_dict(orient='list')
    return response
end_time = datetime.now()
print(f"'Recommend Products' function was successfully initiated - Time Taken = {time_end-time_start}s")
