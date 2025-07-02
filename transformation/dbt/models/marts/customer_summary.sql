{{
  config(
    materialized='table'
  )
}}

-- Customer summary with segmentation
SELECT
    CAST(id AS INTEGER) as customer_id,
    name as customer_name,
    email as customer_email,
    CAST(created_at AS DATE) as signup_date,
    CAST(revenue AS DECIMAL(10,2)) as revenue,
    CASE
        WHEN CAST(revenue AS DECIMAL(10,2)) >= 1500 THEN 'High Value'
        WHEN CAST(revenue AS DECIMAL(10,2)) >= 1000 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment,
    CURRENT_TIMESTAMP as updated_at
FROM {{ source('raw', 'sample_data') }}
ORDER BY revenue DESC
