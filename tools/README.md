# 🔍 Rule of Three Duplicate Code Checker

A sophisticated duplicate code detection tool that implements the "Rule of Three" principle - when similar code appears three times, it should be refactored into a reusable component.

## 🎯 Features

### Core Detection Capabilities
- **AST-Based Analysis**: Uses Python's Abstract Syntax Tree for structural similarity detection
- **Multiple Fragment Types**: Detects duplicate functions, classes, and statement blocks
- **Configurable Thresholds**: Adjustable similarity levels and minimum code size
- **Impact Scoring**: Prioritizes duplications by severity and refactoring benefit
- **Smart Exclusions**: Configurable patterns to exclude test files, migrations, vendor code

### Output Formats
- **Human-Readable Reports**: Detailed text reports with refactoring suggestions
- **JSON Output**: Machine-readable data for CI/CD integration
- **GitHub Annotations**: Inline code comments in pull requests
- **Artifact Generation**: Persistent reports for build pipelines

### CI/CD Integration
- **GitHub Actions Workflow**: Automated duplicate code checking on pushes and PRs
- **Failure Modes**: Configurable failure thresholds for high-impact duplications
- **PR Comments**: Automatic commenting with analysis results
- **Build Artifacts**: Report preservation for historical analysis

## 🚀 Quick Start

### Local Usage

```bash
# Analyze current directory
python3 tools/rule_of_three_checker.py .

# Use the convenient wrapper script
./tools/check_duplicates.sh

# Analyze specific directory with higher threshold
./tools/check_duplicates.sh src/ --similarity 0.9

# CI mode (JSON output + failure on high impact)
./tools/check_duplicates.sh --ci

# Strict mode (fail on any duplication)
./tools/check_duplicates.sh --strict
```

### Command Line Options

```bash
python3 tools/rule_of_three_checker.py [DIRECTORY] [OPTIONS]

Options:
  --min-similarity FLOAT    Minimum similarity threshold (0.0-1.0, default: 0.8)
  --min-lines INT          Minimum lines of code to consider (default: 5)
  --max-impact FLOAT       Maximum impact score before failing (default: 5.0)
  --exclude PATTERNS       Space-separated exclude patterns
  --json                   Output results in JSON format
  --fail-on-duplication    Exit with code 1 if duplications found (for CI)
```

## 📊 Analysis Examples

### Example Output

```
🔍 Rule of Three Duplicate Code Analysis Report
============================================================

⚠️  Found 2 duplication groups that violate the Rule of Three

## Duplication Group 1 (Impact: 4.5/10)
**Type**: Function
**Similarity**: 95.2%
**Instances**: 4

**Suggested Refactoring**: Extract common logic into a shared utility function. Found 4 similar functions.

**Duplicated Code Locations**:
  1. src/module_a.py:45-67 (process_data)
  2. src/module_b.py:123-145 (transform_data)
  3. src/module_c.py:89-111 (validate_data)
  4. src/module_d.py:201-223 (sanitize_data)

**Sample Code** (first instance):
    def process_data(input_data):
        """Process input data with validation."""
        if not input_data:
            raise ValueError("Input data cannot be empty")

        # Normalize data structure
        normalized = {}
        for key, value in input_data.items():
            normalized[key.lower()] = str(value).strip()

        # Apply business rules
        if 'id' not in normalized:
            normalized['id'] = generate_id()

        return normalized
```

### Impact Scoring

The tool calculates an impact score (0-10) based on:
- **Number of duplications** (more duplicates = higher impact)
- **Code size** (larger blocks = higher impact)
- **Fragment type** (functions and classes weighted higher)

**Impact Levels:**
- **0.0-2.0**: Low impact (minor duplications)
- **2.0-5.0**: Medium impact (should be refactored)
- **5.0-10.0**: High impact (requires immediate attention)

## 🔧 Configuration

### Project Configuration

Create `tools/rule_of_three_config.yaml`:

```yaml
analysis:
  min_similarity: 0.8
  min_lines: 5
  max_impact_threshold: 5.0

exclude_patterns:
  - "test_"
  - "__pycache__"
  - "migrations/"
  - "vendor/"

project:
  source_directories:
    - "src/"
    - "orchestration/"
    - "transformation/"
```

### GitHub Actions Integration

The tool automatically integrates with GitHub Actions via `.github/workflows/rule-of-three-check.yml`:

- **Runs on**: Push and pull request events
- **Generates**: Text and JSON reports
- **Creates**: GitHub annotations for duplicated code
- **Comments**: Analysis results on pull requests
- **Fails**: Build if high-impact duplications found

## 🎯 Detection Algorithm

### AST Normalization

The tool normalizes Python AST nodes for similarity comparison:

1. **Variable Names**: Replaced with generic identifiers (`VAR_0`, `VAR_1`)
2. **Function Signatures**: Normalized by parameter count
3. **Constants**: Grouped by type (strings, numbers)
4. **Control Flow**: Preserved structural patterns

