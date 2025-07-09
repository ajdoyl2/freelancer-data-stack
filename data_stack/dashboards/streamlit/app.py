"""
AI Agent Data Stack Dashboard

Interactive Streamlit dashboard for visualizing and analyzing data from the AI agent-driven data stack.
Provides real-time insights into transactions, data quality, and pipeline performance.
"""

import asyncio
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

try:
    from agents.base_agent import WorkflowRequest
    from agents.data_stack_engineer import DataStackEngineer
    from tools.duckdb_tools import DuckDBTools
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.stop()


# Configure Streamlit page
st.set_page_config(
    page_title="AI Agent Data Stack Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dashboard configuration
DUCKDB_PATH = "/data/duckdb/analytics.db"
REFRESH_INTERVAL = 30  # seconds


class DataDashboard:
    """Main dashboard class for the AI agent data stack."""

    def __init__(self):
        self.duckdb_tools = DuckDBTools()
        self.data_stack_engineer = DataStackEngineer()

    async def get_transaction_data(self) -> pd.DataFrame:
        """Get transaction data from DuckDB."""
        try:
            query = """
            SELECT
                transaction_id,
                transaction_date,
                transaction_name,
                amount,
                amount_abs,
                transaction_flow,
                category,
                parent_category,
                account_name,
                is_high_value,
                is_weekend,
                amount_bucket,
                processed_at
            FROM main.stg_transactions
            ORDER BY transaction_date DESC
            """

            result = await self.duckdb_tools.execute_query_to_df(query, DUCKDB_PATH)

            if result["success"]:
                return result["dataframe"]
            else:
                st.error(f"Failed to load transaction data: {result.get('error')}")
                return pd.DataFrame()

        except Exception as e:
            st.error(f"Error loading transaction data: {str(e)}")
            return pd.DataFrame()

    async def get_data_quality_metrics(self) -> dict[str, Any]:
        """Get data quality metrics."""
        try:
            result = await self.duckdb_tools.get_data_quality_metrics(
                "stg_transactions", "main", DUCKDB_PATH
            )
            return result if result["success"] else {}
        except Exception as e:
            logger.error(f"Error getting data quality metrics: {str(e)}")
            return {}

    async def get_pipeline_status(self) -> dict[str, Any]:
        """Get pipeline status from data stack engineer agent."""
        try:
            request = WorkflowRequest(
                user_prompt="Check pipeline health and status",
                agent_role="data_platform_engineer",
            )

            response = await self.data_stack_engineer.execute_task(request)
            return response.output if response.status.name == "SUCCESS" else {}
        except Exception as e:
            logger.error(f"Error getting pipeline status: {str(e)}")
            return {}

    def render_sidebar(self) -> dict[str, Any]:
        """Render sidebar with filters and controls."""
        st.sidebar.title("🤖 AI Data Stack")
        st.sidebar.markdown("---")

        # Date range filter
        st.sidebar.subheader("Date Range")
        date_range = st.sidebar.date_input(
            "Select date range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now(),
        )

        # Account filter
        st.sidebar.subheader("Filters")
        selected_accounts = st.sidebar.multiselect(
            "Accounts", options=["All"] + self.get_available_accounts(), default=["All"]
        )

        # Category filter
        selected_categories = st.sidebar.multiselect(
            "Categories",
            options=["All"] + self.get_available_categories(),
            default=["All"],
        )

        # Amount range
        amount_range = st.sidebar.slider(
            "Amount Range", min_value=0, max_value=10000, value=(0, 10000), step=100
        )

        # Auto-refresh toggle
        auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)

        # Manual refresh button
        if st.sidebar.button("🔄 Refresh Data"):
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown("### Dashboard Info")
        st.sidebar.info(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

        return {
            "date_range": date_range,
            "accounts": selected_accounts,
            "categories": selected_categories,
            "amount_range": amount_range,
            "auto_refresh": auto_refresh,
        }

    def get_available_accounts(self) -> list[str]:
        """Get available accounts from session state or default."""
        if "accounts" in st.session_state:
            return st.session_state.accounts
        return ["Checking Account", "Savings Account", "Credit Card"]

    def get_available_categories(self) -> list[str]:
        """Get available categories from session state or default."""
        if "categories" in st.session_state:
            return st.session_state.categories
        return ["Food", "Transport", "Shopping", "Bills", "Income"]

    def render_kpi_cards(self, df: pd.DataFrame, quality_metrics: dict[str, Any]):
        """Render KPI cards."""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_transactions = len(df)
            st.metric(
                label="Total Transactions",
                value=f"{total_transactions:,}",
                delta=f"+{total_transactions - len(df[df['transaction_date'] < df['transaction_date'].max()])} today",
            )

        with col2:
            total_amount = df["amount_abs"].sum() if not df.empty else 0
            st.metric(
                label="Total Volume",
                value=f"${total_amount:,.2f}",
                delta=f"${df[df['transaction_date'] >= datetime.now().date()]['amount_abs'].sum():,.2f} today",
            )

        with col3:
            avg_amount = df["amount_abs"].mean() if not df.empty else 0
            st.metric(
                label="Average Transaction",
                value=f"${avg_amount:.2f}",
                delta=(
                    f"{((avg_amount - df['amount_abs'].median()) / df['amount_abs'].median() * 100):.1f}% vs median"
                    if not df.empty
                    else "0%"
                ),
            )

        with col4:
            quality_score = quality_metrics.get("overall_score", 0) * 100
            st.metric(
                label="Data Quality Score",
                value=f"{quality_score:.1f}%",
                delta=(
                    "Excellent"
                    if quality_score >= 90
                    else "Good" if quality_score >= 75 else "Needs Attention"
                ),
            )

    def render_transaction_overview(self, df: pd.DataFrame):
        """Render transaction overview charts."""
        st.subheader("📊 Transaction Overview")

        if df.empty:
            st.warning("No transaction data available.")
            return

        col1, col2 = st.columns(2)

        with col1:
            # Daily transaction volume
            daily_data = (
                df.groupby("transaction_date")
                .agg({"amount_abs": "sum", "transaction_id": "count"})
                .reset_index()
            )

            fig = make_subplots(specs=[[{"secondary_y": True}]])

            fig.add_trace(
                go.Scatter(
                    x=daily_data["transaction_date"],
                    y=daily_data["amount_abs"],
                    name="Volume ($)",
                    line={"color": "#1f77b4"},
                ),
                secondary_y=False,
            )

            fig.add_trace(
                go.Scatter(
                    x=daily_data["transaction_date"],
                    y=daily_data["transaction_id"],
                    name="Count",
                    line={"color": "#ff7f0e"},
                ),
                secondary_y=True,
            )

            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Amount ($)", secondary_y=False)
            fig.update_yaxes(title_text="Transaction Count", secondary_y=True)
            fig.update_layout(title_text="Daily Transaction Trends", height=400)

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Transaction flow distribution
            flow_data = df["transaction_flow"].value_counts()

            fig = px.pie(
                values=flow_data.values,
                names=flow_data.index,
                title="Transaction Flow Distribution",
                color_discrete_map={
                    "INFLOW": "#2ca02c",
                    "OUTFLOW": "#d62728",
                    "NEUTRAL": "#ff7f0e",
                },
            )
            fig.update_layout(height=400)

            st.plotly_chart(fig, use_container_width=True)

    def render_category_analysis(self, df: pd.DataFrame):
        """Render category analysis."""
        st.subheader("🏷️ Category Analysis")

        if df.empty:
            st.warning("No transaction data available.")
            return

        col1, col2 = st.columns(2)

        with col1:
            # Top categories by amount
            category_amounts = (
                df.groupby("category")["amount_abs"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            fig = px.bar(
                x=category_amounts.values,
                y=category_amounts.index,
                orientation="h",
                title="Top Categories by Amount",
                labels={"x": "Total Amount ($)", "y": "Category"},
            )
            fig.update_layout(height=400)

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Category transaction counts
            category_counts = df["category"].value_counts().head(10)

            fig = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title="Transaction Count by Category",
                labels={"x": "Category", "y": "Transaction Count"},
            )
            fig.update_xaxes(tickangle=45)
            fig.update_layout(height=400)

            st.plotly_chart(fig, use_container_width=True)

    def render_data_quality_dashboard(self, quality_metrics: dict[str, Any]):
        """Render data quality dashboard."""
        st.subheader("✅ Data Quality Dashboard")

        if not quality_metrics:
            st.warning("No data quality metrics available.")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            # Quality scores
            scores = {
                "Overall": quality_metrics.get("overall_score", 0),
                "Completeness": quality_metrics.get("completeness_score", 0),
                "Uniqueness": quality_metrics.get("uniqueness_score", 0),
                "Consistency": quality_metrics.get("consistency_score", 0),
                "Freshness": quality_metrics.get("freshness_score", 0),
            }

            fig = go.Figure(
                data=go.Scatterpolar(
                    r=list(scores.values()),
                    theta=list(scores.keys()),
                    fill="toself",
                    name="Data Quality Scores",
                )
            )

            fig.update_layout(
                polar={"radialaxis": {"visible": True, "range": [0, 1]}},
                showlegend=False,
                title="Data Quality Radar",
                height=300,
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Null percentages
            null_percentages = quality_metrics.get("null_percentages", {})

            if null_percentages:
                fig = px.bar(
                    x=list(null_percentages.keys()),
                    y=list(null_percentages.values()),
                    title="Null Percentages by Column",
                    labels={"x": "Column", "y": "Null Percentage (%)"},
                )
                fig.update_xaxes(tickangle=45)
                fig.update_layout(height=300)

                st.plotly_chart(fig, use_container_width=True)

        with col3:
            # Quality metrics summary
            st.markdown("**Quality Metrics Summary**")

            total_rows = quality_metrics.get("total_rows", 0)
            duplicate_count = quality_metrics.get("duplicate_count", 0)

            st.metric("Total Rows", f"{total_rows:,}")
            st.metric("Duplicate Rows", f"{duplicate_count:,}")
            st.metric(
                "Duplicate %", f"{quality_metrics.get('duplicate_percentage', 0):.2f}%"
            )

    def render_pipeline_status(self, pipeline_status: dict[str, Any]):
        """Render pipeline status dashboard."""
        st.subheader("🔧 Pipeline Status")

        if not pipeline_status:
            st.warning("Pipeline status information not available.")
            return

        # Pipeline health indicator
        health_status = pipeline_status.get("overall_health", False)

        if health_status:
            st.success("✅ Pipeline is healthy and running normally")
        else:
            st.error("❌ Pipeline issues detected")

        # Recent pipeline runs (placeholder)
        st.markdown("**Recent Pipeline Runs**")

        # Create sample pipeline run data
        pipeline_runs = [
            {
                "Run ID": "run_001",
                "Status": "Success",
                "Duration": "5m 32s",
                "Timestamp": datetime.now() - timedelta(hours=1),
            },
            {
                "Run ID": "run_002",
                "Status": "Success",
                "Duration": "4m 18s",
                "Timestamp": datetime.now() - timedelta(hours=4),
            },
            {
                "Run ID": "run_003",
                "Status": "Failed",
                "Duration": "2m 45s",
                "Timestamp": datetime.now() - timedelta(hours=8),
            },
        ]

        runs_df = pd.DataFrame(pipeline_runs)
        st.dataframe(runs_df, use_container_width=True)

    def render_transaction_table(self, df: pd.DataFrame):
        """Render detailed transaction table."""
        st.subheader("📋 Transaction Details")

        if df.empty:
            st.warning("No transaction data available.")
            return

        # Add search and filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            search_term = st.text_input(
                "Search transactions", placeholder="Enter transaction name..."
            )

        with col2:
            flow_filter = st.selectbox(
                "Transaction Flow", ["All", "INFLOW", "OUTFLOW", "NEUTRAL"]
            )

        with col3:
            high_value_only = st.checkbox("High value transactions only")

        # Apply filters
        filtered_df = df.copy()

        if search_term:
            filtered_df = filtered_df[
                filtered_df["transaction_name"].str.contains(
                    search_term, case=False, na=False
                )
            ]

        if flow_filter != "All":
            filtered_df = filtered_df[filtered_df["transaction_flow"] == flow_filter]

        if high_value_only:
            filtered_df = filtered_df[filtered_df["is_high_value"]]

        # Display table
        display_columns = [
            "transaction_date",
            "transaction_name",
            "amount",
            "transaction_flow",
            "category",
            "account_name",
            "is_high_value",
        ]

        st.dataframe(
            filtered_df[display_columns].head(100), use_container_width=True, height=400
        )

        # Export options
        if st.button("📥 Export to CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )


@st.cache_data(ttl=30)
def load_dashboard_data():
    """Load and cache dashboard data."""
    dashboard = DataDashboard()

    # Run async functions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        df = loop.run_until_complete(dashboard.get_transaction_data())
        quality_metrics = loop.run_until_complete(dashboard.get_data_quality_metrics())
        pipeline_status = loop.run_until_complete(dashboard.get_pipeline_status())

        return df, quality_metrics, pipeline_status
    finally:
        loop.close()


def main():
    """Main dashboard application."""
    st.title("🤖 AI Agent Data Stack Dashboard")
    st.markdown("Real-time insights into your AI-driven data pipeline")

    # Initialize dashboard
    dashboard = DataDashboard()

    # Render sidebar
    filters = dashboard.render_sidebar()

    # Load data
    with st.spinner("Loading dashboard data..."):
        df, quality_metrics, pipeline_status = load_dashboard_data()

    # Store accounts and categories in session state
    if not df.empty:
        st.session_state.accounts = sorted(df["account_name"].unique().tolist())
        st.session_state.categories = sorted(df["category"].unique().tolist())

    # Apply filters to data
    if not df.empty and len(filters["date_range"]) == 2:
        start_date, end_date = filters["date_range"]
        df = df[
            (df["transaction_date"] >= pd.Timestamp(start_date))
            & (df["transaction_date"] <= pd.Timestamp(end_date))
        ]

        if "All" not in filters["accounts"]:
            df = df[df["account_name"].isin(filters["accounts"])]

        if "All" not in filters["categories"]:
            df = df[df["category"].isin(filters["categories"])]

        df = df[
            (df["amount_abs"] >= filters["amount_range"][0])
            & (df["amount_abs"] <= filters["amount_range"][1])
        ]

    # Render dashboard sections
    dashboard.render_kpi_cards(df, quality_metrics)

    st.markdown("---")
    dashboard.render_transaction_overview(df)

    st.markdown("---")
    dashboard.render_category_analysis(df)

    st.markdown("---")
    dashboard.render_data_quality_dashboard(quality_metrics)

    st.markdown("---")
    dashboard.render_pipeline_status(pipeline_status)

    st.markdown("---")
    dashboard.render_transaction_table(df)

    # Auto-refresh functionality
    if filters["auto_refresh"]:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()


if __name__ == "__main__":
    main()
