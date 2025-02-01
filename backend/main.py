import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.metrics import DistanceMetric

import lifetimes

from google.cloud import storage, bigquery
import io


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


####### ----------- RECOMMENDED PRODUCTS API FUNCTION ------------ ############

# Load embedding model
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

# Create product & product list classes
class Product(BaseModel):
    name:str

class Products(BaseModel):
    products: List[Product]

@app.get("/recommend-products", response_model=Products)
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
    recs_db = {"products": []}
    for product in rec_dict.keys():
        product_recs = df_products[df_products.id.isin(rec_dict[product])]
        recs_db["products"].extend([Product(name=prod_name) for prod_name in product_recs.name.tolist()])

    response = Products(products=recs_db["products"])
    return response



########### ---------- UPCOMING SHOPPERS API FUNCTION ------------ #########
# Get order values data
print(f"Querying BigQuery for order values dataframe...")
ORDER_VALUES_QUERY  = f"""
WITH order_values AS (
    SELECT 
      order_id,
      SUM(sale_price) as order_value
    FROM `ecommerce-data-project-444616.the_look_ecommerce_constant.order_items`
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
FROM `ecommerce-data-project-444616.the_look_ecommerce_constant.orders` AS orders
    LEFT JOIN `ecommerce-data-project-444616.the_look_ecommerce_constant.users` AS users ON orders.user_id = users.id
    LEFT JOIN order_values on orders.order_id = order_values.order_id
ORDER BY orders.order_id;
"""
df_order_values = client.query_and_wait(ORDER_VALUES_QUERY).to_dataframe()
df_order_values['created_at'] = df_order_values.created_at.apply(lambda x : x.date())   # reformat 'created_at' column

# Get users data
print(f"Querying BigQuery for users dataframe...")
USERS_QUERY  = f"""
SELECT
  *
FROM `ecommerce-data-project-444616.the_look_ecommerce_constant.users`;
"""
df_users = client.query_and_wait(USERS_QUERY).to_dataframe()


# Create Gamma-Gamma Model based prediction model class
class PredictorGGF:
    def __init__(self, df_summary):
        self.model_name = "GGF"
        self.df_summary = df_summary
        self.correlation = self.df_summary[self.df_summary.frequency != 0][['monetary_value', 'frequency']].corr().values[0,1]

        return print(f"Correlation between shopper frequency & monetary value is : {float(self.correlation):.5f}.")

    def fit_bgf(self, penalty_coef : float=0.01):

        self.bgf = lifetimes.BetaGeoFitter(penalty_coef)
        self.bgf.fit(self.df_summary['frequency'],
                    self.df_summary['recency'],
                    self.df_summary['T'])

        print(f"Beta-Gamma model successfully fitted")
        return self.bgf.summary

    def fit_ggf(self, penalty_coef : float=0.01):
        assert self.correlation < 0.1, f"Correlation between frequency and monetary value for returning customers is {self.correlation} - this is quite high and may cause poor predictions"

        self.ggf = lifetimes.GammaGammaFitter(penalty_coef)
        self.ggf.fit(self.df_summary[self.df_summary.frequency != 0]['frequency'],
                     self.df_summary[self.df_summary.frequency != 0]['monetary_value'])

        print(f"Gamma-Gamma model successfully fitted")
        if float(self.ggf.params_['q']) < 1:
            print("Outliers in the data are causing the 'q' parameter for the Gamma-Gamma model to be < 1 therefore model predictions will fail.\nFix this by either removing outliers until you get 'q' > 1, or use raw monetary values to model CLV.")

        return self.ggf.summary
    
    def predict_clv(self, time : int=12, discount_rate : float=0.1, freq : str="D"):
        """Predict Customer Lifetime Value
        Args:
            time (float, optional) – the lifetime expected for the user in months. Default: 12
            discount_rate (float, optional) – the monthly adjusted discount rate. Default: 0.01
            freq (string, optional) – {“D”, “H”, “M”, “W”} for day, hour, month, week. This represents what unit of time your T is measure in.

        Returns:
            Series – Series object with customer ids as index and the estimated customer lifetime values as values
        """

        # Predict customer lifetime value
        clv_preds_df = self.ggf.customer_lifetime_value(
                            self.bgf,
                            self.df_summary['frequency'],
                            self.df_summary['recency'],
                            self.df_summary['T'],
                            self.df_summary['monetary_value'],
                            time=time,
                            discount_rate=discount_rate,
                            freq=freq
                        ).to_frame()
        
        return clv_preds_df

# Create shopper & shopper list classes
class Shopper(BaseModel):
    shopper_id:int
    name:str
    email:str
    age:int
    gender:str
    country:str
    pred_equity:float

class Shoppers(BaseModel):
    shoppers : List[Shopper]

@app.get("/upcoming-shoppers", response_model=Shoppers)
def upcomingShoppers():

    # Get RFM summary data
    df_rfm  = lifetimes.utils.summary_data_from_transaction_data(df_order_values, 'user_id', 'created_at',
                                                                 freq='D', include_first_transaction = False)
    df_rfm = pd.merge(df_rfm, df_order_values.groupby('user_id')['order_value'].agg(['mean', 'sum']), 
                      how='left', on='user_id').rename(columns={'mean' : 'monetary_value', 'sum' : 'revenue'})
    
    # Fit prediction model to RFM data
    model = PredictorGGF(df_rfm)
    bgf_summary = model.fit_bgf(penalty_coef=0.01)
    ggf_summary = model.fit_ggf(penalty_coef=0.01)

    # Predict shoppers equities over next 24 months
    pred_equity = model.predict_clv(time=24).rename(columns={'clv':'pred_equity'})   # Predict equity over next 24 months 

    # Select shoppers whose first purchase was less than 90 days ago and who's predicted equity is positive
    df_all = pd.merge(df_rfm, pred_equity, how = 'left', left_index=True, right_index=True)
    upcoming_shoppers = df_all[(df_all.pred_equity > 0) & (df_all['T'] < 90)].sort_values(by='pred_equity', ascending=False).index.to_list()

    shoppers_db = {"shoppers" : []}
    for id in upcoming_shoppers:
        shopper = df_users[df_users.id == id]
        shoppers_db["shoppers"].append(Shopper(shopper_id=shopper.id.values[0],
                                               name=shopper.first_name.values[0] + ' ' + shopper.last_name.values[0],
                                               email=shopper.email.values[0],
                                               age=shopper.age.values[0],
                                               gender=shopper.gender.values[0],
                                               country=shopper.country.values[0],
                                               pred_equity=round(df_all.loc[id].pred_equity,2)))
    
    response = Shoppers(shoppers=shoppers_db["shoppers"])
    return response
    





if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)