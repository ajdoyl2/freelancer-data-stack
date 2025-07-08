# PRP Workflow Documentation

## Product Requirements Prompt (PRP) System

The PRP system enables AI agents to implement production-ready features through comprehensive context engineering and validation loops.

### Core Principles

1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance

### PRP Structure

#### Required Sections
```markdown
## Goal
[What needs to be built - specific end state]

## Why
- Business value and user impact
- Integration with existing features
- Problems this solves

## What
[User-visible behavior and technical requirements]

## All Needed Context
### Documentation & References
- url: [API docs]
- file: [example code]
- docfile: [project docs]

### Known Gotchas
- Library quirks
- Performance considerations
- Security requirements

## Implementation Blueprint
### Data models
### Task list
### Pseudocode
### Integration points

## Validation Loop
### Level 1: Syntax & Style
### Level 2: Unit Tests
### Level 3: Integration Tests
### Level 4: Creative Validation
```

### Data Stack Specific Enhancements

#### Environment Integration
```bash
# CRITICAL: Use venv_linux for all Python commands
source venv_linux/bin/activate
```

#### Agent Structure
```
agents/your_agent/
├── agent.py      # Main agent logic
├── tools.py      # Tool functions
└── prompts.py    # System prompts
```

#### Cost Optimization
- **Target**: $50/month operational cost
- **Pattern**: 90% reduction vs cloud alternatives
- **Monitoring**: Real-time cost tracking

#### Quality Gates
- **Threshold**: 0.85 minimum quality score
- **Validation**: 4-level progressive validation
- **Automation**: AI-executable validation commands

### PRP Execution Workflow

#### 1. PRP Creation
```bash
# Interactive creation
/prp-base-create "Your feature description"

# Planning-focused creation
/prp-planning-create "Your planning requirements"
```

#### 2. Context Engineering
- Research existing patterns
- Gather documentation
- Identify integration points
- Document gotchas and constraints

#### 3. AI Execution
```bash
# Interactive mode (recommended)
python PRPs/scripts/prp_runner.py --prp-path PRPs/your-feature.md --interactive

# Headless mode (for automation)
python PRPs/scripts/prp_runner.py --prp-path PRPs/your-feature.md --output-format json
```

#### 4. Validation
```bash
# Level 1: Syntax & Style
ruff check --fix && mypy . && black .

# Level 2: Unit Tests
pytest tests/ -v

# Level 3: Integration Tests
docker-compose up -d && curl http://localhost:8501/health

# Level 4: Creative Validation
python scripts/test_full_pipeline.py --validate-cost-optimization
```

### Best Practices

#### PRP Writing
1. **Be Specific**: Clear, measurable success criteria
2. **Include Examples**: Code patterns and usage examples
3. **Document Constraints**: Performance, security, cost limits
4. **Test Instructions**: Executable validation commands

#### AI Agent Usage
1. **Prime Context**: Load comprehensive project context
2. **Iterative Development**: Start simple, validate, enhance
3. **Follow Patterns**: Use existing agent and tool structures
4. **Validate Continuously**: Run validation gates frequently

#### Quality Assurance
1. **4-Level Validation**: Syntax → Unit → Integration → Creative
2. **Cost Monitoring**: Track against $50/month target
3. **Performance Testing**: Ensure sub-second response times
4. **Security Validation**: Input validation and access control

### Troubleshooting PRPs

#### Common Issues
1. **Insufficient Context**: Add more documentation and examples
2. **Validation Failures**: Check executable commands and fix errors
3. **Integration Problems**: Verify service endpoints and dependencies
4. **Performance Issues**: Profile and optimize critical paths

#### Debugging Steps
1. **Check PRP Structure**: Validate against template requirements
2. **Test Validation Gates**: Run each level independently
3. **Review Logs**: Check service logs for errors
4. **Run Diagnostics**: Use comprehensive validation system

### Advanced Features

#### Parallel PRP Creation
```bash
# Create multiple related PRPs simultaneously
/prp-parallel-create "Feature set description"
```

#### Streaming Output
```bash
# Real-time PRP execution monitoring
python PRPs/scripts/prp_runner.py --prp-path PRPs/your-feature.md --output-format stream-json
```

#### Validation Automation
```bash
# Automated quality gates
python PRPs/scripts/data_stack_prp_helper.py --prp-path PRPs/your-feature.md --validate-only
```

### Integration with Data Stack

#### Pipeline Integration
- **Meltano**: ELT pipeline integration
- **dbt**: Data transformation patterns
- **Airflow**: Workflow orchestration
- **DuckDB**: Analytics database operations

#### Monitoring Integration
- **Grafana**: Dashboard creation
- **Prometheus**: Metrics collection
- **Streamlit**: Real-time monitoring

#### Agent Integration
- **DataStackEngineer**: Core infrastructure agent
- **Tool Integration**: Comprehensive tool ecosystem
- **Context Management**: Project-specific context injection

---

*PRP system enables one-pass implementation success through comprehensive context and validation*
