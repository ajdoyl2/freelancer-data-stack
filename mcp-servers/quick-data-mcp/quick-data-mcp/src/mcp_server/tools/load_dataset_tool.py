"""Dataset loading tool implementation."""

from ..models.schemas import DatasetManager, dataset_schemas, loaded_datasets


async def load_dataset(
    file_path: str, dataset_name: str, sample_size: int | None = None
) -> dict:
    """Load any JSON/CSV dataset into memory with automatic schema discovery."""
    try:
        result = DatasetManager.load_dataset(file_path, dataset_name)

        # Apply sampling if requested
        if sample_size and sample_size < result["rows"]:
            df = DatasetManager.get_dataset(dataset_name)
            sampled_df = df.sample(n=sample_size, random_state=42)
            loaded_datasets[dataset_name] = sampled_df

            # Update schema for sampled data
            schema = dataset_schemas[dataset_name]
            schema.row_count = len(sampled_df)

            result["rows"] = len(sampled_df)
            result["sampled"] = True
            result["original_rows"] = len(df)

        return result

    except Exception as e:
        return {"status": "error", "message": f"Failed to load dataset: {str(e)}"}
