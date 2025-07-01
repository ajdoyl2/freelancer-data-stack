# Data Quality Dashboard

## Great Expectations Validation Results

This dashboard provides an overview of data quality checks and validation results from Great Expectations.

```sql validation_results
SELECT 
    expectation_suite_name,
    run_name,
    run_time,
    success,
    statistics_validated_expectations,
    statistics_successful_expectations,
    statistics_unsuccessful_expectations,
    statistics_success_percent
FROM great_expectations.validations 
ORDER BY run_time DESC 
LIMIT 50;
```

### Validation Success Rate Over Time

<LineChart 
    data={validation_results} 
    x=run_time 
    y=statistics_success_percent
    series=expectation_suite_name
    title="Data Quality Success Rate Over Time"
/>

### Recent Validation Summary

<DataTable 
    data={validation_results}
    rows=10
    search=true
    sort=true
/>

## Data Quality Metrics

```sql quality_metrics
SELECT 
    expectation_suite_name,
    COUNT(*) as total_runs,
    AVG(statistics_success_percent) as avg_success_rate,
    MIN(statistics_success_percent) as min_success_rate,
    MAX(statistics_success_percent) as max_success_rate,
    COUNT(CASE WHEN success = true THEN 1 END) as successful_runs,
    COUNT(CASE WHEN success = false THEN 1 END) as failed_runs
FROM great_expectations.validations 
GROUP BY expectation_suite_name
ORDER BY avg_success_rate DESC;
```

### Quality Metrics by Suite

<BarChart 
    data={quality_metrics} 
    x=expectation_suite_name 
    y=avg_success_rate
    title="Average Success Rate by Expectation Suite"
/>

### Suite Performance Summary

<DataTable 
    data={quality_metrics}
    search=true
    sort=true
/>

## Failed Expectations Details

```sql failed_expectations
SELECT 
    expectation_suite_name,
    run_name,
    run_time,
    expectation_type,
    column_name,
    result_element_count,
    result_missing_count,
    result_unexpected_count
FROM great_expectations.validation_results 
WHERE success = false
ORDER BY run_time DESC
LIMIT 100;
```

### Recent Failures

<DataTable 
    data={failed_expectations}
    rows=20
    search=true
    sort=true
/>

---

*Data updated: {validation_results[0].run_time}*

## Navigation Links

- [Great Expectations Data Docs](http://localhost:8888/view/great-expectations/data_docs/local_site/index.html)
- [DataHub Lineage](http://localhost:9002)
- [Prometheus Metrics](http://localhost:9090)
- [Grafana Dashboards](http://localhost:3000)
