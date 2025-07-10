# Warp Workflows Import Mechanism

## Implementation Choice: Option B (Robust)

**Decision**: Enhanced `import_workflows.py` to dynamically load every YAML file in `.warp/workflows/` and import into Warp's SQLite database.

## Why Option B Was Chosen

Despite Option A being labeled as "simple", Option B actually required **less refactoring** and provides better long-term maintainability:

### Analysis

1. **Existing Infrastructure**: We already had 18 YAML workflow files in `.warp/workflows/` that weren't being utilized by the import mechanism.

2. **Duplicate Maintenance**: The original approach required maintaining workflows in both Python code and JSON files, creating unnecessary duplication.

3. **Simplicity**: The YAML structure is cleaner and more maintainable than hardcoded Python dictionaries.

4. **Extensibility**: Adding new workflows now only requires creating a YAML file - no code changes needed.

## Implementation Details

### Key Changes

1. **Dynamic YAML Loading**: Added `load_workflows_from_yaml()` function that:
   - Scans `.warp/workflows/` for `*.yaml` and `*.yml` files
   - Loads and parses each file using PyYAML
   - Transforms YAML structure to match Warp's expected format
   - Handles complex workflow structures (like PRP workflows with multiple commands)

2. **Enhanced Error Handling**:
   - Graceful handling of malformed YAML files
   - Clear error messages for debugging
   - Continues processing even if individual files fail

3. **Improved Feedback**:
   - Shows which files are being loaded
   - Displays count of workflows found vs. imported
   - Lists available workflows after import

### YAML Structure Support

The import mechanism supports both simple and complex YAML structures:

**Simple Structure** (e.g., `stop-data-stack.yaml`):
```yaml
name: "Stop Data Stack"
command: "docker-compose down"
tags: ["docker", "infrastructure"]
description: "Stop the entire data stack"
arguments: []
```

**Complex Structure** (e.g., `api-contract-define.yaml`):
```yaml
name: "PRP: API Contract Define"
description: "Create detailed API contract specification"
tags: ["prp", "ai", "spec"]
arguments:
  - name: "feature"
    description: "Feature to define API contract for"
    default_value: "${1}"
commands:
  - name: "define_api_contract"
    command: |
      echo "Define API Contract..."
workflow:
  - define_api_contract
```

### Benefits Achieved

1. **Single Source of Truth**: All workflows are now defined in YAML files
2. **Zero Manual Curation**: No need to manually maintain JSON files
3. **Automatic Discovery**: New YAML files are automatically imported
4. **Better Organization**: Workflows are organized as individual files
5. **Version Control Friendly**: Each workflow can be tracked individually
6. **Extensible**: Easy to add new workflow types and structures

## Usage

To import workflows:

```bash
cd .warp
python import_workflows.py
```

To add a new workflow:

1. Create a new YAML file in `.warp/workflows/`
2. Follow the existing structure
3. Run the import script

## Dependencies

- Python 3.6+
- PyYAML library (`pip install pyyaml`)
- SQLite3 (built-in)

## Future Enhancements

1. **Validation**: Add YAML schema validation
2. **Categories**: Support workflow categorization
3. **Templates**: Add workflow templates for common patterns
4. **Sync**: Implement two-way sync between database and YAML files
5. **CLI**: Add command-line options for selective import/export

## Migration Notes

- The old `workflows_for_import.json` file can be removed once all workflows are confirmed working
- The hardcoded workflows in `import_workflows.py` have been replaced with dynamic loading
- All existing functionality is preserved while adding new capabilities

This implementation follows the principle of simplicity while providing a robust foundation for workflow management.
