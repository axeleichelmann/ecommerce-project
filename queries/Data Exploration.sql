-- Utilizing dataset for the first time, performing checks for inconsistensies, errors, and data ranges

-- 1.1) Check for duplicate orders in 'orders' table
SELECT
  order_id,
  COUNT(*) AS order_id_count
FROM `ecommerce-data-project-444616.thelook_ecommerce.orders`
GROUP BY order_id
HAVING order_id_count > 1;

-- 1.2) Check for null values in 'orders' table
SELECT
  SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS nullcount_order_id,
  SUM(CASE WHEN user_id IS NULL THEN 1 ELSE 0 END) AS nullcount_user_id,
  SUM(CASE WHEN status IS NULL THEN 1 ELSE 0 END) AS nullcount_status,
  SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) AS nullcount_gender,
  SUM(CASE WHEN created_at IS NULL THEN 1 ELSE 0 END) AS nullcount_created_at,
  SUM(CASE WHEN returned_at IS NULL THEN 1 ELSE 0 END) AS nullcount_returned_at,
  SUM(CASE WHEN shipped_at IS NULL THEN 1 ELSE 0 END) AS nullcount_shipped_at, -- these orders are either cancelled or still being processed
  SUM(CASE WHEN delivered_at IS NULL THEN 1 ELSE 0 END) AS nullcount_delivered_at, -- these orders are either cancelled, still being processed, or shipped
  SUM(CASE WHEN num_of_item IS NULL THEN 1 ELSE 0 END) AS nullcount_num_of_item
FROM `ecommerce-data-project-444616.thelook_ecommerce.orders`;

-- 1.3) Investigate null values for 'shipped_at' and 'delivered_at' columns in 'orders' table
SELECT
  DISTINCT(status)
FROM `ecommerce-data-project-444616.thelook_ecommerce.orders`
WHERE shipped_at IS NULL;

SELECT
  DISTINCT(status)
FROM `ecommerce-data-project-444616.thelook_ecommerce.orders`
WHERE delivered_at IS NULL;

-- 2) Check distinct product names, product categories, traffic sources, countries, and departments for familiarity and finding irregularities
SELECT -- 1568 product names with more than 1 id
  DISTINCT name,
  COUNT(id) AS count_ids
FROM `ecommerce-data-project-444616.thelook_ecommerce.products`
GROUP BY 1
HAVING count_ids>1
ORDER BY 1;

SELECT -- need to combine 'Pants' and 'Pants & Capris' categories, 'Socks' and 'Socks & Hoiseries' categories, and 'Suits' and 'Suits & SPorts Coats' categories
  DISTINCT category,
  COUNT(name) as count_products
FROM `ecommerce-data-project-444616.thelook_ecommerce.products`
GROUP BY 1
ORDER BY 1;

SELECT
  DISTINCT traffic_source,
FROM `ecommerce-data-project-444616.thelook_ecommerce.users`;

SELECT -- need to combine 'España' and 'Spain' cases
  DISTINCT country
FROM `ecommerce-data-project-444616.thelook_ecommerce.users`
ORDER BY 1;

SELECT 
  DISTINCT department
FROM `ecommerce-data-project-444616.thelook_ecommerce.products`
ORDER BY 1;


-- 3) Check date ranges for purchases, shipping, delivery, returns, to understand time frames
SELECT
  MIN(created_at) AS earliest_order_date,
  MAX(created_at) AS latest_order_date,
  MIN(shipped_at) AS earliest_shipping_date,
  MAX(shipped_at) AS latest_shipping_date,
  MIN(delivered_at) AS earliest_delivery_date,
  MAX(delivered_at) AS latest_delivery_date,
  MIN(returned_at) AS earliest_return_date,
  MAX(returned_at) AS latest_return_date,
FROM `ecommerce-data-project-444616.thelook_ecommerce.orders`;

SELECT 
   APPROX_QUANTILES(TIMESTAMP_DIFF(shipped_at, created_at, HOUR), 4) AS processing_duration_hours_quantiles,
   APPROX_QUANTILES(TIMESTAMP_DIFF(delivered_at, shipped_at, DAY), 4) AS delivery_duration_days_quantiles,
   APPROX_QUANTILES(TIMESTAMP_DIFF(returned_at, delivered_at, DAY), 4) AS return_period_days_quantiles,
FROM `ecommerce-data-project-444616.thelook_ecommerce.orders`;

-- 4) Check product costs & retail prices, order values & sizes
WITH order_data AS (
  SELECT 
    orders.order_id,
    orders.num_of_item,
    order_items.order_value
  FROM `ecommerce-data-project-444616.thelook_ecommerce.orders` AS orders
  LEFT JOIN
    (SELECT
      order_id,
      ROUND(SUM(sale_price),2) AS order_value
    FROM `ecommerce-data-project-444616.thelook_ecommerce.order_items`
    GROUP BY order_id) AS order_items
  ON orders.order_id = order_items.order_id)
SELECT 
   APPROX_QUANTILES(order_value, 4) AS order_value_quantiles,
   APPROX_QUANTILES(num_of_item, 4) AS num_of_item_quantiles,
FROM order_data;

SELECT
 name,
 cost,
 retail_price,
 retail_price - cost AS retail_profit_margin
FROM `ecommerce-data-project-444616.thelook_ecommerce.products`;

SELECT 
   APPROX_QUANTILES(ROUND(cost,2), 4) AS product_cost_quantiles,
   APPROX_QUANTILES(ROUND(retail_price,2), 4) AS retail_price_quantiles,
   APPROX_QUANTILES(ROUND(retail_price - cost,2), 4) AS retail_profit_margin_quantiles,
FROM `ecommerce-data-project-444616.thelook_ecommerce.products`;



