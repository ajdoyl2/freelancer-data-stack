{{
  config(
    materialized='incremental',
    unique_key='metric_date',
    on_schema_change='fail'
  )
}}

with daily_metrics as (
    select
        cast(created_at as date) as metric_date,
        count(distinct case when status = 'completed' then project_id end) as completed_projects,
        count(distinct case when status = 'in_progress' then project_id end) as in_progress_projects,
        count(distinct case when status = 'pending' then project_id end) as pending_projects,
        sum(case when status = 'completed' then project_value else 0 end) as daily_completed_value,
        count(distinct freelancer_id) as active_freelancers,
        avg(project_value) as avg_project_value,
        {% if target.name == 'duckdb_local' %}
        'duckdb_local' as environment,
        {% else %}
        'snowflake_prod' as environment,
        {% endif %}
        current_timestamp as loaded_at
    from {{ ref('stg_projects') }}
    where created_at >= cast('{{ var("start_date") }}' as date)
        and created_at <= cast('{{ var("end_date") }}' as date)
        {% if is_incremental() %}
        -- this filter will only be applied on an incremental run
        and cast(created_at as date) > (select max(metric_date) from {{ this }})
        {% endif %}
    group by cast(created_at as date)
),

-- Generate a complete date series for the specified range
date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('" ~ var('start_date') ~ "' as date)",
        end_date="cast('" ~ var('end_date') ~ "' as date)"
    ) }}
),

final as (
    select
        ds.date_day as metric_date,
        coalesce(dm.completed_projects, 0) as completed_projects,
        coalesce(dm.in_progress_projects, 0) as in_progress_projects,
        coalesce(dm.pending_projects, 0) as pending_projects,
        coalesce(dm.daily_completed_value, 0) as daily_completed_value,
        coalesce(dm.active_freelancers, 0) as active_freelancers,
        dm.avg_project_value,
        dm.environment,
        coalesce(dm.loaded_at, current_timestamp) as loaded_at
    from date_spine ds
    left join daily_metrics dm on ds.date_day = dm.metric_date
    {% if is_incremental() %}
    where ds.date_day > (select max(metric_date) from {{ this }})
    {% endif %}
)

select * from final
