#!/usr/bin/env python3
"""
Script to import AI agent workflows into Warp's database.
This avoids the need to manually add each workflow through the UI.

This script dynamically loads all YAML workflow files from .warp/workflows/
and imports them into Warp's SQLite database, eliminating manual JSON curation.
"""

import json
import sqlite3
from pathlib import Path

import yaml

# Warp database path
WARP_DB_PATH = (
    Path.home() / "Library/Application Support/dev.warp.Warp-Stable/warp.sqlite"
)

# Workflows directory
WORKFLOWS_DIR = Path(__file__).parent / "workflows"


def load_workflows_from_yaml():
    """Load all YAML workflow files from the workflows directory."""
    workflows = []

    if not WORKFLOWS_DIR.exists():
        print(f"⚠️  Workflows directory not found: {WORKFLOWS_DIR}")
        return workflows

    yaml_files = list(WORKFLOWS_DIR.glob("*.yaml")) + list(WORKFLOWS_DIR.glob("*.yml"))

    for yaml_file in yaml_files:
        try:
            with open(yaml_file, encoding="utf-8") as f:
                workflow_data = yaml.safe_load(f)

            # Transform YAML structure to match Warp's expected format
            warp_workflow = {
                "name": workflow_data.get("name", yaml_file.stem),
                "command": workflow_data.get("command", ""),
                "tags": workflow_data.get("tags", []),
                "description": workflow_data.get("description", ""),
                "arguments": workflow_data.get("arguments", []),
                "source_url": workflow_data.get("source_url"),
                "author": workflow_data.get("author"),
                "author_url": workflow_data.get("author_url"),
                "shells": workflow_data.get("shells", []),
                "environment_variables": workflow_data.get("environment_variables"),
            }

            # Handle complex workflow structures (like the PRP workflows)
            if "commands" in workflow_data and "workflow" in workflow_data:
                # For complex workflows, use the first command as the main command
                if workflow_data["commands"]:
                    first_command = workflow_data["commands"][0]
                    warp_workflow["command"] = first_command.get("command", "")

            workflows.append(warp_workflow)
            print(f"📄 Loaded workflow: {warp_workflow['name']} from {yaml_file.name}")

        except Exception as e:
            print(f"❌ Error loading {yaml_file.name}: {e}")
            continue

    return workflows


def workflow_exists(conn, name):
    """Check if a workflow with the given name already exists."""
    cursor = conn.execute(
        "SELECT COUNT(*) FROM workflows WHERE json_extract(data, '$.name') = ?", (name,)
    )
    return cursor.fetchone()[0] > 0


def add_workflow(conn, workflow_data):
    """Add a workflow to the Warp database."""
    workflow_json = json.dumps(workflow_data)

    if workflow_exists(conn, workflow_data["name"]):
        print(f"⚠️  Workflow '{workflow_data['name']}' already exists, skipping...")
        return False

    try:
        conn.execute("INSERT INTO workflows (data) VALUES (?)", (workflow_json,))
        print(f"✅ Added workflow: '{workflow_data['name']}'")
        return True
    except Exception as e:
        print(f"❌ Failed to add workflow '{workflow_data['name']}': {e}")
        return False


def main():
    """Main function to import workflows."""
    if not WARP_DB_PATH.exists():
        print(f"❌ Warp database not found at: {WARP_DB_PATH}")
        print("Make sure Warp is installed and has been run at least once.")
        return

    print(f"🔧 Connecting to Warp database: {WARP_DB_PATH}")
    print(f"📂 Loading workflows from: {WORKFLOWS_DIR}")

    # Load workflows dynamically from YAML files
    workflows = load_workflows_from_yaml()

    if not workflows:
        print("⚠️  No workflows found to import.")
        return

    try:
        conn = sqlite3.connect(WARP_DB_PATH)

        print(f"\n📝 Importing {len(workflows)} workflows...")

        added_count = 0
        for workflow in workflows:
            if add_workflow(conn, workflow):
                added_count += 1

        conn.commit()
        conn.close()

        print(f"\n🎉 Successfully imported {added_count} workflows!")
        print("📱 Open Warp and press Cmd+P to access your new workflows.")

        if added_count > 0:
            print("\n🎯 Available workflows:")
            for workflow in workflows[:5]:  # Show first 5
                print(f"   • {workflow['name']}")
            if len(workflows) > 5:
                print(f"   • ... and {len(workflows) - 5} more")

    except Exception as e:
        print(f"❌ Error connecting to Warp database: {e}")
        print("Make sure Warp is not running while importing workflows.")


if __name__ == "__main__":
    main()
