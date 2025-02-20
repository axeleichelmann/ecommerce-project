# Import modules to acces GCP
import os
from google.cloud import storage, bigquery
storage_client = storage.Client()
bigquery_client = bigquery.Client()

# Import automation modules
from datetime import datetime

# Import packages to create product embeddings
import pandas as pd
import lifetimes
import io
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
        return self.bgf.summary

    def fit_ggf(self, penalty_coef : float=0.01):
        assert self.correlation < 0.1, f"Correlation between frequency and monetary value for returning customers is {self.correlation} - this is quite high and may cause poor predictions"

        self.ggf = lifetimes.GammaGammaFitter(penalty_coef)
        self.ggf.fit(self.df_summary[self.df_summary.frequency != 0]['frequency'],
                     self.df_summary[self.df_summary.frequency != 0]['monetary_value'])
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


#### Create dataframe with upcoming high-value shopper data
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
WHERE orders.status != 'Cancelled'
ORDER BY orders.order_id;
"""
df_order_values = bigquery_client.query_and_wait(ORDER_VALUES_QUERY).to_dataframe()
df_order_values['created_at'] = df_order_values.created_at.apply(lambda x : x.date())   # reformat 'created_at' column

print(f"Querying BigQuery for users dataframe...")
USERS_QUERY  = f"""
SELECT
  *
FROM `ecommerce-data-project-444616.the_look_ecommerce_constant.users`;
"""
df_users = bigquery_client.query_and_wait(USERS_QUERY).to_dataframe()

print(f"Identifying Upcoming High Value Shoppers...")
start_time = datetime.now()
df_rfm  = lifetimes.utils.summary_data_from_transaction_data(df_order_values, 'user_id', 'created_at',
                                                             freq='D', include_first_transaction = False)
df_rfm = pd.merge(df_rfm, df_order_values.groupby('user_id')['order_value'].agg(['mean', 'sum']), 
                  how='left', on='user_id').rename(columns={'mean' : 'monetary_value', 'sum' : 'revenue'})
model = PredictorGGF(df_rfm)
bgf_summary = model.fit_bgf(penalty_coef=0.01)
ggf_summary = model.fit_ggf(penalty_coef=0.01)
pred_equity = model.predict_clv(time=24).rename(columns={'clv':'pred_equity'})   # Predict equity over next 24 months 
df_all = pd.merge(df_rfm, pred_equity, how = 'left', left_index=True, right_index=True)   # Merge predicted equity with RFM data
pred_equity_threshold = 100
upcoming_shoppers = df_all[(df_all.pred_equity > pred_equity_threshold) & (df_all['T'] < 90)].sort_values(by='pred_equity', ascending=False).index.to_list()
shoppers_data = {"shopper_id" : [], "name" : [], "email" : [], "pred_equity" : []}
for id in upcoming_shoppers:
    shopper = df_users[df_users.id == id]
    shoppers_data["shopper_id"].append(shopper.id.values[0])
    shoppers_data["name"].append(shopper.first_name.values[0] + ' ' + shopper.last_name.values[0])
    shoppers_data["email"].append(shopper.email.values[0])
    shoppers_data["pred_equity"].append(round(df_all.loc[id].pred_equity,2))
upcoming_shoppers_df = pd.DataFrame(shoppers_data)
print(f"Finished identifying upcoming high value shoppers - Time Taken = {datetime.now() - start_time}")

print(f"Saving Upcoming Shoppers Data to CSV Buffer...")
start_time = datetime.now()
csv_buffer = io.BytesIO()
upcoming_shoppers_df.to_csv(csv_buffer, index=False)  # Convert DataFrame to CSV
csv_buffer.seek(0)
print(f"Finished saving upcoming shopper data - Time Taken = {datetime.now() - start_time}")


#### Upload new embeddings dataframe to bucket
print(f"Connecting to storage bucket...")
bucket = storage_client.get_bucket("bucket-quickstart_ecommerce-data-project-444616")
blob = bucket.blob("upcoming_shoppers.csv")
print(f"Uploading upcoming shoppers data to storage bucket...")
start_time = datetime.now()
blob.upload_from_file(csv_buffer, content_type="text/csv")
print(f"Finished uploading upcoming shoppers data - Time Taken = {datetime.now() - start_time}")