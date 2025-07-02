# Data Pipeline Design

**Complexity**: Advanced
**Estimated Time**: 45-90 minutes
**Dependencies**: Business requirements, data sources, technical architecture
**Related Prompts**: dagster_asset.md, dbt_model.md, data_quality_checks.md
**Tags**: data-engineering, pipeline, architecture, dagster, dbt, design

## Objective
Design a comprehensive data pipeline that ingests, transforms, and serves data while ensuring quality, performance, and maintainability within the freelancer data stack architecture.

## Context
### Project Environment
- **Data Stack**: Dagster (orchestration), dbt (transformation), DuckDB (warehouse), Streamlit (visualization)
- **Infrastructure**: Docker Compose, Poetry (dependency management), PostgreSQL, Redis
- **Development**: Python 3.11, Ruff/Black (linting), pytest (testing), GitHub Actions (CI/CD)
- **Monitoring**: DataHub (metadata), Great Expectations (data quality)

### Current Situation
You need to design a data pipeline that fits into the existing freelancer data stack. Consider the entire data lifecycle from ingestion through to consumption, ensuring integration with existing components and following best practices for scalability and maintainability.

## Instructions

### Step 1: Requirements Analysis

#### Business Requirements
1. **Data Sources**: Identify all data sources (APIs, databases, files, streams)
2. **Data Consumers**: Understand who will use the data and how
3. **Latency Requirements**: Real-time, near real-time, or batch processing needs
4. **Data Volume**: Current and projected data volumes
5. **Compliance**: Data privacy, retention, and regulatory requirements

#### Technical Constraints
1. **Infrastructure Limits**: Memory, CPU, storage, network constraints
2. **Integration Points**: Existing systems that must be integrated
3. **Performance SLAs**: Response time and throughput requirements
4. **Budget Constraints**: Cost considerations for storage and compute

### Step 2: Architecture Design

#### Data Flow Architecture
```
[Sources] → [Ingestion] → [Raw Storage] → [Transformation] → [Refined Storage] → [Consumption]
```

1. **Ingestion Layer**
   - Source system connections (Airbyte, custom APIs)
   - Data extraction patterns and frequencies
   - Error handling and retry mechanisms
   - Schema evolution handling

2. **Storage Layer**
   - Raw data storage (DuckDB staging tables)
   - Transformed data storage (DuckDB marts)
   - Metadata storage (PostgreSQL for configs)
   - Cache layer (Redis for fast access)

3. **Processing Layer**
   - Transformation logic (dbt models)
   - Data quality validation (Great Expectations)
   - Business logic implementation
   - Performance optimization strategies

4. **Orchestration Layer**
   - Pipeline scheduling (Dagster schedules)
   - Dependency management (Dagster assets)
   - Monitoring and alerting
   - Error handling and recovery

5. **Consumption Layer**
   - Analytics interfaces (Streamlit dashboards)
   - API endpoints for external consumption
   - Export mechanisms
   - Real-time access patterns

### Step 3: Component Design

#### Dagster Assets & Jobs
1. **Source Assets**
   ```python
   @asset(group_name="ingestion")
   def raw_customer_data() -> MaterializeResult:
       # Ingest from source system
   ```

2. **Transformation Assets**
   ```python
   @asset(deps=[raw_customer_data])
   def staging_customers() -> MaterializeResult:
       # dbt model execution
   ```

3. **Mart Assets**
   ```python
   @asset(deps=[staging_customers])
   def customer_analytics() -> MaterializeResult:
       # Business logic implementation
   ```

#### dbt Model Structure
```
models/
├── staging/        # Raw data cleaning
├── intermediate/   # Business logic
└── marts/         # Final analytics tables
```

#### Data Quality Framework
1. **Schema Validation**: Ensure data structure consistency
2. **Business Rules**: Validate business logic constraints
3. **Statistical Checks**: Monitor data distribution changes
4. **Referential Integrity**: Check relationships between datasets

### Step 4: Implementation Strategy

#### Phase 1: Foundation (Week 1-2)
- [ ] Set up basic Dagster assets for key data sources
- [ ] Implement core dbt staging models
- [ ] Configure basic data quality checks
- [ ] Establish monitoring and alerting

#### Phase 2: Core Functionality (Week 3-4)
- [ ] Implement full transformation pipeline
- [ ] Add comprehensive data quality framework
- [ ] Set up automated testing
- [ ] Configure production deployment

#### Phase 3: Enhancement (Week 5-6)
- [ ] Performance optimization
- [ ] Advanced monitoring and observability
- [ ] Additional data sources integration
- [ ] User training and documentation

### Step 5: Quality & Performance Considerations

#### Data Quality Strategy
```python
# Example Great Expectations suite
@asset(deps=[staging_customers])
def validate_customer_data():
    expectations = [
        "expect_column_to_exist",
        "expect_column_values_to_not_be_null",
        "expect_column_values_to_be_unique"
    ]
```

#### Performance Optimization
1. **Query Optimization**: Use appropriate indexes and query patterns
2. **Batch Processing**: Optimal batch sizes for memory usage
3. **Incremental Processing**: Only process changed data
4. **Caching Strategy**: Cache frequently accessed data

