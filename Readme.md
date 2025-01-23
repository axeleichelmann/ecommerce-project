# Ecommerce Data Analysis & CLV Prediction App

> [!WARNING]
> All the metrics, plots, and insights are made up and taken from the internet

![network header](assets/header.jpeg)

# Dataset
The dataset used for this project is the [*The Look eCommerce*]((https://console.cloud.google.com/bigquery/analytics-hub/discovery/projects/1057666841514/locations/us/dataExchanges/google_cloud_public_datasets_17e74966199/listings/thelook_ecommerce)) dataset which is publicly available on Google BigQuery.

This dataset contains data from a fictitious eCommerce clothing site developed by the Looker team. The dataset consists of various different tables containing information about various topics such as customers, products, orders, inventory etc.

# Project Background

 The main objectives of this project are three-fold:
 > 1. **To analyse company data and uncover critical insights that will improve *The Look*'s commercial success**
 > 2. **To develop an API function that will identify recently acquired customer's with potential for large future revenue**
 > 3. **To develop an API function that will recommend products based on the customer's previous purchases**
 

 To achieve these objectives, we broke the problems down into the following mini-objectives:
 1. Analyse the data and uncover critical insights that will improve *theLook*'s commercial success:

      1.1 Analyse *theLook*'s database structure using SQL for familiarization with the dataset's table relationships.
   
      1.2 Uncover insights and provide recommendations on the following areas: sales trends, regional performance, customer analysis, and product level performance.
      
      1.3 Produce a high-level report of the insights uncovered, and an interactive Tableau dashboard displaying key metrics and graphs to accompany the report.

 2. Develop an API function that will identify recently acquired customer's with potential for large revenue:

      2.1 Import order data from Google BigQuery and calculate Recency, Frequency, and Monetary Value for all of *The Look*'s customers.

      2.2 Use the [lifetimes](https://lifetimes.readthedocs.io/en/latest/index.html) python package to predict future equity for *The Look*'s customers that made their first purchase less than 90 days ago.

      2.3 Return a list of customers that made their first purchase less than 90 days ago, who's predicted future equity is large.

 3. Develop an API that will recommend products based on the customer's previous purchases:
   
      3.1 Extract product data from Google BigQuery and create embeddings of the product names.
   
      3.2 Create a function which extracts a customer's order data from Google BigQuery and creates embeddings of the names of their previously purchased products.
   
      3.3 Use an LLM to evaluate the similarity between a customers previously purchased products, and all products available at *The Look*, and return a list of the most similar products.

The SQL queries used to clean, organize and prepare data for the project can be viewed [here](https://github.com/axeleichelmann/ecommerce-project/tree/main/queries)

# Data Structure & Initial Checks
*The Look*'s database structure consists of seven tables containing information on: users, events, orders, order items, products, inventory items, and distribution centers. These tables are related to each other through various shared keys as can be seen in the image below.
![Database Structure](assets/ERD.png)

# Executive Summary
### Overview of findings
Sales metrics across the board have seen impressive growth in 2024, with slight spikes during December which can be attributed to the christmas shopping demand. Compared to 2023, revenue has increased by 91.2%, profits by 91.1%, and order volume by 88.9%. While the overall company performance has been extremely good, the following sections will explore additional areas for improvement.

### Sales Trends:
* The company has seen consistent growth in sales and profits throughout 2024 with a fall to just below the yearly average in the final week of the year. This decrease can likely be attributed to the decrease in demand post-christmas period.
* The biggest client markets - China, United States, and Brazil - saw revenue increases of 91.5%, 92.2%, and 87.4% respectively and were responsible for 70.7% of the company's total revenue with China alone accounting for 33.6% of this. In 2025 efforts should be aimed at diversifying revenue sources by increasing marketing campaigns in medium sized markets such as South Korea, Spain, UK, France, and Germany.
* Australia and Poland made 1,148 and 117 orders respectively and brought in only $101.1k and $7.9k. We should increase marketing efforts in these regions due to their strong economic status and large populations making them countries with large potential for revenue. This will further help to diversify our regional portfolio.

Below is the sales overview page from the Tableau dashboard. The entire interactive dashboard can be viewed [here](https://public.tableau.com/app/profile/axel.eichelmann5606/viz/TheLook-eCommerceSalesAnalysis/SalesDashboard).

![Sales Dashboard](assets/SalesDashboard.png)

### Customer Analysis:
* In 2024 we received orders from 39,897 customers which was a 89.5% increase on the previous year's 23,713 customers. Of these customers, 6,973 (17.5%) made more than one order.
* $1,864,325 (41.3%) of our revenue in 2024 came from these 17.5% of customers that made more than one order. This highlights the importance of returning customers thus efforts should be made the promote repeat buying perhaps by offering deals to returning customers.
* 6 of the top 10 highest revenue customers in 2023 did not make a purchase in 2024 - 5 of these were multiple time buyers. Accordingly, protocols should be implemented in order to maintain relationships with high-value customers to prevent their churn.

Below is the customer overview page from the Tableau dashboard.

![Customer Dashboard](assets/CustomerDashboard.png)

### Product Analysis:
* The top performing category was outerwear & coats bringing in $546.3k of revenue followed closely by Jeans which sold $540.17k, and then Sweaters which sold $351.93k.
* 6 out of the top 10 highest revenue products in 2024 were cold weather jackets. Based on this and the previous insight, we should consider expanding the range of available products within the category of outerwear and coats in order to further increase sales in 2025.
* There were 2,128 products in our inventory that achieved no sales in 2024. We should consider removing these from out inventory through flash sales in order to minimize losses.

Below is the product overview page from the Tableau dashboard.

![Customer Dashboard](assets/ProductDashboard.png)








