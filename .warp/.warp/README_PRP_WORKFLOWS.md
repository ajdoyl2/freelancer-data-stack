# PRP Workflows Documentation

## Overview

PRP (Pull Request Process) workflows are comprehensive, standardized processes for software development activities including feature development, code reviews, deployment validation, and emergency hotfixes. These workflows are designed to integrate seamlessly with our data stack architecture and maintain operational excellence.

## Purpose

PRP workflows serve to:
- **Standardize Development Processes**: Consistent approach to feature development, code reviews, and deployments
- **Ensure Quality**: Built-in validation gates and best practices adherence
- **Enable Automation**: AI-agent compatible workflows for autonomous operation
- **Maintain Cost Efficiency**: Adherence to $50/month operational cost target
- **Support Data Stack Integration**: Seamless integration with Airflow, dbt, DuckDB, and Meltano

## Location & Structure

### Primary Locations

```
.warp/
├── workflows/
│   ├── prp-base-create.yaml          # Base PRP creation workflow
│   ├── prp-base-execute.yaml         # Base PRP execution workflow
│   ├── prp-planning-create.yaml      # Planning PRP creation workflow
│   └── agent_pr_loop.yaml            # Agent-driven PR loop
├── prp_workflow_template.yaml        # Template for new PRP workflows
├── prp_workflows_json.json           # JSON format PRP workflows
└── import_workflows.py               # Dynamic workflow importer
```

### Workflow Categories

1. **Creation Workflows**: Generate comprehensive PRPs with research and validation
2. **Execution Workflows**: Execute PRPs with proper validation gates
3. **Planning Workflows**: Transform ideas into comprehensive PRDs
4. **Review Workflows**: Code review processes with quality gates
5. **Deployment Workflows**: Deployment validation and monitoring
6. **Emergency Workflows**: Hotfix processes for critical issues

## Example Usage

### 1. Creating a Base PRP

```bash
# Create a comprehensive PRP for a new feature
warp workflow run "PRP: Base Create" feature-name
```

This workflow will:
- Guide through comprehensive research process
- Generate implementation blueprint
- Create validation gates
- Output structured PRP document

### 2. Development Process

```bash
# Start development process for a feature
warp workflow run "PRP - Feature Development" "Data Pipeline" "pipeline-feature" "tests/data/"
```

This provides:
- Pre-development checklist
- Branch management guidance
- Quality setup instructions
- Testing strategy
- Deployment validation

### 3. Code Review Process

```bash
# Initiate comprehensive code review
warp workflow run "PRP - Code Review" "Data Pipeline" "85%"
```

Review covers:
- Code quality and style
- Architecture compliance
- Data stack integration
- Security best practices
- Performance optimization

### 4. Deployment Validation

```bash
# Validate deployment to production
warp workflow run "PRP - Deployment Validation" "production" "critical"
```

Includes:
- Pre-deployment checks
- Environment verification
- Post-deployment monitoring
- Rollback procedures

### 5. Emergency Hotfix

```bash
# Handle critical production issues
warp workflow run "PRP - Emergency Hotfix" "Database Connection Issue" "Critical" "All services"
```

Provides:
- Immediate response procedures
- Rapid stabilization steps
- Accelerated testing process
- Emergency deployment guidance

## Technical Integration

### Data Stack Components

PRP workflows integrate with:

- **Airflow**: Task decorators for DAG patterns, retry logic with exponential backoff
- **dbt**: Model compilation, testing, and documentation generation
- **DuckDB**: Analytics queries and cost optimization
- **Meltano**: Data ingestion pipeline validation
- **uv**: Package management and dependency verification

### Validation Gates

Standard validation commands included in workflows:

```bash
# Code quality
ruff check --fix && mypy .

# Testing
uv run pytest tests/ -v

# dbt validation
dbt compile && dbt test

# Dependency management
uv sync && uv --version && uv tree
```

### Agent Integration

All workflows are designed for Pydantic AI agent compatibility:
- Structured responses for autonomous operation
- MCP server tool integration
- Clear execution instructions
- Validation feedback loops

## Guidelines for Adding Future PRP Commands

