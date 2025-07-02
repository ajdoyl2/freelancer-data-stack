# Comprehensive Code Review

**Complexity**: Intermediate
**Estimated Time**: 15-30 minutes
**Dependencies**: Code to review, understanding of project standards
**Related Prompts**: refactor_function.md, error_handling.md, performance_optimization.md
**Tags**: code-quality, review, best-practices, python, data-stack

## Objective
Perform a thorough code review focusing on quality, security, performance, and alignment with the freelancer data stack project standards.

## Context
### Project Environment
- **Data Stack**: Dagster (orchestration), dbt (transformation), DuckDB (warehouse), Streamlit (visualization)
- **Infrastructure**: Docker Compose, Poetry (dependency management), PostgreSQL, Redis
- **Development**: Python 3.11, Ruff/Black (linting), pytest (testing), GitHub Actions (CI/CD)
- **Monitoring**: DataHub (metadata), Great Expectations (data quality)

### Current Situation
You are reviewing code for the freelancer data stack project. Focus on maintainability, performance, security, and integration with the existing data pipeline architecture.

## Instructions

### Step 1: Initial Code Analysis
1. **Read the entire code** to understand the purpose and context
2. **Identify the code type**: Dagster asset, dbt model, API endpoint, utility function, etc.
3. **Understand the data flow** and how it fits into the overall pipeline
4. **Note any immediate red flags** (security issues, obvious bugs, anti-patterns)

### Step 2: Code Quality Assessment

#### Syntax & Style
- [ ] **PEP 8 compliance** - Check formatting, naming conventions, line length
- [ ] **Type hints** - Verify proper type annotations for function parameters and returns
- [ ] **Docstrings** - Ensure comprehensive documentation following project standards
- [ ] **Import organization** - Check for proper grouping and ordering (stdlib, third-party, local)
- [ ] **Code organization** - Logical structure, appropriate class/function decomposition

#### Logic & Functionality  
- [ ] **Correctness** - Does the code do what it's supposed to do?
- [ ] **Edge cases** - Are boundary conditions and error scenarios handled?
- [ ] **Data validation** - Input validation and sanitization where appropriate
- [ ] **Business logic** - Alignment with business requirements and data pipeline needs
- [ ] **Algorithm efficiency** - Appropriate algorithms and data structures

### Step 3: Data Stack Integration Review

#### Dagster Compatibility
- [ ] **Asset dependencies** - Proper upstream/downstream asset relationships
- [ ] **Resource usage** - Correct use of Dagster resources (database connections, configs)
- [ ] **Metadata handling** - Appropriate metadata and logging
- [ ] **Partitioning** - Correct partitioning strategy if applicable
- [ ] **Error handling** - Proper failure modes and retry logic

#### dbt Integration (if applicable)
- [ ] **Model structure** - Proper staging/intermediate/marts organization
- [ ] **Incremental logic** - Correct incremental model implementation
- [ ] **Testing** - Appropriate dbt tests (unique, not_null, relationships)
- [ ] **Documentation** - Model and column descriptions
- [ ] **Macros usage** - Proper use of dbt macros and functions

#### Database & Performance
- [ ] **SQL efficiency** - Optimized queries and appropriate indexing considerations
- [ ] **Connection management** - Proper database connection handling
- [ ] **Transaction management** - Appropriate use of transactions
- [ ] **Memory usage** - Efficient data processing patterns
- [ ] **Batch processing** - Appropriate batch sizes for large datasets

### Step 4: Security & Best Practices

#### Security Review
- [ ] **Input validation** - SQL injection, XSS, and other injection prevention
- [ ] **Secrets management** - No hardcoded credentials or sensitive data
- [ ] **Access control** - Proper authentication and authorization
- [ ] **Data privacy** - PII handling and data protection compliance
- [ ] **Dependency security** - No known vulnerable dependencies

#### Error Handling & Reliability
- [ ] **Exception handling** - Proper try/catch blocks with meaningful error messages
- [ ] **Logging** - Appropriate log levels and structured logging
- [ ] **Graceful degradation** - Fallback mechanisms where appropriate
- [ ] **Resource cleanup** - Proper cleanup of connections, files, etc.
- [ ] **Monitoring hooks** - Integration with monitoring systems

### Step 5: Testing & Documentation

