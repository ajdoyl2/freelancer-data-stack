{{
  config(
    materialized='table'
  )
}}

-- Customer summary model
SELECT
    id,
    name,
    email,
    created_at::date as signup_date,
    revenue,
    CASE
        WHEN revenue >= 1500 THEN 'High Value'
        WHEN revenue >= 1000 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment,
    CURRENT_TIMESTAMP as updated_at
FROM {{ source('raw', 'sample_data') }}
ORDER BY revenue DESC
