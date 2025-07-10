"""Tools package."""

# Import modules for grouped access
from . import pandas_tools
from .analyze_distributions_tool import analyze_distributions
from .calculate_feature_importance_tool import calculate_feature_importance
from .compare_datasets_tool import compare_datasets
from .create_chart_tool import create_chart
from .detect_outliers_tool import detect_outliers
from .execute_custom_analytics_code_tool import execute_custom_analytics_code
from .export_insights_tool import export_insights
from .find_correlations_tool import find_correlations
from .generate_dashboard_tool import generate_dashboard
from .list_loaded_datasets_tool import list_loaded_datasets

# Pandas tools
from .load_dataset_tool import load_dataset
from .memory_optimization_report_tool import memory_optimization_report
from .merge_datasets_tool import merge_datasets
from .segment_by_column_tool import segment_by_column
from .suggest_analysis_tool import suggest_analysis
from .time_series_analysis_tool import time_series_analysis

# Analytics tools
from .validate_data_quality_tool import validate_data_quality

__all__ = [
    # Modules
    "pandas_tools",
    # Analytics tools
    "validate_data_quality",
    "compare_datasets",
    "merge_datasets",
    "generate_dashboard",
    "export_insights",
    "calculate_feature_importance",
    "memory_optimization_report",
    "execute_custom_analytics_code",
    # Pandas tools
    "load_dataset",
    "list_loaded_datasets",
    "segment_by_column",
    "find_correlations",
    "create_chart",
    "analyze_distributions",
    "detect_outliers",
    "time_series_analysis",
    "suggest_analysis",
]