### 1. Workflow Structure

Use the standardized YAML structure:

```yaml
name: "PRP - [Category]: [Purpose]"
description: "Brief description of workflow purpose"
version: "1.0.0"
tags: ["prp", "category", "specific-tags"]

arguments:
  - name: "parameter_name"
    description: "Parameter description"
    default_value: "${1}"

commands:
  - name: "command_name"
    description: "Command description"
    command: |
      echo "Workflow content..."

workflow:
  - command_name
```

### 2. Content Guidelines

**Structure Requirements:**
- Clear section headers with emoji indicators
- Numbered steps for complex processes
- Validation checkpoints throughout
- Error handling and rollback procedures

**Technical Standards:**
- Include relevant validation gates
- Reference specific tools and commands
- Provide parameter expansion examples
- Ensure agent-compatible output

**Integration Points:**
- Data stack tool integration
- Cost optimization considerations
- Performance validation steps
- Security best practices

### 3. Naming Conventions

```
prp-[category]-[action].yaml
```

Examples:
- `prp-feature-create.yaml`
- `prp-security-audit.yaml`
- `prp-performance-optimize.yaml`

### 4. Template Usage

Base your new workflows on `prp_workflow_template.yaml`:

```yaml
# Copy template structure
# Customize command content
# Update tags and arguments
# Add to .warp/workflows/
# Run import_workflows.py
```

### 5. Parameter Expansion

Use bash parameter expansion for flexibility:

```bash
${1:-default_value}    # Use $1 if set, otherwise default
${2:-feature-name}     # Use $2 if set, otherwise "feature-name"
${3:-tests/}           # Use $3 if set, otherwise "tests/"
```

### 6. Quality Checklist

Before adding new PRP workflows:

- [ ] Follows standardized YAML structure
- [ ] Includes comprehensive validation gates
- [ ] Integrates with data stack tools
- [ ] Provides clear error handling
- [ ] Supports agent automation
- [ ] Includes cost optimization considerations
- [ ] Has proper documentation
- [ ] Uses standard parameter expansion
- [ ] Includes relevant tags
- [ ] Follows naming conventions

### 7. Testing New Workflows

```bash
# 1. Add workflow file to .warp/workflows/
# 2. Import workflows
cd .warp && python import_workflows.py

# 3. Test workflow execution
warp workflow run "Your New PRP Workflow" param1 param2

# 4. Validate output and functionality
# 5. Document any special requirements
```

### 8. Integration with Existing Systems

Ensure new workflows integrate with:

- **Version Control**: Git operations and branch management
- **CI/CD**: Pipeline validation and deployment processes
- **Monitoring**: Health checks and performance metrics
- **Documentation**: Automated documentation generation
- **Cost Management**: Resource optimization and tracking

### 9. Advanced Features

Consider adding:

- **Conditional Logic**: Environment-specific behavior
- **Parallel Execution**: Multiple validation streams
- **Progress Tracking**: Step completion indicators
- **Rollback Automation**: Automatic failure recovery
- **Notification Integration**: Team communication triggers

### 10. Best Practices

- **Modular Design**: Reusable components across workflows
- **Clear Documentation**: Comprehensive inline documentation
- **Error Recovery**: Graceful failure handling
- **Performance Optimization**: Efficient resource usage
- **Security First**: Security validation in all workflows
- **Cost Consciousness**: Always consider operational costs

## Workflow Import Process

The dynamic import mechanism automatically loads all YAML files from `.warp/workflows/`:

```bash
cd .warp
python import_workflows.py
```

This will:
- Scan for all `.yaml` and `.yml` files
- Parse and validate workflow structure
- Import into Warp's SQLite database
- Report import status and available workflows

## Maintenance

### Regular Updates

- Review and update validation gates
- Ensure tool version compatibility
- Update cost optimization strategies
- Refresh best practices documentation

### Monitoring

- Track workflow execution success rates
- Monitor validation gate effectiveness
- Analyze cost impact of processes
- Review agent automation performance

---

For questions or contributions to PRP workflows, refer to the specific workflow files in `.warp/workflows/` or the template in `prp_workflow_template.yaml`.
