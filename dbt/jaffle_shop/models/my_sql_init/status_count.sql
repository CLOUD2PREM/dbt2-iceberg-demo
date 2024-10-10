{{ config(materialized='table') }}

WITH order_status AS (
    SELECT
        icc.id AS customer_id,
        CEIL(ROW_NUMBER() OVER (ORDER BY icc.id) / 10.0) AS teams,
        ico.status
    FROM 
        {{ source('jaffle_shop_iceberg', 'clean_customers') }} icc
    INNER JOIN 
        {{ source('jaffle_shop_iceberg', 'clean_orders') }} ico 
    ON icc.id = ico.user_id
    INNER JOIN 
        {{ source('jaffle_shop_iceberg', 'clean_payments') }} icp
    ON ico.id = icp.order_id
)
SELECT 
    os.teams,
    os.status,
    COUNT(*) AS status_count
FROM 
    order_status os
GROUP BY 
    os.teams, os.status
ORDER BY 
    os.teams DESC
