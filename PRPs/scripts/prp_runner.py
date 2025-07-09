#!/usr/bin/env -S uv run --script
"""Run an AI coding agent against a PRP.

KISS version - no repo-specific assumptions.

Typical usage:
    uv run RUNNERS/claude_runner.py --prp test --interactive
    uv run RUNNERS/claude_runner.py --prp test --output-format json
    uv run RUNNERS/claude_runner.py --prp test --output-format stream-json

Arguments:
    --prp-path       Path to a PRP markdown file (overrides --prp)
    --prp            Feature key; resolves to PRPs/{feature}.md
    --model          CLI executable for the LLM (default: "claude") Only Claude Code is supported for now
    --interactive    Pass through to run the model in chat mode; otherwise headless.
    --output-format  Output format for headless mode: text, json, stream-json (default: text)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

ROOT = (
    Path(__file__).resolve().parent.parent
)  # freelancer-data-stack root  # project root

META_HEADER = """Enhanced Data Stack PRP Runner

Data Stack Project-Specific Instructions:
- Use venv_linux for ALL Python commands
- Follow 500-line file limit rule
- Use UV for dependency management
- Integrate with existing agent patterns (agent.py, tools.py, prompts.py)
- Target $50/month operational cost
- Maintain 0.85 quality threshold
- Preserve DuckDB/Meltano/dbt/Airflow integration patterns

