# 🤖 AI Agent Warp Workflows

This directory contains Warp terminal workflows and functions designed to streamline AI agent interactions with your data stack project.

## 🚀 Quick Setup

1. **Run the setup script:**
   ```bash
   bash .warp/setup.sh
   ```

2. **For persistent access across all terminals, add to your shell profile:**
   ```bash
   echo 'source $(pwd)/.warp/agent_functions.sh' >> ~/.zshrc
   # or for bash users:
   echo 'source $(pwd)/.warp/agent_functions.sh' >> ~/.bashrc
   ```

3. **Reload your shell or source the functions:**
   ```bash
   source .warp/agent_functions.sh
   ```

## 📋 Available Commands

### Main Workflow Functions

| Command | Description | Usage |
|---------|-------------|-------|
| `ads` | Start AI Agent Development Session | `ads` |
| `atest` | Run comprehensive test suite | `atest` |
| `aenv` | Setup development environment | `aenv` |
| `ahealth` | Check service health | `ahealth` |
| `apr` | Create PR with AI-generated content | `apr [branch-name] [commit-message]` |
| `aclean` | Clean caches and temporary files | `aclean` |

### Quick Shortcuts

| Alias | Full Command | Description |
|-------|--------------|-------------|
| `qi` | `poetry install --with dev,test` | Quick install |
| `qt` | `poetry run pytest tests/ -v --tb=short` | Quick test |
| `qf` | Format and lint code | Quick format |
| `qs` | `docker-compose up -d postgres redis` | Quick start services |
| `qd` | `docker-compose down` | Quick stop services |

## 🎯 Common Workflows

### 1. Starting a Development Session
```bash
ads  # Shows project status, environment info, and available commands
```

### 2. Running Tests Before Deployment
```bash
atest  # Runs quality checks and comprehensive test suite
```

### 3. Setting Up Environment
```bash
aenv  # Installs dependencies, creates directories, starts services
```

### 4. Creating a PR
```bash
apr  # Creates branch, commits changes, runs checks, creates PR
# or with custom parameters:
apr "feature/new-improvement" "feat: add new analytics feature"
```

### 5. Health Check
```bash
ahealth  # Checks Docker services, PostgreSQL, Redis connections
```

## 📁 File Structure

```
.warp/
├── README.md                 # This file
├── setup.sh                 # Setup script
├── agent_functions.sh        # Main functions and aliases
├── agent_rules.yaml         # AI agent configuration rules
├── workflows/
│   ├── agent_test_suite.json # Warp workflow for testing
│   ├── agent_test_suite.yaml # Extended workflow definition
│   ├── dev_environment.yaml  # Development environment workflow
│   └── agent_pr_loop.yaml   # PR creation workflow
├── templates/
│   └── dev_commands.yaml    # Command templates
└── macros/
    └── agent_sessions.yaml  # Session macros
```

## 🔧 Customization

### Adding New Functions

Edit `.warp/agent_functions.sh` to add new functions:

```bash
my_custom_function() {
    echo "🎯 Running custom workflow..."
    # Your commands here
}

# Add alias
alias mcf='my_custom_function'
```

### Modifying Existing Functions

Each function in `agent_functions.sh` can be customized for your specific needs. For example, to change the test command in `atest`, modify the `poetry run pytest` line.

### Environment Variables

The functions set up these environment variables:
- `PYTHONPATH` - Includes current directory
- Standard Poetry and Docker environment

## 🎨 Features

- **🌈 Colored Output**: Functions use colors to make output more readable
- **🔍 Health Checks**: Automatic service health verification
- **🧪 Test Integration**: Comprehensive testing with quality checks
- **📝 PR Automation**: Automated PR creation with standardized templates
- **🧹 Cleanup Tools**: Cache and temporary file management
- **⚡ Quick Commands**: Short aliases for common operations

## 🆘 Troubleshooting

### Functions Not Available
If functions aren't available after setup:
1. Make sure you sourced the file: `source .warp/agent_functions.sh`
2. Check if the file is executable: `chmod +x .warp/agent_functions.sh`
3. Verify your shell: `echo $SHELL`

### Service Connection Issues
If health checks fail:
1. Start services: `qs` or `docker-compose up -d postgres redis`
2. Check Docker: `docker-compose ps`
3. Verify ports: `lsof -i :5432,6379`

### Test Failures
If tests fail:
1. Install dependencies: `qi`
2. Check environment: `poetry env info`
3. Run specific tests: `poetry run pytest tests/unit/ -v`

## 🔄 Integration with Warp

These workflows integrate with Warp's features:

1. **Command Palette**: Use `Cmd+P` in Warp to search for any of these commands
2. **History**: All commands are saved in Warp's history
3. **Workflows**: The JSON workflow files can be imported into Warp
4. **Blocks**: Each function creates organized output blocks in Warp

## 📚 Next Steps

1. **Try the basic workflow**: `ads` → `atest` → `apr`
2. **Customize functions** for your specific needs
3. **Add new workflows** based on your development patterns
4. **Integrate with CI/CD** by using these functions in GitHub Actions

## 🤝 Contributing

To add new workflows or improve existing ones:
1. Edit the appropriate files in `.warp/`
2. Test your changes: `source .warp/agent_functions.sh`
3. Update this README if adding new commands
4. Submit your improvements via PR

---

*These workflows are designed to work seamlessly with AI agents and improve development efficiency in Warp terminal.*
