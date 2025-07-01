{{ config(materialized='view') }}

with source_data as (
    select
        project_id,
        title,
        description,
        client_id,
        freelancer_id,
        cast(project_value as decimal(10,2)) as project_value,
        cast(start_date as date) as start_date,
        cast(end_date as date) as end_date,
        status,
        cast(created_at as timestamp) as created_at,
        current_timestamp as loaded_at
    from {{ ref('projects') }}
)

select * from source_data
