from fastapi import FastAPI
import pandas as pd
import numpy as np

import sklearn
from sklearn.metrics import DistanceMetric

from datetime import datetime
from dateutil.relativedelta import relativedelta
from sentence_transformers import SentenceTransformer

from .utils import getRecommendedProducts, getUpcomingShoppers, PredictorRawMonetary, PredictorGGF

import os
from google.cloud import bigquery



# Connect to BigQuery
print(f"Connecting to BigQuery...")
start_time = datetime.now()
gcr_project_id = os.getenv('GCR_CLV_PROJECT_ID')
client = bigquery.Client()
end_time = datetime.now()
print(f"Successfully connected to BigQuery - Time Taken = {end_time - start_time}s")


####### Product Recommendation Model Creation ######
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


######## High Value Shopper Prediction Model Creation #########
# Get order values data
print(f"Collecting order values data from BigQuery...")
start_time = datetime.now()
ORDER_VALUES_QUERY  = f"""
WITH order_values AS (
    SELECT 
      order_id,
      SUM(sale_price) as order_value
    FROM `ecommerce-data-project-444616.thelook_ecommerce.order_items`
    GROUP BY order_id
    ORDER BY order_id
)
SELECT 
  orders.order_id,
  orders.user_id,
  users.first_name,
  users.last_name,
  users.email,
  orders.created_at,
  orders.status,
  order_values.order_value
FROM `ecommerce-data-project-444616.thelook_ecommerce.orders` AS orders
    LEFT JOIN `ecommerce-data-project-444616.thelook_ecommerce.users` AS users ON orders.user_id = users.id
    LEFT JOIN order_values on orders.order_id = order_values.order_id
ORDER BY orders.order_id;
"""
df_order_values = client.query_and_wait(ORDER_VALUES_QUERY).to_dataframe()
end_time = datetime.now()
print(f"Successfully collected order values data from BigQuery - Time Taken = {end_time - start_time}s")

# Get users data
print(f"Collecting users data from BigQuery...")
start_time = datetime.now()
USERS_QUERY  = f"""
SELECT
  *
FROM `ecommerce-data-project-444616.thelook_ecommerce.users`;
"""
df_users = client.query_and_wait(USERS_QUERY).to_dataframe()
end_time = datetime.now()
print(f"Successfully collected users data from BigQuery - Time Taken = {end_time - start_time}s")


####### API Creation #######
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
    return {'name' : 'The Look eCommerce API', 'Description' : "API to recommend products for shoppers and identify upcoming high value shoppers"}
end_time = datetime.now()
print(f"'info' function was successfully initiated - Time Taken = {time_end-time_start}s")

print(f"Initiating 'recommend products' function")
start_time = datetime.now()
@app.get('/recommend_products')
def recommendProducts(customer_id : int):
    df_rec = getRecommendedProducts(customer_id, model, metric, df_orders, df_products)
    response = df_rec.to_dict(orient='list')
    return response
end_time = datetime.now()
print(f"'Recommend Products' function was successfully initiated - Time Taken = {time_end-time_start}s")


print(f"Initiating 'upcoming shoppers' function")
start_time = datetime.now()
@app.get('/upcoming_shoppers')
def upcomingShoppers():
    df_shoppers = getUpcomingShoppers(df_order_values, df_users, model_class=PredictorGGF)
    response = df_shoppers.to_dict(orient='list')
    return response
end_time = datetime.now()
print(f"'Recommend Products' function was successfully initiated - Time Taken = {time_end-time_start}s")
