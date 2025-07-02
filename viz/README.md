# Visualization Layer Configuration

This directory contains the complete configuration for the visualization layer of the Freelancer Data Stack.

## ✅ Configuration Complete

### 🦆 Evidence.dev
**Status: Configured for DuckDB and Snowflake**

- **DuckDB Connection**: Pointing to `/data/main.db` with sample project data
- **Snowflake Connection**: Configured with your credentials via environment variables
- **Dashboard Pages**:
  - `duckdb-sample.md` - Sample DuckDB analytics dashboard
  - `snowflake-analytics.md` - Snowflake analytics dashboard
  - `data-quality.md` - Data quality monitoring dashboard
- **Access**: http://localhost:3001
- **Volume Mounts**:
  - `./viz/evidence:/app` (Evidence pages and configuration)
  - `${HOME}/data-stack/volumes/duckdb:/data` (DuckDB access)

### 📊 Metabase
**Status: Configured with environment variable loading**

- **PostgreSQL Connection**: For application metadata
- **DuckDB Connection**: Via SQLite driver to local DuckDB file
- **Snowflake Connection**: Configured with environment variables
- **Data Sources Configuration**: `data-sources.json` with connection templates
- **Access**: http://localhost:3002
- **Volume Mounts**:
  - `${HOME}/data-stack/volumes/metabase:/metabase-data` (Metabase data)
  - `./viz/metabase:/metabase-config` (Configuration files)
  - `${HOME}/data-stack/volumes/duckdb:/metabase-data/duckdb` (DuckDB access)

### 🐍 Streamlit (Jupyter Upgrade)
**Status: Complete replacement for Jupyter notebooks**

- **Main Application**: `viz/streamlit/app.py`
- **Features**:
  - Data Overview dashboard
  - DuckDB Analytics with custom query interface
  - Snowflake Analytics (placeholder configured)
  - Data Quality monitoring
  - System monitoring
- **Access**: http://localhost:8501
- **Run Commands**:
  ```bash
  # Original command (backward compatibility)
  streamlit run notebooks/app.py

  # Direct command
  streamlit run viz/streamlit/app.py

  # Using helper script
  ./viz/streamlit/run.sh
  ```

## 🔗 Data Connections

### DuckDB
- **File**: `volumes/duckdb/main.db`
- **Sample Data**: Created with project data (3 sample projects)
- **Connected Services**: Evidence.dev, Metabase, Streamlit

### Snowflake
- **Account**: LKEKQHS-RH36152
- **Database**: ANALYTICS
- **Warehouse**: COMPUTE_WH
- **Connected Services**: Evidence.dev, Metabase, Streamlit
- **Credentials**: Stored in environment variables

### PostgreSQL
- **Purpose**: Application metadata storage
- **Database**: data_stack
- **Connected Services**: Metabase, Airflow

## 🚀 Quick Start

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **Access visualization tools**:
   - Evidence.dev: http://localhost:3001
   - Metabase: http://localhost:3002
   - Streamlit: http://localhost:8501
   - Jupyter (legacy): http://localhost:8888

3. **Run Streamlit locally**:
   ```bash
   streamlit run notebooks/app.py
   # or
   ./viz/streamlit/run.sh
   ```

## 📁 Directory Structure

```
viz/
├── evidence/
│   ├── evidence.settings.json      # Multi-database configuration
│   └── pages/
│       ├── duckdb-sample.md        # DuckDB dashboard
│       ├── snowflake-analytics.md  # Snowflake dashboard
│       └── data-quality.md         # Data quality dashboard
├── metabase/
│   └── data-sources.json           # Database connection templates
├── streamlit/
│   ├── app.py                      # Main Streamlit application
│   ├── requirements.txt            # Python dependencies
│   └── run.sh                      # Run script
└── README.md                       # This file
```

## 🔧 Environment Variables

All database credentials are loaded from `.env` file:
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USERNAME`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_ROLE`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`
- `POSTGRES_PASSWORD`
- `JUPYTER_TOKEN`

## 🎯 Next Steps

1. **Customize Evidence.dev dashboards** with your actual data queries
2. **Set up Metabase dashboards** using the configured data sources
3. **Extend Streamlit app** with additional analytics pages
4. **Add real Snowflake tables** to replace placeholder queries
5. **Configure data quality checks** with actual validation rules

---

**✨ Visualization layer configuration complete!**
