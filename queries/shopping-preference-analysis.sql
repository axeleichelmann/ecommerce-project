######### Get Data for Shopping Preference Analysis ##########
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
FROM `ecommerce-data-project-444616.thelook_ecommerce.order_items` as order_items
LEFT JOIN `ecommerce-data-project-444616.thelook_ecommerce.users` as users
ON order_items.user_id = users.id
LEFT JOIN `ecommerce-data-project-444616.thelook_ecommerce.products` as products
ON order_items.product_id = products.id
ORDER BY order_items.user_id
LIMIT 100;

######## Get list of products available from 'theLook' #########
SELECT *
FROM `ecommerce-data-project-444616.thelook_ecommerce.products`;

