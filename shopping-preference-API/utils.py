from sentence_transformers import SentenceTransformer
import lifetimes
import sklearn
import pandas as pd
from datetime import datetime


###### Product Recommendation Utility Functions #######
def getQuery(customer_id : int, df_orders : pd.DataFrame):
    """
    Get a list of customers' purchased products.
    """

    # Get list of customer's purchased products
    customer_purchases = df_orders[(df_orders.user_id == customer_id) & (df_orders.status != 'Cancelled')]
    purchased_products = customer_purchases.product_name.tolist()

    return purchased_products


def getEmbeddings(model, df_products):
    """
    Create embeddings for product names.
    """

    # Get embedding of product names
    embedding_arr = model.encode(df_products['name'].to_list())

    # Store embeddings in a dataframe
    df_embedding = pd.DataFrame(embedding_arr)
    df_embedding.columns = ['product-embedding-'+str(i) for i in range(embedding_arr.shape[1])]

    # Add product details to embedding dataframe
    df_embedding = pd.concat([df_products, df_embedding], axis=1)
    
    return df_embedding

def getRecommendationDict(model, queries, df_embedding, df_products, metric, top_k : int=5):
    """
    Create a dictionary containing a customers' previously purchased products, and the ids of the corresponding recommended products for each purchased product. 
    """
    # Initiate dictionary
    rec_dict = {}

    # Loop through previously purchased products
    for query in queries:
        query_embedding = model.encode(query).reshape(1,-1)   # Create embedding for purchased product's name
        query_dist = metric.pairwise(df_embedding.values[:,9:], query_embedding).flatten()   # Calculate distance between purchased product embedding & embeddings of all available products
        query_dist_df = pd.DataFrame({'product_id' : df_products.id,    # Store distance results in a dataframe
                                    'dist' : query_dist})
        rec_dict[query] = query_dist_df.sort_values(by='dist').product_id.head(top_k).tolist()    # Add purchased product's top k most similar products to dictionary

    return rec_dict

def getProducts(product_id_list : list, df_products : pd.DataFrame):
    """
    Get slice of products dataframe containing products whose ID is in 'product_id_list' argument.
    """
    return df_products[df_products.id.isin(product_id_list)]



def getRecommendedProducts(customer_id : int,
                           model : SentenceTransformer, metric : sklearn.metrics,
                           df_orders : pd.DataFrame, df_products : pd.DataFrame,
                           top_k : int=5):
    """
    Get dataframe containing recommendations for future product purchases given a customers previous purchases.
    """
    
    print(f"Creating embeddings...")
    start_time = datetime.now()
    df_embedding = getEmbeddings(model, df_products)
    end_time = datetime.now()
    print(f"Embeddings created - Time Taken = {end_time - start_time}")

    print(f"Retrieving customers previous orders...")
    start_time = datetime.now()
    queries = getQuery(customer_id, df_orders)
    end_time = datetime.now()
    print(f"Customer orders retrieved - Time Taken = {end_time - start_time}")

    print(f"Creating product recommendation dictionary...")
    start_time = datetime.now()
    rec_dict = getRecommendationDict(model, queries, df_embedding, df_products, metric, top_k)
    end_time = datetime.now()
    print(f"Product recommendation dictionary created - Time Taken = {end_time - start_time}")


    print(f"Creating recommended product dataframe...")
    start_time = datetime.now()
    df_recs = pd.DataFrame(columns=df_products.columns)
    for product in rec_dict.keys():
        print(f"Getting products related to {product}")
        product_recs = getProducts(rec_dict[product], df_products)
        df_recs = pd.concat([df_recs, product_recs], axis=0)
    end_time = datetime.now()
    print(f"Recommended product dataframe created - Time Taken = {end_time - start_time}")

    return df_recs


###### High Value Shopper Prediction Functions #######
# Gamma-Gamma Model based prediction model class
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

