import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

import pandas as pd

from sentence_transformers import SentenceTransformer
import sklearn
from sklearn.metrics import DistanceMetric

from google.cloud import storage, bigquery
import io

print(f"Loading LLM for product recommendations ...")
model = SentenceTransformer("all-mpnet-base-v2")
print(f"Loading metric for product recommendations ...")
metric = DistanceMetric.get_metric('euclidean')

# Get product embeddings dataframe
print(f"Downloading product embeddings dataframe ...")
client = storage.Client() # Connect to Google Cloud Storage
blob = client.bucket("bucket-quickstart_ecommerce-data-project-444616").blob("product_embeddings_all-mpnet-base-v2.csv") # Connect to google cloud bucket
content = blob.download_as_bytes() # Download the embeddings file
df_embedding = pd.read_csv(io.BytesIO(content)) # Convert to Pandas DataFrame

# Get products dataframe
print(f"Querying BigQuery for products dataframe")
client = bigquery.Client()
PRODUCTS_QUERY  = f"""
SELECT *
FROM `ecommerce-data-project-444616.the_look_ecommerce_constant.products`;
"""
df_products = client.query_and_wait(PRODUCTS_QUERY).to_dataframe()

# Get orders dataframe
print(f"Querying BigQuery for orders dataframe")
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
FROM `ecommerce-data-project-444616.the_look_ecommerce_constant.order_items` as order_items
LEFT JOIN `ecommerce-data-project-444616.the_look_ecommerce_constant.users` as users
ON order_items.user_id = users.id
LEFT JOIN `ecommerce-data-project-444616.the_look_ecommerce_constant.products` as products
ON order_items.product_id = products.id
ORDER BY order_items.user_id;
"""
df_orders = client.query_and_wait(ORDERS_QUERY).to_dataframe()



app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/recommend-products")
def recommendProducts(customer_id : int):

    # Get list of customer's purchased products
    customer_purchases = df_orders[(df_orders.user_id == customer_id) & (df_orders.status != 'Cancelled')]
    purchased_products = customer_purchases.product_name.tolist()

    # Create dictionary containing customer's previously purchased products and the ids of the corresponding recommended products. 
    rec_dict = {}
    for query in purchased_products:
        query_embedding = model.encode(query).reshape(1,-1)   # Create embedding for purchased product's name
        query_dist = metric.pairwise(df_embedding.values[:,10:], query_embedding).flatten()   # Calculate distance between purchased product embedding & embeddings of all available products
        query_dist_df = pd.DataFrame({'product_id' : df_products.id,    # Store distance results in a dataframe
                                      'dist' : query_dist})
        rec_dict[query] = query_dist_df.sort_values(by='dist').product_id.head(5).tolist()    # Add purchased product's top 5 most similar products to dictionary

    # Create recommended products dataframe
    df_recs = pd.DataFrame(columns=df_products.columns)
    for product in rec_dict.keys():
        product_recs = df_products[df_products.id.isin(rec_dict[product])]
        df_recs = pd.concat([df_recs, product_recs], axis=0)
    
    response = df_recs.to_dict(orient='list')
    return response


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)