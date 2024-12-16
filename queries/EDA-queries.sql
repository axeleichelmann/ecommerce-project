#SELECT
#  COUNT(DISTINCT(id)) AS customer_count,
#  COUNT(DISTINCT(country)) AS country_count,
#FROM `ecommerce-data-project-444616.thelook_ecommerce.users`;

-- WITH order_values AS (
--   SELECT *
--   FROM `ecommerce-data-project-444616.thelook_ecommerce.orders` AS orders
--   LEFT JOIN `ecommerce-data-project-444616.thelook_ecommerce.order_items` AS order_items
--   ON orders.order_id = order_items.order_id
-- )
-- SELECT *
-- FROM order_values
-- LIMIT 1000;


---- GET ORDER VALUES OF COMPLETE ORDERS------
-- WITH order_values AS (SELECT 
--                         order_id,
--                         SUM(sale_price) as order_value
--                       FROM `ecommerce-data-project-444616.thelook_ecommerce.order_items`
--                       GROUP BY order_id
--                       ORDER BY order_id)
-- SELECT 
--   MIN(order_values.order_value) AS min_order_val,
--   MAX(order_values.order_value) AS max_order_val,
--   AVG(order_values.order_value) AS avg_order_val
-- FROM order_values WHERE order_values.status = 'Complete'

----- GET CUSTOMERS' REALIZED REVENUE -----
WITH adjusted_prices AS (
  SELECT order_id, user_id, status, sale_price,
    CASE 
        WHEN status = 'Returned' THEN -0.15*sale_price  # Assume return shipping costs 15% of item cost
        WHEN status = 'Cancelled' THEN 0
        ELSE sale_price 
    END AS adjusted_sale_price
  FROM `ecommerce-data-project-444616.thelook_ecommerce.order_items`
)
SELECT
  adjusted_prices.user_id,
  users.first_name, users.last_name, users.email,
  SUM(adjusted_prices.adjusted_sale_price) AS realized_revenue
FROM adjusted_prices
LEFT JOIN `ecommerce-data-project-444616.thelook_ecommerce.users` AS users
ON adjusted_prices.user_id = users.id
GROUP BY user_id
LIMIT 100;


