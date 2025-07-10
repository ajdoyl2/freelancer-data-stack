"""
Test script for Quick Data MCP integration
"""

import asyncio

import aiohttp

BASE_URL = "http://localhost:8080"  # Main MCP server URL
QUICK_DATA_URL = "http://localhost:9060"  # Quick Data MCP server URL


async def test_quick_data_health():
    """Test Quick Data MCP server health"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{QUICK_DATA_URL}/health") as response:
            assert response.status == 200
            data = await response.json()
            print(f"Quick Data health: {data}")


async def test_load_dataset():
    """Test loading a dataset"""
    test_data = {
        "file_path": "/data/test_sales.csv",
        "dataset_name": "test_sales",
        "sample_size": 1000,
    }

    async with aiohttp.ClientSession() as session:
        # First create a test CSV file
        csv_content = """date,product,sales,quantity
2024-01-01,Widget A,1500.00,100
2024-01-02,Widget B,2300.00,150
2024-01-03,Widget A,1800.00,120
2024-01-04,Widget C,3200.00,200
2024-01-05,Widget B,2100.00,140"""

        # Write test file (would normally be done through the file system)
        print(f"Test CSV content:\n{csv_content}")

        # Load dataset through main MCP server
        async with session.post(
            f"{BASE_URL}/api/quick-data/load-dataset", json=test_data
        ) as response:
            assert response.status == 200
            data = await response.json()
            print(f"Dataset loaded: {data}")
            return data


async def test_list_datasets():
    """Test listing loaded datasets"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/quick-data/datasets") as response:
            assert response.status == 200
            data = await response.json()
            print(f"Loaded datasets: {data}")
            return data


async def test_analyze_dataset():
    """Test dataset analysis"""
    async with aiohttp.ClientSession() as session:
        # Find correlations
        correlation_data = {"dataset_name": "test_sales", "threshold": 0.3}

        async with session.post(
            f"{QUICK_DATA_URL}/tools/find_correlations", json=correlation_data
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"Correlations: {data}")

        # Analyze distribution
        distribution_data = {"dataset_name": "test_sales", "column_name": "sales"}

        async with session.post(
            f"{QUICK_DATA_URL}/tools/analyze_distributions", json=distribution_data
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"Distribution analysis: {data}")


async def test_create_chart():
    """Test chart creation"""
    chart_config = {
        "dataset_name": "test_sales",
        "chart_type": "bar",
        "x_column": "product",
        "y_column": "sales",
        "title": "Sales by Product",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{QUICK_DATA_URL}/tools/create_chart", json=chart_config
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"Chart created: {data}")


async def main():
    """Run all tests"""
    print("Testing Quick Data MCP Integration...")
    print("=" * 50)

    try:
        print("\n1. Testing Quick Data health...")
        await test_quick_data_health()

        print("\n2. Loading test dataset...")
        await test_load_dataset()

        print("\n3. Listing datasets...")
        await test_list_datasets()

        print("\n4. Analyzing dataset...")
        await test_analyze_dataset()

        print("\n5. Creating chart...")
        await test_create_chart()

        print("\n" + "=" * 50)
        print("All tests completed successfully!")

    except Exception as e:
        print(f"\nError during testing: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
