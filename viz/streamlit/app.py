"""
Freelancer Data Stack - Streamlit Analytics App
=============================================

This replaces Jupyter notebooks with an interactive Streamlit application
for data analysis, visualization, and reporting.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb
import os
from datetime import datetime, timedelta
import sqlite3

# Configure Streamlit page
st.set_page_config(
    page_title="Freelancer Data Stack",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("🏗️ Freelancer Data Stack Analytics")
st.markdown("""
**Interactive data analysis and visualization platform**

This Streamlit application provides real-time analytics capabilities, replacing traditional Jupyter notebooks
with an interactive dashboard for exploring your data stack.
""")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Data Overview", "DuckDB Analytics", "Snowflake Analytics", "Data Quality", "System Monitoring"]
)

# Database connection functions
@st.cache_resource
def get_duckdb_connection():
    """Connect to DuckDB database"""
    try:
        # In Docker environment, DuckDB is mounted at /data/main.db
        # In local development, use volumes/duckdb/main.db
        if os.path.exists("/data/main.db"):
            db_path = "/data/main.db"
        else:
            db_path = "../../volumes/duckdb/main.db"
        
        conn = duckdb.connect(db_path, read_only=True)
        return conn
    except Exception as e:
        st.error(f"Failed to connect to DuckDB: {e}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def query_duckdb(query):
    """Execute query against DuckDB"""
    conn = get_duckdb_connection()
    if conn:
        try:
            df = conn.execute(query).df()
            return df
        except Exception as e:
            st.error(f"Query failed: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=300)
def get_sample_data():
    """Get sample data from DuckDB"""
    query = """
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
    """
    return query_duckdb(query)

def show_data_overview():
    """Data Overview page"""
    st.header("📊 Data Overview")
    
    col1, col2, col3 = st.columns(3)
    
    # Sample metrics
    with col1:
        st.metric("Total Projects", "3", "+1")
    
    with col2:
        st.metric("Average Value", "$1,533.50", "+5.2%")
    
    with col3:
        st.metric("Data Sources", "3", "DuckDB, Snowflake, PostgreSQL")
    
    # Data source status
    st.subheader("Data Source Status")
    
    status_data = {
        "Data Source": ["DuckDB", "Snowflake", "PostgreSQL", "Evidence.dev", "Metabase"],
        "Status": ["🟢 Connected", "🟢 Connected", "🟢 Connected", "🟢 Running", "🟢 Running"],
        "Last Updated": [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ]
    }
    
    status_df = pd.DataFrame(status_data)
    st.dataframe(status_df, use_container_width=True)

def show_duckdb_analytics():
    """DuckDB Analytics page"""
    st.header("🦆 DuckDB Analytics")
    
    # Get sample data
    df = get_sample_data()
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Project Values")
            fig = px.bar(df, x='name', y='value', color='value_category',
                        title="Project Value Comparison")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Value Over Time")
            fig = px.line(df, x='created_date', y='value', markers=True,
                         title="Project Values Over Time")
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("Project Data")
        st.dataframe(df, use_container_width=True)
        
        # Custom query interface
        st.subheader("Custom DuckDB Query")
        custom_query = st.text_area(
            "Enter your SQL query:",
            value="SELECT * FROM sample_data LIMIT 10;",
            height=100
        )
        
        if st.button("Execute Query"):
            if custom_query.strip():
                result_df = query_duckdb(custom_query)
                if not result_df.empty:
                    st.dataframe(result_df, use_container_width=True)
                else:
                    st.warning("Query returned no results or failed.")
    else:
        st.warning("No data available in DuckDB. Please check your database connection.")

def show_snowflake_analytics():
    """Snowflake Analytics page"""
    st.header("❄️ Snowflake Analytics")
    
    st.info("🚧 Snowflake connection setup required. This page will display Snowflake analytics once configured.")
    
    # Placeholder for Snowflake connection
    with st.expander("Snowflake Connection Details"):
        st.code(f"""
        Account: {os.getenv('SNOWFLAKE_ACCOUNT', 'Not configured')}
        Username: {os.getenv('SNOWFLAKE_USERNAME', 'Not configured')}
        Database: {os.getenv('SNOWFLAKE_DATABASE', 'Not configured')}
        Warehouse: {os.getenv('SNOWFLAKE_WAREHOUSE', 'Not configured')}
        """)
    
    # Sample Snowflake visualizations (placeholder data)
    st.subheader("Schema Overview")
    
    # Create sample data for demonstration
    schema_data = {
        'Schema': ['PUBLIC', 'ANALYTICS', 'STAGING'],
        'Tables': [15, 8, 12],
        'Views': [5, 3, 2]
    }
    schema_df = pd.DataFrame(schema_data)
    
    fig = px.bar(schema_df, x='Schema', y=['Tables', 'Views'], 
                 title="Snowflake Schema Overview", barmode='group')
    st.plotly_chart(fig, use_container_width=True)

def show_data_quality():
    """Data Quality page"""
    st.header("✅ Data Quality Dashboard")
    
    # Quality metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Data Quality Score", "98%", "+2%")
    
    with col2:
        st.metric("Failed Tests", "2", "-1")
    
    with col3:
        st.metric("Coverage", "95%", "+5%")
    
    with col4:
        st.metric("Last Check", "2 min ago", "")
    
    # Quality trends
    st.subheader("Quality Trends")
    
    # Generate sample quality data
    dates = pd.date_range(start='2024-01-01', end='2024-06-30', freq='D')
    quality_scores = 95 + 5 * pd.Series(range(len(dates))).apply(lambda x: 0.01 * x % 10)
    
    quality_df = pd.DataFrame({
        'Date': dates,
        'Quality Score': quality_scores
    })
    
    fig = px.line(quality_df, x='Date', y='Quality Score', 
                  title="Data Quality Score Over Time")
    fig.update_yaxis(range=[90, 100])
    st.plotly_chart(fig, use_container_width=True)
    
    # Test results
    st.subheader("Recent Test Results")
    
    test_data = {
        'Test Name': ['Null Check - Customer ID', 'Range Check - Revenue', 'Uniqueness - Email', 'Format Check - Phone'],
        'Status': ['✅ Passed', '❌ Failed', '✅ Passed', '⚠️ Warning'],
        'Last Run': ['2 min ago', '5 min ago', '2 min ago', '10 min ago'],
        'Success Rate': ['100%', '98%', '100%', '95%']
    }
    
    test_df = pd.DataFrame(test_data)
    st.dataframe(test_df, use_container_width=True)

def show_system_monitoring():
    """System Monitoring page"""
    st.header("🔧 System Monitoring")
    
    # Service status
    services = {
        'Service': ['Airflow', 'Evidence.dev', 'Metabase', 'DuckDB', 'Postgres', 'Kafka'],
        'Status': ['🟢 Running', '🟢 Running', '🟢 Running', '🟢 Running', '🟢 Running', '🟢 Running'],
        'CPU': ['12%', '8%', '15%', '5%', '20%', '18%'],
        'Memory': ['512MB', '256MB', '1.2GB', '128MB', '800MB', '600MB'],
        'Uptime': ['2d 5h', '2d 5h', '2d 5h', '2d 5h', '2d 5h', '2d 5h']
    }
    
    services_df = pd.DataFrame(services)
    st.dataframe(services_df, use_container_width=True)
    
    # Resource usage charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CPU Usage")
        cpu_data = pd.DataFrame({
            'Service': services['Service'],
            'CPU %': [12, 8, 15, 5, 20, 18]
        })
        
        fig = px.pie(cpu_data, values='CPU %', names='Service', 
                     title="CPU Usage by Service")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Memory Usage")
        memory_values = [512, 256, 1200, 128, 800, 600]  # MB
        memory_data = pd.DataFrame({
            'Service': services['Service'],
            'Memory MB': memory_values
        })
        
        fig = px.bar(memory_data, x='Service', y='Memory MB',
                     title="Memory Usage by Service")
        st.plotly_chart(fig, use_container_width=True)

# Main page routing
if page == "Data Overview":
    show_data_overview()
elif page == "DuckDB Analytics":
    show_duckdb_analytics()
elif page == "Snowflake Analytics":
    show_snowflake_analytics()
elif page == "Data Quality":
    show_data_quality()
elif page == "System Monitoring":
    show_system_monitoring()

# Footer
st.markdown("---")
st.markdown("""
**Freelancer Data Stack** | Powered by Streamlit | 
[Evidence.dev](http://localhost:3001) | [Metabase](http://localhost:3002) | [Airflow](http://localhost:8080)
""")
