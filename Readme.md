# Ecommerce Data Analysis & CLV Prediction App

> [!WARNING]
> All the metrics, plots, and insights are made up and taken from the internet

![network header](assets/header.jpeg)

# Dataset
The dataset used for this project is the 'theLook eCommerce' dataset which is publicly available on [Google BigQuery](https://console.cloud.google.com/bigquery/analytics-hub/discovery/projects/1057666841514/locations/us/dataExchanges/google_cloud_public_datasets_17e74966199/listings/thelook_ecommerce).

This dataset contains data from a fictitious eCommerce clothing site developed by the Looker team. The dataset consists of various different tables containing information about various topics such as customers, products, orders, inventory etc.

# Objectives

 The main objective of this project is:
 > **To develop a system that will identify high value shoppers recommend personalised advertising strategies for these customers**

 To achieve this objective, we broke it down into the following mini-objectives:
 1. Perform in depth exploratory data analysis of the *orders*, *order_items*, *products*, *events*, and *users* tables.
 2. Develop a CLV (customer lifetime value) prediction model and use it to identify high value shoppers.
 3. Develop a function that identifies a customer's shopping preferences based on their previous transactions.
 4. Combine the above two processes to create an app which recommends shoppers for targeted advertisement, and suggests items to promote.
 5. Create containerized version of the app and deploy it to GCP.