Ingest and understand the Product Requirement Prompt (PRP) below in detail.

    # DATA STACK WORKFLOW GUIDANCE:

    ## Planning Phase (Data Stack Specific)
    - **Read PLANNING.md and CLAUDE.md** for project context and patterns
    - **Check TASK.md** before starting - add task if not listed
    - Think hard before you code. Create comprehensive plan addressing requirements.
    - Use TodoWrite tool to create and track implementation plan.
    - Search for existing data stack patterns in agents/, tools/, data_stack/
    - Consider cost optimization and performance impact (~$50/month target)
    - Identify integration points with Meltano, dbt, Airflow, DuckDB

    ## Implementation Phase (Data Stack Specific)
    - **Use venv_linux** for all Python command execution
    - **Follow agent structure**: agent.py (logic), tools.py (functions), prompts.py (system prompts)
    - **Respect 500-line limit** - refactor by splitting into modules if needed
    - Follow existing patterns in data_stack/ directory
    - Use UV for dependency management
    - Integrate with existing DuckDB, Meltano, dbt, Airflow patterns
    - Consider cost optimization for data processing (~90% cost reduction patterns)
    - Use type hints and pydantic for data validation
    - Follow PEP8 and format with black

    ## Testing Phase (Data Stack Specific)
    - **Create pytest unit tests** for all new functions/classes
    - Test data pipeline integration (extract, transform, load)
    - Validate agent patterns and tool integration
    - Test cost optimization and performance metrics
    - Verify Docker Compose service integration
    - Run validation gates: syntax, unit, integration, creative
    - Ensure all requirements satisfied before marking complete

    ## Data Stack Validation Gates:

    ### Level 1: Syntax & Style (Data Stack)
    ```bash
    # CRITICAL: Use venv_linux for ALL Python commands
    source venv_linux/bin/activate
    ruff check scripts/ --fix
    ruff check agents/ --fix
    ruff check tools/ --fix
    mypy scripts/ agents/ tools/
    black scripts/ agents/ tools/
    markdownlint PRPs/templates/*.md PRPs/ai_docs/*.md
    ```

    ### Level 2: Unit Testing (Data Stack)
    ```bash
    # Test new functionality with existing patterns
    uv run pytest tests/test_*.py -v
    uv run pytest tests/test_data_stack_workflows.py -v
    uv run pytest tests/test_agents.py -v
    uv run pytest tests/test_tools.py -v
    ```

    ### Level 3: Integration Testing (Data Stack)
    ```bash
    # Test complete data stack integration
    docker-compose up -d duckdb meltano streamlit

    # Test data pipeline functionality
    cd data_stack/meltano && meltano --environment=dev elt tap-csv target-duckdb
    cd ../dbt && dbt run --profiles-dir . && dbt test --profiles-dir .

    # Test monitoring and dashboards
    curl -f http://localhost:8501/health || echo "Streamlit dashboard check"
    curl -f http://localhost:3000/api/health || echo "Grafana monitoring check"
    curl -f http://localhost:8080/api/v1/health || echo "Airflow orchestration check"
    ```

    ### Level 4: Creative Validation (Data Stack)
    ```bash
    # Test AI agent functionality
    python -c "
    from agents.data_stack_engineer import DataStackEngineer
    from agents.base_agent import WorkflowRequest
    agent = DataStackEngineer()
    result = agent.execute_task(WorkflowRequest(user_prompt='Test task'))
    print('AI agent system functional')
    "

    # Test cost optimization
    python -c "
    from tools.cost_optimizer import CostOptimizer
    optimizer = CostOptimizer()
    print(f'Monthly cost estimate: ${optimizer.calculate_monthly_cost()}')
    "

    # Test end-to-end data pipeline
    python scripts/test_full_pipeline.py --validate-cost-optimization
    ```

    ## Example Data Stack Implementation Approach:
    1. **Context Loading**: Read PLANNING.md, CLAUDE.md, existing agent patterns
    2. **Analysis**: Search agents/, tools/, data_stack/ for existing patterns
    3. **Research**: Web search for data stack best practices, cost optimization
    4. **Planning**: Create TodoWrite plan with data stack integration points
    5. **Implementation**: Follow agent structure, use venv_linux, respect 500-line limit
    6. **Testing**: Run all 4 validation levels, ensure cost/performance targets met
    7. **Integration**: Verify Docker Compose, monitoring, and AI agent integration

    ***When finished, move completed PRP to PRPs/completed folder and update TASK.md***
    """


def build_prompt(prp_path: Path) -> str:
    return META_HEADER + prp_path.read_text()


def stream_json_output(process: subprocess.Popen) -> Iterator[dict[str, Any]]:
    """Parse streaming JSON output line by line."""
    for line in process.stdout or []:
        line = line.strip()
        if line:
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSON line: {e}", file=sys.stderr)
                print(f"Line content: {line}", file=sys.stderr)


def handle_json_output(output: str) -> dict[str, Any]:
    """Parse the JSON output from Claude Code."""
    try:
        return json.loads(output)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output: {e}", file=sys.stderr)
        return {"error": "Failed to parse JSON output", "raw": output}


def run_model(
    prompt: str,
    model: str = "claude",
    interactive: bool = False,
    output_format: str = "text",
) -> None:
    if interactive:
        # Chat mode: feed prompt via STDIN, no -p flag so the user can continue the session.
        cmd = [
            model,
            "--allowedTools",
            "Edit,Bash,Write,MultiEdit,NotebookEdit,WebFetch,Agent,LS,Grep,Read,NotebookRead,TodoRead,TodoWrite,WebSearch,Task,Glob,mcp__ide__getDiagnostics,mcp__ide__executeCode",
        ]
        subprocess.run(cmd, input=prompt.encode(), check=True)
    else:
        # Headless: pass prompt via -p for non-interactive mode
        cmd = [
            model,
            "-p",  # This is the --print flag for non-interactive mode
            prompt,
            "--allowedTools",
            "Edit,Bash,Write,MultiEdit,NotebookEdit,WebFetch,Agent,LS,Grep,Read,NotebookRead,TodoRead,TodoWrite,WebSearch,Task,Glob,mcp__ide__getDiagnostics,mcp__ide__executeCode",
            # "--max-turns",
            # "30",  # Safety limit for headless mode uncomment if needed
            "--output-format",
            output_format,
        ]

        if output_format == "stream-json":
            # Handle streaming JSON output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
            )

            try:
                for message in stream_json_output(process):
                    # Process each message as it arrives
                    if (
                        message.get("type") == "system"
                        and message.get("subtype") == "init"
                    ):
                        print(
                            f"Session started: {message.get('session_id')}",
                            file=sys.stderr,
                        )
                    elif message.get("type") == "assistant":
                        print(
                            f"Assistant: {message.get('message', {}).get('content', '')[:100]}...",
                            file=sys.stderr,
                        )
                    elif message.get("type") == "result":
                        print("\nFinal result:", file=sys.stderr)
                        print(
                            f"  Success: {message.get('subtype') == 'success'}",
                            file=sys.stderr,
                        )
                        print(
                            f"  Cost: ${message.get('cost_usd', 0):.4f}",
                            file=sys.stderr,
                        )
                        print(
                            f"  Duration: {message.get('duration_ms', 0)}ms",
                            file=sys.stderr,
                        )
                        print(
                            f"  Turns: {message.get('num_turns', 0)}", file=sys.stderr
                        )
                        if message.get("result"):
                            print(
                                f"\nResult text:\n{message.get('result')}",
                                file=sys.stderr,
                            )

                    # Print the full message for downstream processing
                    print(json.dumps(message))

                # Wait for process to complete
                process.wait()
                if process.returncode != 0:
                    stderr = process.stderr.read() if process.stderr else ""
                    print(
                        f"Claude Code failed with exit code {process.returncode}",
                        file=sys.stderr,
                    )
                    print(f"Error: {stderr}", file=sys.stderr)
                    sys.exit(process.returncode)

            except KeyboardInterrupt:
                process.terminate()
                print("\nInterrupted by user", file=sys.stderr)
                sys.exit(1)

        elif output_format == "json":
            # Handle complete JSON output
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(
                    f"Claude Code failed with exit code {result.returncode}",
                    file=sys.stderr,
                )
                print(f"Error: {result.stderr}", file=sys.stderr)
                sys.exit(result.returncode)

            # Parse and pretty print the JSON
            json_data = handle_json_output(result.stdout)
            print(json.dumps(json_data, indent=2))

            # Print summary to stderr for user visibility
            if isinstance(json_data, dict):
                if json_data.get("type") == "result":
                    print("\nSummary:", file=sys.stderr)
                    print(
                        f"  Success: {not json_data.get('is_error', False)}",
                        file=sys.stderr,
                    )
                    print(
                        f"  Cost: ${json_data.get('cost_usd', 0):.4f}", file=sys.stderr
                    )
                    print(
                        f"  Duration: {json_data.get('duration_ms', 0)}ms",
                        file=sys.stderr,
                    )
                    print(
                        f"  Session: {json_data.get('session_id', 'unknown')}",
                        file=sys.stderr,
                    )

        else:
            # Default text output
            subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a PRP with an LLM agent.")
    parser.add_argument(
        "--prp-path", help="Relative path to PRP file eg: PRPs/feature.md"
    )
    parser.add_argument(
        "--prp", help="The file name of the PRP without the .md extension eg: feature"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Launch interactive chat session"
    )
    parser.add_argument("--model", default="claude", help="Model CLI executable name")
    parser.add_argument(
        "--output-format",
        choices=["text", "json", "stream-json"],
        default="text",
        help="Output format for headless mode (default: text)",
    )
    args = parser.parse_args()

    if not args.prp_path and not args.prp:
        sys.exit("Must supply --prp or --prp-path")

    prp_path = Path(args.prp_path) if args.prp_path else ROOT / f"PRPs/{args.prp}.md"
    if not prp_path.exists():
        sys.exit(f"PRP not found: {prp_path}")

    os.chdir(ROOT)  # ensure relative paths match PRP expectations
    prompt = build_prompt(prp_path)
    run_model(
        prompt,
        model=args.model,
        interactive=args.interactive,
        output_format=args.output_format,
    )


if __name__ == "__main__":
    main()
