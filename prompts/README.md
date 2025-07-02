# 🎯 AI Agent Prompt Library

A curated collection of high-quality prompts for AI agents working on the freelancer data stack project.

## 📁 Directory Structure

```
prompts/
├── README.md                 # This file - usage guide and index
├── coding/                   # Code generation and improvement prompts
├── architecture/             # System design and architecture prompts
├── debugging/                # Problem diagnosis and resolution prompts
├── testing/                  # Test creation and validation prompts
├── deployment/               # Production deployment and infrastructure prompts
├── documentation/            # Documentation generation and maintenance prompts
├── data/                     # Data modeling and pipeline prompts
└── analysis/                 # Data analysis and business intelligence prompts
```

## 🚀 Quick Start

### Using with Warp
Warp snippets are available for quick access:
```bash
# List all available prompts
cat prompts/*/index.md

# Use a specific prompt
cat prompts/coding/code_review.md

# Search for prompts by keyword
grep -r "keyword" prompts/
```

### Using with AI Agents
Reference prompts in conversations:
```
Please use the prompt from prompts/coding/refactor_function.md to improve this code...
```

## 📚 Available Prompt Categories

### 🔧 Coding Prompts
- **Code Review**: Comprehensive code quality analysis
- **Refactoring**: Code improvement and optimization
- **Bug Fixing**: Systematic debugging approach
- **API Design**: RESTful API development guidelines
- **Database Schema**: Data modeling best practices

### 🏗️ Architecture Prompts  
- **System Design**: High-level architecture planning
- **Microservices**: Service decomposition strategies
- **Data Architecture**: Pipeline and warehouse design
- **Security Architecture**: Security-first design principles
- **Performance**: Scalability and optimization planning

### 🐛 Debugging Prompts
- **Error Analysis**: Systematic error investigation
- **Performance Issues**: Bottleneck identification
- **Integration Problems**: Service communication debugging
- **Data Quality**: Data validation and cleansing
- **Production Issues**: Live system troubleshooting

### 🧪 Testing Prompts
- **Unit Tests**: Component-level test generation
- **Integration Tests**: End-to-end test scenarios
- **Performance Tests**: Load and stress testing
- **Data Quality Tests**: Data validation scenarios
- **Security Tests**: Vulnerability assessment

### 🚀 Deployment Prompts
- **Infrastructure**: Cloud resource provisioning
- **CI/CD Pipeline**: Automated deployment setup
- **Monitoring**: Observability and alerting
- **Backup & Recovery**: Disaster recovery planning
- **Security**: Production security hardening

### 📝 Documentation Prompts
- **API Documentation**: Comprehensive API docs
- **User Guides**: End-user documentation
- **Architecture Docs**: Technical documentation
- **Runbooks**: Operational procedures
- **Knowledge Transfer**: Handover documentation

### 📊 Data Prompts
- **ETL Design**: Data pipeline architecture
- **Data Modeling**: Dimensional modeling
- **Quality Checks**: Data validation rules
- **Schema Evolution**: Database migration strategies
- **Pipeline Optimization**: Performance tuning

### 📈 Analysis Prompts
- **Business Intelligence**: KPI and metrics design
- **Data Exploration**: Exploratory data analysis
- **Visualization**: Chart and dashboard design
- **Statistical Analysis**: Data science techniques
- **Reporting**: Automated report generation

## 🎯 Prompt Quality Standards

All prompts in this library follow these standards:

### ✅ Structure Requirements
- **Clear objective** stated at the beginning
- **Specific context** about the data stack environment
- **Step-by-step instructions** where applicable
- **Expected output format** clearly defined
- **Quality criteria** for evaluation

### ✅ Content Guidelines
- **Technology-specific** references to our stack (Dagster, dbt, DuckDB, etc.)
- **Best practices** integrated into instructions
- **Error handling** considerations included
- **Security implications** addressed where relevant
- **Performance considerations** mentioned when applicable

### ✅ Metadata Tags
Each prompt includes:
- **Complexity**: Beginner/Intermediate/Advanced
- **Estimated time**: How long the task should take
- **Dependencies**: Required tools or knowledge
- **Related prompts**: Cross-references to complementary prompts

## 🔄 Usage Patterns

### 1. Sequential Workflow Prompts
Use multiple prompts in sequence for complex tasks:
```
1. prompts/architecture/system_design.md
2. prompts/coding/api_design.md  
3. prompts/testing/integration_tests.md
4. prompts/deployment/production_setup.md
```

### 2. Contextual Prompt Chaining
Reference previous outputs in follow-up prompts:
```
"Using the architecture from the previous response, now apply 
prompts/coding/implement_service.md to create the user service..."
```

### 3. Prompt Customization
Adapt prompts for specific scenarios:
```
"Use prompts/data/etl_design.md but focus specifically on 
real-time streaming data from Kafka..."
```

## 🛠️ Integration with Development Tools

### Warp Terminal
- Snippets available for quick prompt access
- Command templates include prompt references
- Session macros can chain multiple prompts

### VS Code / IDEs
- Snippets can be imported as code snippets
- Extensions can reference prompt files
- Templates available for quick access

### CI/CD Pipelines
- Prompts used in automated code review
- Quality gates reference prompt criteria
- Documentation generation uses prompt templates

## 📊 Prompt Analytics

Track prompt effectiveness:
- **Usage frequency** - Which prompts are most valuable
- **Success rate** - How often prompts achieve desired outcomes
- **Improvement suggestions** - Community feedback on prompts
- **Version evolution** - How prompts improve over time

## 🤝 Contributing New Prompts

### Adding a New Prompt
1. **Choose appropriate category** directory
2. **Follow naming convention**: `snake_case.md`
3. **Use the prompt template** (see `prompts/template.md`)
4. **Include proper metadata** and tags
5. **Test with AI agents** before committing
6. **Update category index** file

### Prompt Template Structure
```markdown
# Prompt Title

**Complexity**: Beginner/Intermediate/Advanced
**Estimated Time**: 15-30 minutes
**Dependencies**: List required tools/knowledge
**Related Prompts**: Links to related prompts

## Objective
Clear statement of what this prompt achieves.

## Context
Specific information about our data stack environment.

## Instructions
Step-by-step instructions for the AI agent.

## Expected Output
Description of expected response format and content.

## Quality Criteria
How to evaluate if the output meets requirements.

## Examples
Sample inputs and outputs where helpful.
```

## 🔍 Quick Reference

### Most Used Prompts
- `coding/code_review.md` - Comprehensive code analysis
- `debugging/error_analysis.md` - Systematic troubleshooting
- `data/pipeline_design.md` - Data pipeline architecture
- `testing/unit_tests.md` - Test generation
- `documentation/api_docs.md` - API documentation

### Emergency Prompts
- `debugging/production_issues.md` - Live system problems
- `deployment/rollback_procedure.md` - Deployment rollback
- `data/data_recovery.md` - Data loss scenarios
- `architecture/scaling_urgent.md` - Urgent scaling needs

---

*This prompt library is designed to enhance AI agent effectiveness and ensure consistent, high-quality outputs across all development activities.*