### Similarity Calculation

1. **Exact Matches**: AST hash comparison for identical structure
2. **Near Matches**: Sequence matching on normalized content
3. **Threshold Filtering**: Only similarities above configured threshold
4. **Type Grouping**: Only compare same fragment types (function vs function)

### Rule of Three Application

- **Minimum Count**: Requires at least 3 similar code fragments
- **Impact Assessment**: Prioritizes by refactoring benefit
- **Suggestion Generation**: Provides specific refactoring advice

## 📈 Metrics and Reporting

### Summary Statistics

```json
{
  "summary": {
    "total_groups": 3,
    "total_fragments": 12,
    "high_impact_groups": 1,
    "average_impact": 3.7
  }
}
```

### Detailed Group Information

```json
{
  "id": 1,
  "fragment_type": "function",
  "similarity_score": 0.952,
  "impact_score": 4.5,
  "suggested_refactoring": "Extract common logic into utility function",
  "fragments": [
    {
      "file_path": "src/module_a.py",
      "start_line": 45,
      "end_line": 67,
      "name": "process_data"
    }
  ]
}
```

## 🛠 Integration Examples

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: rule-of-three-check
      name: Rule of Three Duplicate Code Check
      entry: ./tools/check_duplicates.sh
      args: ['--max-impact', '5.0']
      language: system
      pass_filenames: false
```

### Make Target

Add to `Makefile`:

```makefile
.PHONY: check-duplicates
check-duplicates:
	@echo "🔍 Checking for duplicate code..."
	./tools/check_duplicates.sh --ci

.PHONY: check-duplicates-strict
check-duplicates-strict:
	@echo "🔍 Strict duplicate code check..."
	./tools/check_duplicates.sh --strict
```

### Poetry Script

Add to `pyproject.toml`:

```toml
[tool.poetry.scripts]
check-duplicates = "tools.rule_of_three_checker:main"
```

## 🧪 Testing the Tool

### Test on Sample Code

```bash
# Analyze orchestration code (known to have duplications)
python3 tools/rule_of_three_checker.py orchestration/

# Test with different thresholds
python3 tools/rule_of_three_checker.py . --min-similarity 0.95

# Generate JSON report
python3 tools/rule_of_three_checker.py . --json > reports/duplicates.json
```

### Expected Results

The tool should detect:
- **Configuration Classes**: Similar Config classes with small variations
- **Boilerplate Functions**: Repeated initialization or validation logic
- **Error Handling**: Similar exception handling patterns

## 📋 Best Practices

### Refactoring Strategies

When the tool identifies duplications:

1. **Extract Functions**: Move common logic to utility functions
2. **Base Classes**: Use inheritance for similar class structures
3. **Configuration**: Move hardcoded values to config files
4. **Mixins**: Use composition for shared behavior
5. **Templates**: Use code generation for boilerplate

### Exclusion Guidelines

Exclude these patterns to avoid false positives:
- Test files (`test_*`, `*_test.py`)
- Generated code (`*_pb2.py`, migrations)
- Third-party code (`vendor/`, `node_modules/`)
- Configuration boilerplate (`__init__.py`)

### CI/CD Recommendations

- **Fail Threshold**: Set `max_impact` to 5.0 for balanced strictness
- **PR Comments**: Enable for code review guidance
- **Artifacts**: Preserve reports for trend analysis
- **Notifications**: Alert on increasing duplication trends

## 🔍 Troubleshooting

### Common Issues

**Analysis Too Slow**
- Reduce directory scope
- Increase `--min-lines` threshold
- Add more exclusion patterns

**False Positives**
- Increase `--min-similarity` threshold
- Exclude specific file patterns
- Review fragment type filters

**Missing Duplications**
- Lower `--min-similarity` threshold
- Reduce `--min-lines` requirement
- Check exclusion patterns

### Debug Mode

```bash
# Verbose output for debugging
./tools/check_duplicates.sh --verbose

# Check specific directory
python3 tools/rule_of_three_checker.py src/ --min-lines 3 --min-similarity 0.7
```

## 📚 Technical Details

### Dependencies

- **Python 3.8+**: Core language support
- **Standard Library**: `ast`, `difflib`, `pathlib`, `argparse`
- **Optional**: `pyyaml` for configuration files

### Performance Characteristics

- **Memory Usage**: O(n²) for similarity comparisons
- **Time Complexity**: O(n²) worst case for fragment pairs
- **Optimization**: Early termination on low similarity
- **Scalability**: Suitable for codebases up to 100k lines

### Algorithm Limitations

- **Python Only**: Currently supports Python source code
- **AST Parsing**: Requires syntactically valid Python
- **Structural Focus**: May miss semantic duplications
- **Threshold Sensitivity**: Requires tuning for different codebases

---

*This tool implements the "Rule of Three" principle established by Martin Fowler and other software engineering experts. It helps maintain code quality by identifying refactoring opportunities before technical debt accumulates.*
