{{ config(materialized='view') }}

with source_data as (
    select
        freelancer_id,
        name,
        email,
        skill_category,
        cast(hourly_rate as decimal(10,2)) as hourly_rate,
        cast(join_date as date) as join_date,
        location,
        cast(rating as decimal(3,2)) as rating,
        current_timestamp as loaded_at
    from {{ ref('freelancers') }}
)

select * from source_data
