# 🧪 Pipeline Testing & Validation Plan
## Meltano-Based Modern Data Stack

**Created**: July 2, 2025
**Stack Version**: Meltano 3.7.9 + dbt 1.10.2 + DuckDB 1.3.1
**Status**: Ready for End-to-End Testing

---

## 📋 **Overview**

This plan outlines the systematic testing approach for our newly migrated data stack, moving from Dagster+Airbyte to Meltano-only with built-in orchestration.

### **Migration Summary**
- ✅ **Dependencies**: Updated and installed successfully
- ✅ **Git Branch**: `feat/migrate-to-meltano-modernize-stack`
- ✅ **Pull Request**: [#7](https://github.com/ajdoyl2/freelancer-data-stack/pull/7)
- 🔄 **Next Phase**: End-to-end pipeline validation

---

## 🎯 **Step 2: Start Meltano Services & Basic Connectivity**

### **2.1 Environment Setup**
```bash
# Activate virtual environment
poetry shell

# Verify Meltano installation
meltano --version

# Navigate to Meltano project
cd meltano/
```

### **2.2 Initialize Meltano Project**
```bash
# Verify Meltano configuration
meltano config list

# Check installed plugins
meltano invoke tap-csv --about
meltano invoke target-duckdb --about

# Test Meltano project structure
meltano project show
```

### **2.3 Database Connectivity Test**
```bash
# Start DuckDB and verify connection
cd ../
python -c "import duckdb; conn = duckdb.connect('data/analytics.duckdb'); print('DuckDB connection: OK'); conn.close()"

# Verify sample data exists
ls -la meltano/extract/sample_data.csv
```

### **Expected Outcomes**
- ✅ Meltano commands execute without errors
- ✅ Plugins respond to `--about` queries
- ✅ DuckDB database file accessible
- ✅ Sample CSV data file present

---

## 🔄 **Step 3: Execute End-to-End Meltano Pipeline**

### **3.1 Basic ELT Pipeline Execution**
```bash
cd meltano/

# Run full ELT pipeline: Extract + Load
meltano run tap-csv target-duckdb

# Verify data loaded into DuckDB
meltano invoke duckdb --command "SELECT COUNT(*) FROM raw_customers;"
```

### **3.2 Data Quality Validation**
```bash
# Check raw data structure
meltano invoke duckdb --command "DESCRIBE raw_customers;"

# Sample data verification
meltano invoke duckdb --command "SELECT * FROM raw_customers LIMIT 5;"

# Verify record counts match source
wc -l extract/sample_data.csv
meltano invoke duckdb --command "SELECT COUNT(*) FROM raw_customers;"
```

### **3.3 dbt Transformation Pipeline**
```bash
# Navigate to dbt project
cd ../transformation/dbt/

# Install dbt packages (if any)
dbt deps

# Test source connections
dbt source freshness

# Run all transformations
dbt run

# Test data quality
dbt test

# Generate documentation
dbt docs generate
```

### **Expected Outcomes**
- ✅ CSV data successfully extracted and loaded to DuckDB
- ✅ Raw data table created with expected schema
- ✅ dbt models execute without errors
- ✅ Customer segmentation model produces results
- ✅ Data quality tests pass

---

## 🔍 **Step 4: Validation & Documentation**

### **4.1 End-to-End Data Flow Verification**
```bash
# Verify full pipeline data flow
cd ../../meltano/

# Check final transformed data
meltano invoke duckdb --command "SELECT * FROM customer_segments LIMIT 10;"

# Validate business logic
meltano invoke duckdb --command "
SELECT
    segment,
    COUNT(*) as customer_count,
    AVG(customer_value) as avg_value
FROM customer_segments
GROUP BY segment
ORDER BY avg_value DESC;
"
```

### **4.2 Pipeline Performance Metrics**
```bash
# Time the full pipeline
time meltano run tap-csv target-duckdb

# Check DuckDB database size
ls -lh ../data/analytics.duckdb

# Verify data lineage (basic)
meltano invoke duckdb --command "PRAGMA table_info(raw_customers);"
meltano invoke duckdb --command "PRAGMA table_info(customer_segments);"
```

### **4.3 Orchestration Validation**
```bash
# Test Meltano scheduling capabilities
meltano schedule list

# Create a basic schedule (for demonstration)
meltano schedule add daily-elt --job=tap-csv-to-target-duckdb --interval="@daily"

# Verify schedule configuration
meltano config meltano-schedule daily-elt
```

### **4.4 Error Handling & Recovery**
```bash
# Test pipeline resilience
# 1. Run with invalid data (intentional fail)
echo "invalid,data,format" > extract/test_bad_data.csv
meltano run tap-csv target-duckdb --config-override="files=[{entity: test_bad_data, path: extract/test_bad_data.csv}]" || echo "Expected failure: OK"

# 2. Restore and verify recovery
rm extract/test_bad_data.csv
meltano run tap-csv target-duckdb
```

### **Expected Outcomes**
- ✅ Complete data flow from CSV → DuckDB → Transformed tables
- ✅ Business logic produces sensible customer segments
- ✅ Pipeline performance within acceptable bounds
- ✅ Meltano scheduling capabilities functional
- ✅ Error handling gracefully manages failures

---

## 📊 **Success Criteria**

| Test Category | Criteria | Status |
|---------------|----------|--------|
| **Basic Setup** | Meltano commands work, plugins respond | 🔄 Pending |
| **Data Extraction** | CSV files successfully read by tap-csv | 🔄 Pending |
| **Data Loading** | Data appears in DuckDB with correct schema | 🔄 Pending |
| **Transformations** | dbt models run successfully, tests pass | 🔄 Pending |
| **Data Quality** | Customer segmentation logic produces results | 🔄 Pending |
| **Performance** | Full pipeline completes in reasonable time | 🔄 Pending |
| **Orchestration** | Meltano scheduling configured successfully | 🔄 Pending |

---

## 🚨 **Potential Issues & Troubleshooting**

### **Common Issues**
1. **Plugin Not Found**: Run `meltano install` to ensure all plugins installed
2. **DuckDB Lock**: Close any existing DuckDB connections
3. **Schema Mismatches**: Check CSV headers match expected format
4. **dbt Connection**: Verify `profiles.yml` points to correct DuckDB file

### **Debug Commands**
```bash
# Check Meltano environment
meltano config list-all

# Debug specific plugins
meltano invoke tap-csv --config
meltano invoke target-duckdb --config

# Verbose pipeline execution
meltano --log-level=debug run tap-csv target-duckdb

# dbt debug
cd transformation/dbt && dbt debug
```

---

## 🎯 **Post-Testing Actions**

### **If All Tests Pass ✅**
1. **Update README.md** with new pipeline instructions
2. **Document performance benchmarks** in `PERFORMANCE.md`
3. **Create operational runbooks** for pipeline management
4. **Plan Airflow re-integration** when compatibility allows

### **If Issues Found ❌**
1. **Document specific failures** with reproduction steps
2. **Create GitHub issues** for each problem area
3. **Prioritize fixes** based on criticality
4. **Consider rollback strategy** if major issues found

---

## 📚 **Documentation Updates Required**

1. **README.md**: Update setup and usage instructions
2. **meltano/README.md**: Create Meltano-specific documentation
3. **ARCHITECTURE.md**: Update architecture diagrams
4. **TROUBLESHOOTING.md**: Add common Meltano issues and solutions

---

**Next Command**: `poetry shell && cd meltano && meltano --version`
**Estimated Duration**: 2-3 hours for complete validation
**Prerequisites**: PR merged and dependencies installed

---

*This plan ensures systematic validation of the entire modernized data stack while documenting any issues for future resolution.*