# Raw Monetary Value based prediction model class
class PredictorRawMonetary:
    def __init__(self, df_summary):
        self.model_name = "Raw Monetary Value"
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
        clv_preds_df = lifetimes.utils._customer_lifetime_value(
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


# Dataset creation functions
def getRFMData(df : pd.DataFrame):
    """Get RFM summary dataframe.
    
    Args:
        df - dataframe containing order values data
        
    Returns:
        Tuple[df_train_rfm, df_test_rfm, df_all_rfm]
    """
            
    # Create copy of dataset & reformat 'created_at' column
    df1 = df.copy()
    df1['created_at'] = df1.created_at.apply(lambda x : x.date())

    # Get RFM summary data from training period
    df_train_rfm  = lifetimes.utils.summary_data_from_transaction_data(df1, 'user_id', 'created_at',
                                                                       freq='D', include_first_transaction = False)
    df_train_rfm = pd.merge(df_train_rfm, df1.groupby('user_id')['order_value'].agg(['mean', 'sum']), 
                            how='left', on='user_id').rename(columns={'mean' : 'monetary_value', 'sum' : 'revenue'})

    return df_train_rfm

# Fit prediction model
def getFittedModel(df_train : pd.DataFrame, model_class, penalty_val : float=0.01):
    """Fit the prediction model to the historic order data"""

    model = model_class(df_train)
    bgf_summary = model.fit_bgf(penalty_coef=penalty_val)
    ggf_summary = model.fit_ggf(penalty_coef=penalty_val)

    return model

# Future Equity Prediction function
def getPredEquity(model,
                  prediction_period_duration : int=12,
                  discount_rate : float=0.1, freq : str="D"):
    """Predict the future equity of shoppers during the prediction period.
    
    Args:
        model - prediction model that has already been fitted with the training dataset
        prediction_period_duration - duration of the prediction period in months
        
    Returns:
        pred_equity - dataframe containing predicted equity for each shopper
    """
    
    pred_equity = model.predict_clv(prediction_period_duration, discount_rate, freq).rename(columns={'clv':'pred_equity'})

    return pred_equity


# Upcoming Shopper Identification function
def getUpcomingShoppers(df_order_values : pd.DataFrame, df_users : pd.DataFrame,
                        model_class,
                        penalty_val : float=0.01):
    """Get dataframe of shoppers whose first purchase was less than 90 days ago, and who'se predicted future equity is large"""

    print(f"Creating RFM summary dataframe...")
    start_time = datetime.now()
    df_rfm = getRFMData(df_order_values)
    end_time = datetime.now()
    print(f"RFM summary dataframe created - Time Taken = {end_time - start_time}")

    # Fit model to training data
    print(f"Fitting prediction model to historic order data...")
    start_time = datetime.now()
    model = getFittedModel(df_rfm, model_class, penalty_val)
    end_time = datetime.now()
    print(f"{model.model_name} prediction model fitted - Time Taken = {end_time - start_time}")

    # Predict shopper equity during prediction period
    print(f"Predicting shoppers' future equity...")
    start_time = datetime.now()
    pred_equity = getPredEquity(model, prediction_period_duration=8)
    end_time = datetime.now()
    print(f"Successfully predicted future equity - Time Taken = {end_time - start_time}")

    # Identify shoppers whose first purchase was less than 90 days ago, and who'se predicted future equity is large
    print(f"Identifying upcoming high value shoppers...")
    start_time = datetime.now()
    df_all = pd.merge(df_rfm, pred_equity, how = 'left', left_index=True, right_index=True)
    if model.model_name == "GGF":
        upcoming_shoppers = df_rfm[(df_all.pred_equity > 0) & (df_all['T'] < 90)].index.to_list()
    else:
        upcoming_shoppers = df_rfm[(df_all.pred_equity > 25) & (df_all['T'] < 90)].index.to_list()
    end_time = datetime.now()
    print(f"Successfully identified upcoming high value shoppers - Time Taken = {end_time - start_time}")

    return df_users[df_users.id.isin(upcoming_shoppers)]




