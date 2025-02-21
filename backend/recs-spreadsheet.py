# Import packages to connect to Google Storage
import os
from google.cloud import storage, bigquery
storage_client = storage.Client()
bigquery_client  = bigquery.Client()

# Import packages to connect to Google Sheets API
import gspread
from google.oauth2.service_account import Credentials
import json
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
secret = json.loads(os.getenv('GCP_SERVICE_ACCOUNT'))
creds = Credentials.from_service_account_info(secret, scopes=scopes)
client = gspread.authorize(creds)

# Import packages to create product recommendations
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics import DistanceMetric
import pandas as pd
import io
import requests

# Get list of upcoming shoppers
print(f"Downloading upcoming shoppers data...")
bucket = storage_client.get_bucket("bucket-quickstart_ecommerce-data-project-444616")
content = bucket.blob("upcoming_shoppers.csv").download_as_bytes() # Download the upcoming shoppers file
df_upcoming_shoppers = pd.read_csv(io.BytesIO(content)) # Convert to Pandas DataFrame

# Get product embeddings dataframe
print(f"Downloading product embeddings data...")
content = bucket.blob("product_embeddings_all-mpnet-base-v2.csv").download_as_bytes() # Download the embeddings file
df_embedding = pd.read_csv(io.BytesIO(content)) # Convert to Pandas DataFrame

# Get products dataframe
print(f"Querying BigQuery for products dataframe")
PRODUCTS_QUERY  = f"""
SELECT *
FROM `ecommerce-data-project-444616.the_look_ecommerce_constant.products`;
"""
df_products = bigquery_client.query_and_wait(PRODUCTS_QUERY).to_dataframe()

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
df_orders = bigquery_client.query_and_wait(ORDERS_QUERY).to_dataframe()

# Load embedding model
print(f"Loading LLM for product recommendations ...")
model = SentenceTransformer("all-mpnet-base-v2")
print(f"Loading metric for product recommendations ...")
metric = DistanceMetric.get_metric('euclidean')

# Define product recommendation function
def recommendProducts(customer_id : int):

    # Get list of customer's purchased products
    customer_purchases = df_orders[(df_orders.user_id == customer_id) & (df_orders.status != 'Cancelled')]
    purchased_products = customer_purchases.product_name.tolist()

    # Create dictionary containing customer's previously purchased products and the ids of the corresponding recommended products. 
    rec_dict = {}
    for query in purchased_products:
        query_embedding = model.encode(query).reshape(1,-1)   # Create embedding for purchased product's name
        query_dist = metric.pairwise(df_embedding.values[:,9:], query_embedding).flatten()   # Calculate distance between purchased product embedding & embeddings of all available products
        query_dist_df = pd.DataFrame({'product_id' : df_products.id,    # Store distance results in a dataframe
                                      'dist' : query_dist})
        rec_dict[query] = query_dist_df.sort_values(by='dist').product_id.head(5).tolist()    # Add purchased product's top 5 most similar products to dictionary

    # Create recommended products dataframe
    recs_db = {"products": []}
    for product in rec_dict.keys():
        product_recs = df_products[df_products.id.isin(rec_dict[product])]
        recs_db["products"].extend(product_recs.name.tolist())

    return recs_db

# Create dataframe with product recommendations for upcoming shoppers
print(f"Creating Recommendations Dataframe...")
start_time = datetime.now()
recs_data = {'First Name' : [],
             'Last Name' : [],
             'Recipient' : [],
             'Rec Prod1' : [], 'Rec Prod2' : [], 'Rec Prod3' : [], 'Rec Prod4' : [], 'Rec Prod5' : []}

for row, row_vals in df_upcoming_shoppers.iterrows():
    recs_data['First Name'].append(row_vals['name'].split(' ')[0])
    recs_data['Last Name'].append(row_vals['name'].split(' ')[1])
    recs_data['Recipient'].append(row_vals['email'])

    shopper_id = row_vals['shopper_id']
    recs = recommendProducts(shopper_id)['products']
    for rec_num in range(5):
        recs_data[f"Rec Prod{rec_num+1}"].append(recs[rec_num])

recs_df = pd.DataFrame(recs_data)
recs_df['Email Sent'] = '' # Add empty 'email sent' column
print(f"Finished creating recommendations dataframe - Time Taken = {datetime.now() - start_time}")


# Create new worksheet with upcoming shoppers & recommended products
print(f"Uploading recommendations dataframe to worksheet")
spreadsheet = client.open_by_key("1LIcZbfx_Gh_spRUAAst2doEb7bW0ZJuwR0VpRQWcUvU")
worksheet = spreadsheet.add_worksheet(title=f"recommendations-{datetime.strftime(datetime.now().date(), '%d-%m-%Y')}", 
                                      rows=recs_df.shape[0], cols=recs_df.shape[1])
worksheet.update([recs_df.columns.values.tolist()] + recs_df.values.tolist())