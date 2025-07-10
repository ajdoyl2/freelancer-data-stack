# Quick Data MCP Server Integration

The Quick Data MCP server provides powerful data analysis capabilities for JSON and CSV files through the Model Context Protocol.

## Overview

This integration brings the quick-data-mcp server functionality into the freelancer-data-stack, providing:

- **Data Loading**: Load JSON/CSV datasets with automatic schema discovery
- **Data Analysis**: Segmentation, correlation analysis, distribution analysis
- **Visualization**: Create charts and dashboards from your data
- **Data Quality**: Validate and assess data quality
- **Custom Analytics**: Execute custom Python code against datasets

## Architecture

The Quick Data MCP server is integrated as:

1. **Standalone MCP Server**: Runs as a separate container (quick-data-mcp)
2. **MCP Adapter**: QuickDataAdapter provides integration with the main MCP server
3. **REST API Endpoints**: Exposed through the main MCP server at `/api/quick-data/*`

## Configuration

### Environment Variables

- `JWT_SECRET`: JWT secret for authentication (shared with other MCP servers)
- `ALLOWED_ORIGINS`: Allowed CORS origins
- `DATA_DIRECTORY`: Directory for storing datasets (default: `/data`)

### Docker Configuration

The server runs on port 9060 and is included in the `docker-compose.mcp.yml` file:

```yaml
quick-data-mcp:
  build:
    context: ./mcp-servers/quick-data-mcp
    dockerfile: Dockerfile
  container_name: quick-data-mcp
  environment:
    - JWT_SECRET=${JWT_SECRET}
    - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    - DATA_DIRECTORY=/data
  ports:
    - "9060:8000"
  volumes:
    - ./volumes/quick-data:/data
  networks:
    - data-stack
```

## API Endpoints

### Main MCP Server Endpoints

- `POST /api/quick-data/load-dataset` - Load a dataset
- `GET /api/quick-data/datasets` - List loaded datasets

### Quick Data MCP Direct Endpoints

- `POST /tools/load_dataset` - Load dataset
- `GET /tools/list_loaded_datasets` - List datasets
- `POST /tools/segment_by_column` - Segment data
- `POST /tools/find_correlations` - Find correlations
- `POST /tools/create_chart` - Create visualization
- `POST /tools/analyze_distributions` - Analyze distributions
- `POST /tools/detect_outliers` - Detect outliers
- `POST /tools/validate_data_quality` - Validate data quality
- `POST /tools/suggest_analysis` - Get AI-powered suggestions
- `POST /tools/execute_custom_analytics_code` - Run custom Python code

### Resource Endpoints

- `GET /resources/datasets/{dataset_name}/summary` - Dataset summary
- `GET /resources/datasets/{dataset_name}/schema` - Dataset schema
- `GET /resources/datasets/{dataset_name}/sample` - Sample rows

## Usage Examples

### Loading a Dataset

```python
import aiohttp

async def load_sales_data():
    async with aiohttp.ClientSession() as session:
        data = {
            "file_path": "/data/sales_2024.csv",
            "dataset_name": "sales_2024",
            "sample_size": 10000
        }
        async with session.post("http://localhost:8080/api/quick-data/load-dataset", json=data) as resp:
            result = await resp.json()
            print(f"Dataset loaded: {result}")
```

### Finding Correlations

```python
async def analyze_correlations():
    async with aiohttp.ClientSession() as session:
        data = {
            "dataset_name": "sales_2024",
            "threshold": 0.5
        }
        async with session.post("http://localhost:9060/tools/find_correlations", json=data) as resp:
            correlations = await resp.json()
            print(f"Strong correlations: {correlations}")
```

### Creating a Chart

```python
async def create_sales_chart():
    async with aiohttp.ClientSession() as session:
        data = {
            "dataset_name": "sales_2024",
            "chart_type": "bar",
            "x_column": "month",
            "y_column": "revenue",
            "title": "Monthly Revenue 2024"
        }
        async with session.post("http://localhost:9060/tools/create_chart", json=data) as resp:
            chart = await resp.json()
            print(f"Chart created: {chart}")
```

### Custom Analytics

```python
async def run_custom_analysis():
    async with aiohttp.ClientSession() as session:
        code = """
# Calculate monthly growth rates
monthly_revenue = df.groupby('month')['revenue'].sum()
growth_rates = monthly_revenue.pct_change() * 100

print("Monthly Revenue Growth Rates:")
print(growth_rates.round(2))

# Find top products
top_products = df.groupby('product')['revenue'].sum().nlargest(5)
print("\\nTop 5 Products by Revenue:")
print(top_products)
"""
        data = {
            "dataset_name": "sales_2024",
            "python_code": code
        }
        async with session.post("http://localhost:9060/tools/execute_custom_analytics_code", json=data) as resp:
            output = await resp.text()
            print(f"Analysis output:\n{output}")
```

## Testing

Run the integration tests:

```bash
cd mcp-server/tests
python test_quick_data_integration.py
```

## Deployment

1. Build and start the Quick Data MCP server:
   ```bash
   docker-compose -f docker-compose.mcp.yml up quick-data-mcp
   ```

2. Verify the server is running:
   ```bash
   curl http://localhost:9060/health
   ```

3. Test through the main MCP server:
   ```bash
   curl http://localhost:8080/api/quick-data/datasets
   ```

## Troubleshooting

### Server not starting
- Check logs: `docker logs quick-data-mcp`
- Verify port 9060 is not in use
- Ensure JWT_SECRET is set in environment

### Dataset loading fails
- Verify file path is accessible within container
- Check file permissions in volume mount
- Ensure file format is CSV or JSON

### Connection errors
- Verify network connectivity between containers
- Check if both MCP servers are on the same Docker network
- Verify environment variables are set correctly

## Future Enhancements

1. **Additional File Formats**: Support for Parquet, Excel, etc.
2. **Streaming Analysis**: Handle large datasets with streaming
3. **ML Integration**: Add machine learning capabilities
4. **Caching**: Implement dataset caching for performance
5. **Multi-tenancy**: Support for user-specific datasets