#### Test Coverage
- [ ] **Unit tests** - Adequate test coverage for all functions
- [ ] **Integration tests** - Tests for external dependencies
- [ ] **Mock usage** - Proper mocking of external services
- [ ] **Test data** - Appropriate test fixtures and data setup
- [ ] **Edge case testing** - Tests for boundary conditions and error scenarios

#### Documentation Quality
- [ ] **API documentation** - Clear function/class documentation
- [ ] **Usage examples** - Code examples where helpful
- [ ] **Configuration docs** - Documentation of configuration options
- [ ] **Architecture notes** - High-level design decisions explained
- [ ] **Deployment notes** - Any special deployment considerations

## Expected Output

### Format
Provide a structured review with the following sections:

### Content Requirements

#### 1. Executive Summary
- Overall code quality score (1-10)
- Main strengths and areas for improvement
- Critical issues that must be addressed
- Estimated effort to address all issues

#### 2. Detailed Findings

##### Critical Issues (Must Fix)
- Security vulnerabilities
- Data corruption risks
- Performance bottlenecks
- Integration breaking changes

##### Major Issues (Should Fix)
- Code quality problems
- Missing error handling
- Poor performance patterns
- Incomplete testing

##### Minor Issues (Nice to Have)
- Style improvements
- Documentation enhancements
- Code organization suggestions
- Performance optimizations

#### 3. Specific Recommendations
For each issue, provide:
- **Location**: File name and line number(s)
- **Issue**: Clear description of the problem
- **Impact**: Risk level and potential consequences
- **Solution**: Specific code changes or approaches to fix
- **Example**: Before/after code snippets where helpful

#### 4. Positive Highlights
- Well-implemented patterns
- Good design decisions
- Excellent documentation
- Robust error handling
- Performance optimizations

## Quality Criteria

### Technical Standards
- [ ] All code quality issues identified with specific locations
- [ ] Security implications thoroughly assessed
- [ ] Performance considerations evaluated
- [ ] Integration points with data stack verified
- [ ] Actionable recommendations provided

### Review Completeness
- [ ] Every function/class reviewed
- [ ] Data flow implications considered
- [ ] Testing strategy evaluated
- [ ] Documentation completeness assessed
- [ ] Deployment considerations noted

## Examples

### Input Example
```python
def process_customer_data(data):
    results = []
    for item in data:
        if item['revenue'] > 1000:
            results.append({
                'id': item['customer_id'],
                'category': 'high_value'
            })
    return results
```

### Expected Output Example
```markdown
## Executive Summary
Code Quality Score: 4/10
This function has basic functionality but lacks error handling, type hints, 
documentation, and efficient data processing patterns.

## Critical Issues
None identified.

## Major Issues
1. **Missing Error Handling** (Lines 3-8)
   - No validation of input data structure
   - KeyError risk if 'revenue' or 'customer_id' keys are missing
   - Solution: Add try/catch and input validation

2. **Missing Type Hints** (Line 1)
   - Function parameters and return type not specified
   - Solution: Add proper type annotations

## Recommendations
```python
from typing import List, Dict, Any

def process_customer_data(data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Process customer data to identify high-value customers.
    
    Args:
        data: List of customer dictionaries with 'customer_id' and 'revenue'
        
    Returns:
        List of high-value customer records
        
    Raises:
        ValueError: If required keys are missing from customer data
    """
    if not isinstance(data, list):
        raise ValueError("Input data must be a list")
    
    results = []
    for item in data:
        try:
            if item.get('revenue', 0) > 1000:
                results.append({
                    'id': item['customer_id'],
                    'category': 'high_value'
                })
        except KeyError as e:
            raise ValueError(f"Missing required key in customer data: {e}")
    
    return results
```
```

## Troubleshooting

### Common Issues
- **Too many minor issues**: Focus on critical and major issues first
- **Missing context**: Ask for more information about the code's purpose
- **Performance assumptions**: Request actual performance requirements

### Validation Steps
1. Verify all recommendations are actionable and specific
2. Ensure security considerations are thoroughly covered
3. Check that data stack integration points are reviewed
4. Confirm examples are relevant and helpful

## Follow-up Actions

### Immediate Next Steps
- Address critical issues before any deployment
- Create GitHub issues for major improvements
- Update documentation based on findings
- Add missing tests identified in review

### Related Tasks
- Use `refactor_function.md` for specific function improvements
- Apply `error_handling.md` for robustness enhancements
- Reference `performance_optimization.md` for speed improvements

---

**Version**: 1.0
**Last Updated**: July 2025
**Created By**: AI Agent Team
