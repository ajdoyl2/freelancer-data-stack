# 🐛 Debugging Prompts Index

## Available Prompts

### Error Analysis & Resolution
- **[error_analysis.md](error_analysis.md)** - Systematic error investigation and resolution
- **[production_issues.md](production_issues.md)** - Live system troubleshooting
- **[performance_debugging.md](performance_debugging.md)** - Performance bottleneck identification
- **[memory_issues.md](memory_issues.md)** - Memory leak and usage problems

### Data Pipeline Debugging
- **[pipeline_failures.md](pipeline_failures.md)** - Data pipeline failure diagnosis
- **[data_quality_issues.md](data_quality_issues.md)** - Data validation and quality problems
- **[dagster_debugging.md](dagster_debugging.md)** - Dagster-specific troubleshooting
- **[dbt_debugging.md](dbt_debugging.md)** - dbt model and compilation issues

### Integration & Connectivity
- **[api_debugging.md](api_debugging.md)** - API connection and response issues
- **[database_debugging.md](database_debugging.md)** - Database connectivity and query problems
- **[docker_debugging.md](docker_debugging.md)** - Container and service issues
- **[network_debugging.md](network_debugging.md)** - Network connectivity problems

### Monitoring & Observability
- **[log_analysis.md](log_analysis.md)** - Log investigation and pattern analysis
- **[metrics_debugging.md](metrics_debugging.md)** - Monitoring and alerting issues
- **[trace_analysis.md](trace_analysis.md)** - Distributed tracing investigation
- **[health_check_debugging.md](health_check_debugging.md)** - System health monitoring

## Quick Reference Commands

```bash
# Emergency debugging workflow
cat prompts/debugging/production_issues.md

# Search for specific error patterns
grep -r "ConnectionError" prompts/debugging/

# List all debugging prompts
ls prompts/debugging/*.md
```

## Emergency Debugging Workflow

### 1. Production Incident Response
```
1. production_issues.md - Immediate triage
2. error_analysis.md - Root cause analysis
3. log_analysis.md - Evidence gathering
4. health_check_debugging.md - System assessment
```

### 2. Data Pipeline Issues
```
1. pipeline_failures.md - Identify failure point
2. dagster_debugging.md - Orchestration issues
3. dbt_debugging.md - Transformation problems
4. data_quality_issues.md - Validation failures
```

### 3. Performance Problems
```
1. performance_debugging.md - Identify bottlenecks
2. memory_issues.md - Memory optimization
3. database_debugging.md - Query optimization
4. metrics_debugging.md - Monitor improvements
```
