# Project Guidelines & Workflow Rules

## Task Management Rules

### 1. Task Documentation
- **Always store action plans**: Each major task or set of action items MUST be documented in a markdown file within the `documents/` directory
- **Use descriptive naming**: Task files should follow the pattern `task-YYYY-MM-DD-{description}.md`
- **Include completion status**: Each task item should be marked with status indicators:
  - `[ ]` - Not started
  - `[~]` - In progress
  - `[x]` - Completed
  - `[!]` - Blocked/needs attention

### 2. Context Window Management
- **Long plans**: For action plans with >10 steps, break into multiple focused tasks
- **Reference previous work**: Always link to related task files when continuing work
- **Update status**: Mark completed items immediately after validation

### 3. Testing Requirements
- **Test every change**: After completing any development task, MUST run appropriate tests:
  - Code changes: Run linters, formatters, and relevant unit tests
  - Environment changes: Verify tool versions and functionality
  - Configuration changes: Test the configuration works as expected
  - Documentation: Verify examples and commands work

### 4. Validation Checklist
After completing any task, verify:
- [ ] All planned action items are completed
- [ ] Code passes pre-commit hooks
- [ ] Configuration files are valid
- [ ] Documentation is accurate and up-to-date
- [ ] Changes are committed with descriptive messages

## Git Workflow Rules

### Branch Strategy
1. **Main branch protection**: `main` branch represents production-ready code
2. **Feature branches**: Use descriptive branch names: `feature/{description}` or `task/{ticket-id}`
3. **Hotfix branches**: For urgent fixes: `hotfix/{description}`
4. **Branch naming conventions**:
   - `feature/python-environment-setup`
   - `feature/airflow-dags-implementation`
   - `hotfix/critical-bug-fix`

### Commit Standards
1. **Conventional Commits**: Follow the format:
   ```
   <type>(<scope>): <description>

   [optional body]

   [optional footer(s)]
   ```

2. **Commit Types**:
   - `feat`: A new feature
   - `fix`: A bug fix
   - `docs`: Documentation only changes
   - `style`: Code style changes (formatting, missing semi-colons, etc)
   - `refactor`: Code change that neither fixes a bug nor adds a feature
   - `test`: Adding missing tests or correcting existing tests
   - `chore`: Changes to build process or auxiliary tools

3. **Examples**:
   ```
   feat(python): add pyenv and poetry environment management

   - Install Python 3.11.13 via pyenv
   - Configure Poetry with dependency groups
   - Set up pre-commit hooks for code quality
   - Create requirements files for Docker compatibility

   Closes #123
   ```

### Workflow Process
1. **Before starting work**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/descriptive-name
   ```

2. **During development**:
   ```bash
   # Make changes
   git add .
   git commit -m "feat(scope): descriptive commit message"

   # Push regularly
   git push origin feature/descriptive-name
   ```

3. **Before committing**:
   ```bash
   # Ensure code quality
   pre-commit run --all-files

   # Run tests if applicable
   pytest tests/

   # Verify functionality
   ./scripts/verify-setup.sh
   ```

4. **Creating pull requests**:
   - Use descriptive PR titles
   - Include task completion checklist
   - Reference related issues/tasks
   - Add screenshots for UI changes

### Required Checks
Before any merge to main:
- [ ] All pre-commit hooks pass
- [ ] Code is properly documented
- [ ] No secrets or sensitive data committed
- [ ] Requirements files are updated if dependencies changed
- [ ] Tests pass (when applicable)

## Implementation Rules for AI Assistant

### Always Follow These Steps:
1. **Document the plan**: Create or update task file with action items
2. **Execute systematically**: Work through items one by one
3. **Test each change**: Verify functionality after each major change
4. **Update status**: Mark completed items in the task file
5. **Commit properly**: Use conventional commit format
6. **Validate completion**: Run full validation checklist

### Error Recovery:
- If a step fails, document the issue in the task file
- Mark problematic items as `[!]` blocked
- Provide clear error description and potential solutions
- Don't proceed to dependent steps until blockers are resolved

### Communication:
- Always report progress on task completion
- Highlight any deviations from the original plan
- Ask for guidance when encountering unexpected issues
- Provide clear next steps for any remaining work

## File Locations

### Task Files
- **Location**: `documents/tasks/`
- **Archive**: Completed tasks moved to `documents/tasks/archive/`
- **Template**: Use `documents/templates/task-template.md`

### Documentation
- **Technical docs**: `docs/`
- **Project guidelines**: `documents/`
- **Process docs**: `documents/processes/`

### Scripts
- **Automation**: `scripts/`
- **Validation**: `scripts/verify-*`
- **Setup**: `scripts/setup-*`

---

*Last updated: 2025-06-30*
*Version: 1.0*
