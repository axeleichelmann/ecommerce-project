-- Cleaning, combining, and organizing data for use

-- During the data exploration phase we discovered irregularities & inconsistencies which we will now correct

-- 1) Create clean 'products' dataframe
WITH category_counts AS (
    SELECT 
        name,
        category,
        COUNT(*) AS category_count
    FROM `ecommerce-data-project-444616.thelook_ecommerce.products`
    GROUP BY name, category
),
ranked_categories AS (
    SELECT 
        name,
        category,
        category_count,
        RANK() OVER (PARTITION BY name ORDER BY category_count DESC, category ASC) AS rank
    FROM category_counts
),
majority_categories AS (
    SELECT 
        name,
        category AS majority_category
    FROM ranked_categories
    WHERE rank = 1
),
cleaned_products AS (
  SELECT
    id,
    ROUND(cost,2) AS cost,
    products.name AS name,
    brand,
    ROUND(retail_price,2) AS retail_price,
    department,
    CASE 
      WHEN majority_categories.majority_category = 'Pants' THEN 'Pants & Capris'
      WHEN majority_categories.majority_category = 'Socks' THEN 'Socks & Hosiery'
      WHEN majority_categories.majority_category = 'Suits' THEN 'Suits & Sport Coats'
      ELSE majority_categories.majority_category
    END AS category
  FROM `ecommerce-data-project-444616.thelook_ecommerce.products` AS products
  LEFT JOIN majority_categories ON products.name = majority_categories.name
),


-- 2) Create clean version of 'users' dataframe
cleaned_users AS (
  SELECT 
    id,
    first_name,
    last_name,
    email,
    age,
    gender,
    state,
    street_address,
    postal_code,
    city,
    CASE
      WHEN country='España' THEN 'Spain'
      WHEN country='Deutschland' THEN 'Germany'
      ELSE country
    END AS country,
    traffic_source,
    created_at
  FROM `ecommerce-data-project-444616.thelook_ecommerce.users`
),
-- 3) Create clean version of 'orders' table
cleaned_orders AS (
  SELECT
    orders.order_id,
    orders.user_id,
    orders.status,
    DATE(orders.created_at) AS created_at,
    DATE(orders.shipped_at) AS shipped_at,
    DATE(orders.delivered_at) AS delivered_at,
    DATE(orders.returned_at) AS returned_at,
    order_values.order_value,
    orders.num_of_item
  FROM `ecommerce-data-project-444616.thelook_ecommerce.orders` AS orders
  LEFT JOIN (
    SELECT 
      order_id,
      SUM(ROUND(sale_price,2)) AS order_value
    FROM `ecommerce-data-project-444616.thelook_ecommerce.order_items`
    GROUP BY order_id) AS order_values
  ON orders.order_id = order_values.order_id
),

-- 4) Create clean version of 'order_items' table
cleaned_order_items AS (
  SELECT
    order_items.order_id,
    order_items.user_id,
    order_items.product_id,
    order_items.inventory_item_id,
    order_items.status,
    ROUND(order_items.sale_price,2) AS sale_price,
  FROM `ecommerce-data-project-444616.thelook_ecommerce.order_items` AS order_items
),

-- 5) Create clean version of 'inventory_items' table
cleaned_inventory_items AS (
  SELECT
    id,
    product_id,
    created_at AS added_to_inventory_at
  FROM `ecommerce-data-project-444616.thelook_ecommerce.inventory_items`
),

-- 6) Create clean version of 'events' table
cleaned_events AS (
  SELECT
    user_id,
    sequence_number,
    session_id,
    created_at AS event_occured_at,
    ip_address,
    event_type
  FROM `ecommerce-data-project-444616.thelook_ecommerce.events`
)




-- Prepare data table to use for Tableau dashboard creation
SELECT
  cleaned_orders.*,
  cleaned_products.cost,
  cleaned_products.name,
  cleaned_products.brand,
  cleaned_products.retail_price,
  cleaned_products.department,
  cleaned_products.sku,
  cleaned_products.distribution_center_id,
  cleaned_products.category,
  cleaned_users.traffic_source,
  cleaned_users.country,
  cleaned_users.city,
FROM cleaned_orders
LEFT JOIN cleaned_products ON cleaned_orders.product_id = cleaned_products.id
LEFT JOIN cleaned_users ON cleaned_orders.user_id = cleaned_users.id;











