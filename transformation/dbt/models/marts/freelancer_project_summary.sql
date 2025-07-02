{{ config(materialized='table') }}

with freelancer_projects as (
    select
        f.freelancer_id,
        f.name,
        f.skill_category,
        f.hourly_rate,
        f.rating,
        f.location,
        f.join_date,
        p.project_id,
        p.title as project_title,
        p.project_value,
        p.status,
        p.start_date,
        p.end_date,
        p.created_at
    from {{ ref('stg_freelancers') }} f
    left join {{ ref('stg_projects') }} p
        on f.freelancer_id = p.freelancer_id
),

summary_stats as (
    select
        freelancer_id,
        name,
        skill_category,
        hourly_rate,
        rating,
        location,
        join_date,
        count(project_id) as total_projects,
        count(case when status = 'completed' then 1 end) as completed_projects,
        count(case when status = 'in_progress' then 1 end) as in_progress_projects,
        count(case when status = 'pending' then 1 end) as pending_projects,
        sum(case when status = 'completed' then project_value else 0 end) as total_completed_value,
        avg(case when status = 'completed' then project_value end) as avg_project_value,
        min(start_date) as first_project_date,
        max(end_date) as latest_project_date
    from freelancer_projects
    group by 1,2,3,4,5,6,7
)

select * from summary_stats
