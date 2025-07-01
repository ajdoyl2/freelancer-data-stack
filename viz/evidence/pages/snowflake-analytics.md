# Snowflake Analytics Dashboard

This dashboard demonstrates Evidence.dev connected to Snowflake for analytics data.

```sql snowflake:analytics_overview
-- Example queries for Snowflake analytics
-- Replace with your actual table names and structure

SELECT 
    'Analytics Database' as source,
    COUNT(*) as total_records,
    CURRENT_TIMESTAMP() as last_updated
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'PUBLIC'
LIMIT 1;
```

## Connection Status

<DataTable 
    data={analytics_overview}
    search=true
    sort=true
/>

## Sample Snowflake Queries

```sql snowflake:sample_tables
-- Show available tables in the analytics database
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE,
    ROW_COUNT,
    CREATED
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'PUBLIC'
ORDER BY TABLE_NAME;
```

### Available Tables

<DataTable 
    data={sample_tables}
    rows=10
    search=true
    sort=true
/>

## Database Schema Information

```sql snowflake:schema_info
-- Get schema and column information
SELECT 
    TABLE_SCHEMA,
    COUNT(DISTINCT TABLE_NAME) as table_count,
    COUNT(*) as column_count
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA IN ('PUBLIC', 'ANALYTICS')
GROUP BY TABLE_SCHEMA
ORDER BY table_count DESC;
```

### Schema Summary

<BarChart 
    data={schema_info} 
    x=TABLE_SCHEMA 
    y=table_count
    title="Tables per Schema"
/>

## Data Quality Checks

*Note: Replace these queries with your actual data quality checks*

```sql snowflake:data_quality
-- Example data quality metrics
-- Modify based on your actual table structure
SELECT 
    'Sample Check' as check_name,
    'Passed' as status,
    100 as score,
    CURRENT_TIMESTAMP() as checked_at;
```

<BigValue 
    data={data_quality} 
    value=score
    title="Data Quality Score"
    fmt="#%"
/>

---

## Multi-Database Comparison

You can also query both DuckDB and Snowflake in the same dashboard:

```sql duckdb:local_data
SELECT 
    'DuckDB Local' as source,
    COUNT(*) as record_count
FROM sample_data;
```

```sql snowflake:remote_data
SELECT 
    'Snowflake Remote' as source,
    1 as record_count;  -- Placeholder
```

### Data Source Comparison

<BarChart 
    data={[...local_data, ...remote_data]} 
    x=source 
    y=record_count
    title="Local vs Remote Data Volume"
/>

---

*Connected to Snowflake: ${SNOWFLAKE_ACCOUNT}.snowflakecomputing.com*
