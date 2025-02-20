# Import packages to connect to Google Storage
import os
from google.cloud import storage
storage_client = storage.Client()

# Import packages to connect to Google Sheets API
import gspread
from google.oauth2.service_account import Credentials
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("backend/credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# Import packages to create product recommendations
from datetime import datetime
import pandas as pd
import io
import requests

# Get list of upcoming shoppers
print(f"Connecting to storage bucket...")
bucket = storage_client.get_bucket("bucket-quickstart_ecommerce-data-project-444616")
content = bucket.blob("upcoming_shoppers.csv").download_as_bytes() # Download the upcoming shoppers file
df_upcoming_shoppers = pd.read_csv(io.BytesIO(content)) # Convert to Pandas DataFrame

# Create dataframe with product recommendations for upcoming shoppers
print(f"Creating Recommendations Dataframe")
recs_data = {'First Name' : [],
             'Last Name' : [],
             'Email' : [],
             'Rec Prod1' : [], 'Rec Prod2' : [], 'Rec Prod3' : [], 'Rec Prod4' : [], 'Rec Prod5' : []}

for row, row_vals in df_upcoming_shoppers.iterrows():
    recs_data['First Name'].append(row_vals['name'].split(' ')[0])
    recs_data['Last Name'].append(row_vals['name'].split(' ')[1])
    recs_data['Email'].append(row_vals['email'])

    shopper_id = row_vals['shopper_id']
    recs = requests.get(f"http://0.0.0.0:8000/recommend-products?customer_id={shopper_id}").json()['products']
    for rec_num in range(5):
        recs_data[f"Rec Prod{rec_num+1}"].append(recs[rec_num]['name'])

recs_df = pd.DataFrame(recs_data)
recs_df['Email Sent'] = '' # Add empty 'email sent' column


# Create new worksheet with upcoming shoppers & recommended products
print(f"Uploading recommendations dataframe to worksheet")
spreadsheet = client.open_by_key("1LIcZbfx_Gh_spRUAAst2doEb7bW0ZJuwR0VpRQWcUvU")
worksheet = spreadsheet.add_worksheet(title=f"recommendations-{datetime.strftime(datetime.now().date(), '%Y-%m-%d')}", 
                                      rows=recs_df.shape[0], cols=recs_df.shape[1])
worksheet.update([recs_df.columns.values.tolist()] + recs_df.values.tolist())