# Import modules to acces GCP
import os
from google.cloud import storage, bigquery
storage_client = storage.Client()
bigquery_client = bigquery.Client()

# Import automation modules
from datetime import datetime

# Import packages to create product embeddings
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics import DistanceMetric
import io


#### Create new product embeddings dataframe
model = SentenceTransformer("all-mpnet-base-v2")
metric = DistanceMetric.get_metric('euclidean')
QUERY  = f"""
SELECT *
FROM `ecommerce-data-project-444616.the_look_ecommerce_constant.products`;
"""
df_products = bigquery_client.query_and_wait(QUERY).to_dataframe()

print(f"Creating Product Embeddings...")
start_time = datetime.now()
embedding_arr = model.encode(df_products['name'].to_list())
df_embedding = pd.DataFrame(embedding_arr)
df_embedding.columns = ['product-embedding-'+str(i) for i in range(embedding_arr.shape[1])]
df_embedding = pd.concat([df_products, df_embedding], axis=1)
print(f"Finished creating product embeddings - Time Taken = {datetime.now() - start_time}")

print(f"Saving Product Embeddings to CSV Buffer...")
start_time = datetime.now()
csv_buffer = io.BytesIO()
df_embedding.to_csv(csv_buffer, index=False)  # Convert DataFrame to CSV
csv_buffer.seek(0)
print(f"Finished saving product embeddings - Time Taken = {datetime.now() - start_time}")


#### Upload new embeddings dataframe to bucket
print(f"Connecting to storage bucket...")
bucket = storage_client.get_bucket("bucket-quickstart_ecommerce-data-project-444616")
blob = bucket.blob("product_embeddings_all-mpnet-base-v2.csv")
print(f"Uploading product embeddings to storage bucket...")
start_time = datetime.now()
blob.upload_from_file(csv_buffer, content_type="text/csv", timeout=600)
print(f"Finished uploading product embeddings - Time Taken = {datetime.now() - start_time}")