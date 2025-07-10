"""Custom analytics code execution tool implementation."""

import logging
import os
import sys
from pathlib import Path

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

from input_validation import InputValidationError, validator

from ..models.schemas import DatasetManager

logger = logging.getLogger(__name__)


async def execute_custom_analytics_code(dataset_name: str, python_code: str) -> str:
    """
    Execute custom Python code against a loaded dataset.

    Implementation steps:
    1. Validate inputs for security
    2. Get dataset from DatasetManager
    3. Serialize dataset to JSON for subprocess
    4. Wrap user code in execution template
    5. Execute via subprocess with uv run python -c
    6. Capture and return stdout/stderr
    """
    import asyncio

    try:
        # Step 1: Validate inputs for security
        try:
            validated_dataset_name = validator.validate_dataset_name(dataset_name)
            validated_python_code = validator.validate_python_code(python_code)
        except InputValidationError as e:
            logger.warning(f"Input validation failed: {e}")
            return f"VALIDATION ERROR: {str(e)}"

        # Step 2: Get dataset
        df = DatasetManager.get_dataset(validated_dataset_name)

        # Step 3: Serialize dataset
        dataset_json = df.to_json(orient="records")

        # Step 4: Create execution template
        # Need to properly indent user code
        import textwrap

        indented_user_code = textwrap.indent(validated_python_code, "    ")

        execution_code = f"""
import pandas as pd
import numpy as np
import plotly.express as px
import json

try:
    # Load dataset
    dataset_data = {dataset_json}
    df = pd.DataFrame(dataset_data)

    # Execute user code
{indented_user_code}

except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
    import traceback
    print("Traceback:")
    print(traceback.format_exc())
"""

        # Step 5: Execute subprocess with restricted environment
        # Create a restricted environment
        restricted_env = os.environ.copy()
        restricted_env["PYTHONPATH"] = ""  # Clear Python path

        process = await asyncio.create_subprocess_exec(
            "uv",
            "run",
            "--with",
            "pandas",
            "--with",
            "numpy",
            "--with",
            "plotly",
            "python",
            "-c",
            execution_code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=restricted_env,
        )

        # Step 6: Get output with timeout (reduced from 30 to 15 seconds)
        try:
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=15.0)
            result = stdout.decode("utf-8")

            # Log code execution for audit
            logger.info(
                f"Code executed successfully for dataset: {validated_dataset_name}"
            )

            return result
        except TimeoutError:
            process.kill()
            await process.wait()
            logger.warning(
                f"Code execution timeout for dataset: {validated_dataset_name}"
            )
            return "TIMEOUT: Code execution exceeded 15 second limit"

    except Exception as e:
        return f"EXECUTION ERROR: {type(e).__name__}: {str(e)}"
