# Validate PRP

## PRP File: $ARGUMENTS

Pre-flight validation of a PRP to ensure all context and dependencies are available before execution.

## Validation Process

1. **Parse PRP**
   - Read the specified PRP file
   - Extract all file references, URLs, and dependencies
   - Parse validation checklist items

2. **Context Validation**
   - Check all referenced files exist
   - Validate all URLs are accessible
   - Verify environment dependencies are available
   - Check for required API keys/credentials

3. **Codebase Analysis**
   - Scan for similar patterns mentioned in PRP
   - Validate existing examples are current
   - Check for architectural consistency

4. **Dependency Check**
   - Verify all required libraries are installed
   - Check version compatibility
   - Validate external service connectivity

5. **Risk Assessment**
   - Analyze failure patterns mentioned in PRP
   - Assess complexity and confidence score
   - Identify potential bottlenecks

## Validation Gates

### File References

```bash
# Check all referenced files exist
echo "Validating file references..."
for file in $(grep -o 'file: [^[:space:]]*' "$PRP_FILE" | cut -d' ' -f2); do
    if [ ! -f "$file" ]; then
        echo "❌ Missing file: $file"
        exit 1
    else
        echo "✅ Found: $file"
    fi
done
```

### URL Accessibility

```bash
# Check all referenced URLs are accessible
echo "Validating URL references..."
for url in $(grep -o 'url: [^[:space:]]*' "$PRP_FILE" | cut -d' ' -f2); do
    if curl -s --head "$url" > /dev/null; then
        echo "✅ Accessible: $url"
    else
        echo "⚠️  Cannot access: $url"
    fi
done
```

### Environment Dependencies

```bash
# Check environment setup
echo "Validating environment dependencies..."

# Check Python dependencies
if command -v python3 &> /dev/null; then
    echo "✅ Python3 available"

    # Check specific imports mentioned in PRP
    python3 -c "
import re
import sys
# Read PRP file and extract import statements
with open('$PRP_FILE', 'r') as f:
    content = f.read()
# Find import statements in code blocks
imports = re.findall(r'^(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE)
unique_imports = set(imports)
failed_imports = []
for module in unique_imports:
    try:
        __import__(module)
        print(f'✅ Module available: {module}')
    except ImportError:
        failed_imports.append(module)
        print(f'⚠️  Module missing: {module}')
if failed_imports:
    print(f'❌ Missing modules: {failed_imports}')
    sys.exit(1)
"
else
    echo "❌ Python3 not available"
    exit 1
fi
```

### API Connectivity

```bash
# Check external API connectivity
echo "Validating API connectivity..."

# Check common APIs mentioned in PRP
if grep -q "api.openai.com" "$PRP_FILE"; then
    if [ -n "$OPENAI_API_KEY" ]; then
        echo "✅ OpenAI API key configured"
    else
        echo "⚠️  OpenAI API key not set"
    fi
fi

if grep -q "api.anthropic.com" "$PRP_FILE"; then
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        echo "✅ Anthropic API key configured"
    else
        echo "⚠️  Anthropic API key not set"
    fi
fi

# Add more API checks as needed
```

## Validation Report

Generate a comprehensive validation report with:

1. **Context Completeness Score** (0-100)
2. **Dependency Readiness** (Ready/Issues/Blocked)
3. **Risk Assessment** (Low/Medium/High)
4. **Recommended Actions** (before execution)

## Output Format

```
🔍 PRP Validation Report
========================
📁 Context Validation: [PASS/FAIL]
- Files referenced: X/X found
- URLs accessible: X/X responding
- Examples current: [YES/NO]
🔧 Dependencies: [READY/ISSUES/BLOCKED]
- Python modules: X/X available
- External services: X/X accessible
- API keys: X/X configured
⚠️  Risk Assessment: [LOW/MEDIUM/HIGH]
- Complexity score: X/10
- Failure patterns: X identified
- Mitigation strategies: X documented
📊 Readiness Score: XX/100
🎯 Recommended Actions:
[ ] Install missing dependencies
[ ] Configure missing API keys
[ ] Update stale examples
[ ] Review risk mitigation strategies
Status: [READY_TO_EXECUTE/NEEDS_ATTENTION/BLOCKED]
```