#### Monitoring Strategy
1. **Pipeline Health**: Success rates, execution times, data quality metrics
2. **Data Freshness**: Track data latency and staleness
3. **Resource Usage**: Monitor CPU, memory, and storage usage
4. **Business Metrics**: Track key business KPIs

## Expected Output

### Format
Provide a comprehensive pipeline design document with the following sections:

### Content Requirements

#### 1. Executive Summary
- Pipeline purpose and business value
- Key design decisions and rationale
- Implementation timeline and milestones
- Resource requirements and constraints

#### 2. Architecture Overview
- High-level data flow diagram
- Component interaction diagram
- Technology stack integration
- Scalability and performance considerations

#### 3. Detailed Design

##### Data Sources & Ingestion
- Source system details and connection methods
- Data extraction schedules and patterns
- Error handling and retry strategies
- Schema evolution and backward compatibility

##### Storage Design
- Data model and schema design
- Storage optimization strategies
- Backup and recovery procedures
- Data retention policies

##### Transformation Logic
- dbt model structure and dependencies
- Business rule implementation
- Data cleaning and enrichment strategies
- Performance optimization techniques

##### Quality Assurance
- Data validation framework
- Quality metrics and KPIs
- Alerting and notification strategies
- Issue resolution procedures

##### Orchestration & Scheduling
- Dagster job and asset definitions
- Scheduling strategies and dependencies
- Error handling and recovery mechanisms
- Monitoring and observability setup

#### 4. Implementation Plan
- Phase-by-phase implementation strategy
- Resource allocation and team assignments
- Risk assessment and mitigation strategies
- Testing and validation approaches

#### 5. Operations & Maintenance
- Deployment procedures
- Monitoring and alerting setup
- Troubleshooting guides
- Performance tuning strategies

## Quality Criteria

### Technical Standards
- [ ] All components integrate properly with existing data stack
- [ ] Follows dbt and Dagster best practices
- [ ] Includes comprehensive error handling
- [ ] Considers scalability and performance
- [ ] Implements proper data quality checks

### Design Completeness
- [ ] All data sources and consumers addressed
- [ ] Clear data lineage and dependencies
- [ ] Appropriate testing strategy included
- [ ] Monitoring and observability covered
- [ ] Documentation and maintenance procedures

### Business Alignment
- [ ] Meets stated business requirements
- [ ] Addresses compliance and regulatory needs
- [ ] Provides appropriate data quality assurance
- [ ] Scales to projected data volumes
- [ ] Delivers required performance characteristics

## Examples

### Input Example
```
Business Requirement:
- Ingest customer data from Salesforce API (daily)
- Transform to calculate customer lifetime value
- Serve data to Streamlit dashboard for sales team
- Data must be available by 8 AM daily
- 10,000 customers, growing 20% annually
```

### Expected Output Example
```markdown
# Customer Analytics Pipeline Design

## Executive Summary
This pipeline ingests customer data from Salesforce, calculates key metrics
including lifetime value, and serves analytics to the sales team dashboard.

## Architecture Overview
```
Salesforce API → Airbyte → DuckDB (staging) → dbt → DuckDB (marts) → Streamlit
```

## Data Flow Design

### Ingestion (Dagster Asset)
```python
@asset(group_name="salesforce_ingestion")
def raw_salesforce_customers() -> MaterializeResult:
    # Daily extraction at 6 AM via Airbyte
    return MaterializeResult(metadata={"records_processed": record_count})
```

### Transformation (dbt Models)
```sql
-- models/staging/stg_customers.sql
{{ config(materialized='table') }}

select
    id as customer_id,
    name as customer_name,
    created_date,
    total_revenue
from {{ source('salesforce', 'customers') }}
where created_date is not null
```

### Analytics (dbt Mart)
```sql
-- models/marts/customer_analytics.sql
select
    customer_id,
    customer_name,
    total_revenue,
    months_active,
    total_revenue / nullif(months_active, 0) as monthly_ltv
from {{ ref('stg_customers') }}
```

## Quality Checks
- Customer ID uniqueness validation
- Revenue value range checks
- Data freshness monitoring (< 24 hours)
- Row count stability checks (±10% tolerance)
```

## Troubleshooting

### Common Issues
- **Data source connectivity**: Implement robust retry mechanisms
- **Schema evolution**: Plan for backward compatibility
- **Performance degradation**: Monitor query execution times

### Validation Steps
1. Verify all data sources are accessible and documented
2. Ensure transformation logic is tested and validated
3. Confirm monitoring and alerting covers all critical paths
4. Validate that output meets business requirements

## Follow-up Actions

### Immediate Next Steps
- Create detailed implementation tickets
- Set up development environment
- Begin with proof-of-concept implementation
- Establish testing and validation procedures

### Related Tasks
- Use `dagster_asset.md` for asset implementation details
- Apply `dbt_model.md` for transformation development
- Reference `data_quality_checks.md` for validation framework

---

**Version**: 1.0
**Last Updated**: July 2025
**Created By**: AI Agent Team
