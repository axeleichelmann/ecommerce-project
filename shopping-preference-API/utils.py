from sentence_transformers import SentenceTransformer
import sklearn
import pandas as pd
from datetime import datetime

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