## Auto-Fix Suggestions

When validation fails, provide actionable suggestions:

```bash
# Auto-generate fixes where possible
if [ "$STATUS" != "READY_TO_EXECUTE" ]; then
    echo "🔧 Auto-fix suggestions:"
    echo "pip install missing-module-1 missing-module-2"
    echo "export MISSING_API_KEY=your_key_here"
    echo "git checkout HEAD -- outdated-example.py"
fi
```

## Integration with Execute Command

The validate command should be automatically called by execute-prp before starting implementation:

```bash
# In execute-prp.md, add this as step 0:
echo "Running pre-execution validation..."
validate-prp "$PRP_FILE"
if [ $? -ne 0 ]; then
    echo "❌ Validation failed. Please fix issues before execution."
    exit 1
fi
```

### Data Stack Context

```yaml
# MUST READ - Data stack specific context
- file: agents/data_stack_engineer.py
  why: Core AI agent patterns for data infrastructure management

- file: tools/duckdb_tools.py
  why: Database operations and analytics patterns (90% cost reduction vs Snowflake)

- file: tools/meltano_tools.py
  why: ELT pipeline management with Singer protocol

- file: tools/dbt_tools.py
  why: Data transformation and modeling patterns

- file: data_stack/airflow/dags/
  why: Workflow orchestration patterns with AI agent integration

- file: data_stack/dbt/models/staging/
  why: 31-column EDA transformation patterns

- url: http://localhost:8501
  why: Streamlit dashboard for real-time data monitoring

- url: http://localhost:3000
  why: Grafana monitoring and alerting interface

- url: http://localhost:8080
  why: Airflow UI for pipeline orchestration
```

### Data Stack Architecture Patterns
```python
# CRITICAL: Use existing agent patterns
from agents.data_stack_engineer import DataStackEngineer
from agents.base_agent import WorkflowRequest, AgentResponse

agent = DataStackEngineer()
result = await agent.execute_task(WorkflowRequest(
    user_prompt="YOUR_DATA_STACK_TASK"
))

# CRITICAL: Cost optimization patterns (~$50/month target)
config.cost_optimization = {
    "duckdb_vs_snowflake": "90% cost reduction",
    "self_hosted_vs_cloud": "88-95% savings",
    "quality_threshold": 0.85
}

# CRITICAL: Use venv_linux for Python commands
# Example: pytest tests/ should be run in venv_linux environment
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check scripts/ --fix          # Auto-fix Python scripts
ruff check PRPs/scripts/ --fix     # Fix PRP utility scripts
mypy scripts/                      # Type checking
black scripts/ PRPs/scripts/       # Code formatting

# Validate markdown files
markdownlint .claude/commands/*.md PRPs/templates/*.md PRPs/ai_docs/*.md

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Testing
```bash
# Test new functionality
uv run pytest tests/test_*.py -v

# Test data stack specific workflows
uv run pytest tests/test_data_stack_workflows.py -v
uv run pytest tests/test_prp_integration.py -v

# Expected: All tests pass, existing functionality preserved, new functionality working
```

### Level 3: Integration Testing
```bash
# Test complete workflow with data stack
.claude/commands/deploy-data-stack.md --validate-only
.claude/commands/monitor-data-stack.md --health-check
.claude/commands/validate-pipeline.md --verbose

# Test enhanced PRP workflows
.claude/commands/prp-base-create.md "Test integration workflow"
.claude/commands/prp-base-execute.md "PRPs/test-integration-prp.md"

# Expected: All workflows functional, no regression in data stack capabilities
```

### Level 4: Creative Validation
```bash
# Test end-to-end data pipeline
cd data_stack/meltano && meltano --environment=dev elt tap-csv target-duckdb
cd ../dbt && dbt run --profiles-dir . && dbt test --profiles-dir .

# Verify dashboard functionality
curl -f http://localhost:8501/health || echo "Streamlit dashboard check"
curl -f http://localhost:3000/api/health || echo "Grafana monitoring check"

# AI agent validation
python -c "
from agents.data_stack_engineer import DataStackEngineer
from agents.base_agent import WorkflowRequest
agent = DataStackEngineer()
print('AI agent system functional')
"

# Expected: Complete data pipeline functional, monitoring operational
```
