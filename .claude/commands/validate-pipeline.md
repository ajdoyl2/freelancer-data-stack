# Validate Data Pipeline End-to-End

Run comprehensive validation of the AI agent data stack pipeline.

## Validation Framework

1. **Level 1: Syntax & Style Validation**
   - Python code syntax validation
   - YAML configuration validation
   - Docker Compose syntax check
   - SQL query validation

2. **Level 2: Unit Testing**
   - DuckDB tools unit tests
   - Meltano tools unit tests
   - AI agent unit tests
   - Tool integration tests

3. **Level 3: Integration Testing**
   - End-to-end pipeline validation
   - Data quality validation
   - Performance benchmarking
   - Business logic validation

## Validation Tests

- **Source Data Validation**: CSV format and content quality
- **Meltano ELT Validation**: Extraction and loading processes
- **dbt Transformation Validation**: Model compilation and execution
- **Data Quality Validation**: Comprehensive quality metrics
- **Schema Compliance**: 31-column schema validation
- **Business Logic Validation**: Transaction flow consistency
- **Performance Validation**: Query execution benchmarks
- **Monitoring Validation**: System observability checks

## Commands to Execute

```bash
# Run complete validation suite
./scripts/validate_pipeline.py --verbose

# Run with custom quality threshold
./scripts/validate_pipeline.py --data-quality-threshold=0.90

# Generate detailed report
./scripts/validate_pipeline.py --output-format=json --output-file=validation_report.json

# Run specific validation level
python -m pytest tests/ -v
```

## Success Criteria

- All 10 validation tests pass
- Data quality score ≥ 85%
- Performance benchmarks met
- No critical errors or warnings
- Complete validation report generated