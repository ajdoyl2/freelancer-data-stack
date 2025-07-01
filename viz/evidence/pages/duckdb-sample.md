# DuckDB Sample Dashboard

This dashboard demonstrates Evidence.dev connected to DuckDB with sample project data.

```sql sample_projects
SELECT 
    id,
    name,
    value,
    created_date,
    CASE 
        WHEN value > 2000 THEN 'High Value'
        WHEN value > 1000 THEN 'Medium Value'
        ELSE 'Low Value'
    END as value_category
FROM sample_data 
ORDER BY created_date DESC;
```

## Project Overview

<DataTable 
    data={sample_projects}
    search=true
    sort=true
/>

## Project Values Over Time

<LineChart 
    data={sample_projects} 
    x=created_date 
    y=value
    title="Project Values Over Time"
/>

## Value Distribution

<BarChart 
    data={sample_projects} 
    x=name 
    y=value
    title="Project Value Comparison"
/>

## Summary Statistics

```sql project_stats
SELECT 
    COUNT(*) as total_projects,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    SUM(value) as total_value
FROM sample_data;
```

<BigValue 
    data={project_stats} 
    value=total_projects
    title="Total Projects"
/>

<BigValue 
    data={project_stats} 
    value=avg_value
    title="Average Value"
    fmt="$#,##0.00"
/>

<BigValue 
    data={project_stats} 
    value=total_value
    title="Total Value"
    fmt="$#,##0.00"
/>

---

*Data source: DuckDB - main.db*
