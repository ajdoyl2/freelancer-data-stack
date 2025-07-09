name: "Repository Cleanup and Change Resolution Task PRP"
description: |
  Comprehensive task plan to resolve all untracked and tracked changes in the repository,
  organizing files appropriately and ensuring clean git state.

---

## Goal
Clean up the repository by resolving all untracked files, organizing them appropriately, and ensuring a clean git state while preserving all valuable work and maintaining system functionality.

## Why
- **Repository hygiene**: Clean git state improves development workflow
- **Storage optimization**: Remove unnecessary files and organize data properly
- **Security**: Ensure no sensitive data is tracked inappropriately
- **Maintenance**: Easier navigation and understanding of project structure

## What
Systematically categorize and resolve all untracked files, create proper .gitignore rules, and organize the repository structure for optimal development workflow.

### Success Criteria
- [ ] All untracked files properly categorized and resolved
- [ ] Clean git status with no unwanted untracked files
- [ ] Proper .gitignore rules implemented
- [ ] All valuable work preserved and properly organized
- [ ] No sensitive data accidentally tracked

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- file: .gitignore
  why: Current ignore patterns to understand and extend

- file: PRPs/enhance-claude-prp-agentic-eng-integration.md
  why: Recent integration work that generated many files

- docfile: PRPs/INTEGRATION_GUIDE.md
  why: Understanding of recent system changes

- url: https://git-scm.com/docs/gitignore
  why: Git ignore pattern syntax and best practices
```

### Current Repository Analysis
```bash
# Untracked files identified:
CLAUDE.md.backup                    # Backup file - safe to ignore
README.md.backup                    # Backup file - safe to ignore
backups/                            # Important - keep for rollback capability
data_stack/meltano/transactions.csv # Data file - should be in gitignore
feature-enhance-claude-prp.md       # Feature file - evaluate for archival
feature-mcp-server-integration.md   # Feature file - next work item
temp/                               # Temporary files - should be ignored
volumes/duckdb/                     # Docker volume - should be ignored
volumes/grafana/plugins/            # Docker volume - should be ignored
volumes/prometheus/                 # Docker volume - should be ignored
```

### Known Gotchas & Patterns
```python
# CRITICAL: Docker volumes contain runtime data
# Pattern: volumes/* should be in .gitignore but not the volume configs
# Example: Keep docker-compose.yml but ignore volumes/*/

# CRITICAL: Backup files are security-critical
# Pattern: Keep backups/ directory but evaluate contents
# Example: Security backup system created for rollback capability

# CRITICAL: Feature files may contain next work
# Pattern: Archive completed features, preserve active ones
# Example: feature-mcp-server-integration.md is next planned work
```

## Implementation Blueprint

### File Categorization Matrix
```yaml
CATEGORY_IMMEDIATE_DELETE:
  - "*.backup files (after verification)"
  - "temp/ directory contents"
  - "volumes/ runtime data"

CATEGORY_GITIGNORE_ADD:
  - "*.csv data files"
  - "volumes/*"
  - "temp/*"
  - "*.backup"
  - ".DS_Store"

CATEGORY_ARCHIVE:
  - "feature-enhance-claude-prp.md (completed work)"

CATEGORY_PRESERVE:
  - "backups/ (security system)"
  - "feature-mcp-server-integration.md (next work)"

CATEGORY_EVALUATE:
  - "temp/PRPs-agentic-eng/ (source materials)"
  - "temp/*.md (reports)"
```

### Task Sequence

```yaml
Task 1 - ANALYZE:
  ACTION: "Catalog and verify all untracked files"
  COMMANDS:
    - "git status --porcelain | grep '^??'"
    - "find . -name '*.backup' -type f"
    - "du -sh volumes/ temp/ backups/"
  VALIDATE: "Complete file inventory created"
  IF_FAIL: "Re-run discovery commands"

Task 2 - SECURE:
  ACTION: "Verify no sensitive data in untracked files"
  COMMANDS:
    - "grep -r 'password\\|secret\\|key\\|token' --include='*.md' --include='*.csv' ."
    - "find . -name '*.env*' -type f"
  VALIDATE: "No sensitive data found in untracked files"
  IF_FAIL: "Secure or remove files with sensitive data"

Task 3 - BACKUP_VERIFY:
  ACTION: "Verify backup system integrity"
  COMMANDS:
    - "ls -la backups/"
    - "cat backups/*/backup_metadata.json"
  VALIDATE: "Backup system verified functional"
  IF_FAIL: "Check backup system documentation"

Task 4 - GITIGNORE_UPDATE:
  ACTION: "Update .gitignore with proper patterns"
  PATTERNS:
    - "# Data files"
    - "*.csv"
    - "data_stack/meltano/transactions.csv"
    - ""
    - "# Docker volumes"
    - "volumes/*"
    - "!volumes/.gitkeep"
    - ""
    - "# Temporary files"
    - "temp/*"
    - "!temp/.gitkeep"
    - ""
    - "# Backup files"
    - "*.backup"
    - ""
    - "# System files"
    - ".DS_Store"
    - "Thumbs.db"
  VALIDATE: "git status shows reduced untracked files"
  IF_FAIL: "Check gitignore syntax and patterns"

Task 5 - ARCHIVE_COMPLETED:
  ACTION: "Archive completed feature files"
  OPERATIONS:
    - "mkdir -p PRPs/completed"
    - "mv feature-enhance-claude-prp.md PRPs/completed/"
  VALIDATE: "Completed features archived properly"
  IF_FAIL: "Check directory permissions"

Task 6 - PRESERVE_ACTIVE:
  ACTION: "Ensure active work is preserved"
  OPERATIONS:
    - "git add feature-mcp-server-integration.md"
    - "git add backups/"
  VALIDATE: "Important files staged for commit"
  IF_FAIL: "Check file existence and git status"

Task 7 - TEMP_CLEANUP:
  ACTION: "Clean temporary files while preserving reports"
  OPERATIONS:
    - "mkdir -p docs/reports"
    - "mv temp/*.md docs/reports/ || true"
    - "rm -rf temp/PRPs-agentic-eng/"
  VALIDATE: "Temp cleaned, reports preserved"
  IF_FAIL: "Check file permissions and paths"

Task 8 - VOLUME_CLEANUP:
  ACTION: "Clean Docker volumes but preserve structure"
  OPERATIONS:
    - "docker-compose down || true"
    - "rm -rf volumes/duckdb/* || true"
    - "rm -rf volumes/grafana/plugins/* || true"
    - "rm -rf volumes/prometheus/* || true"
    - "touch volumes/.gitkeep"
  VALIDATE: "Volume directories exist but are empty"
  IF_FAIL: "Check Docker status and permissions"

Task 9 - FINAL_COMMIT:
  ACTION: "Commit organized changes"
  OPERATIONS:
    - "git add .gitignore"
    - "git add PRPs/completed/"
    - "git add feature-mcp-server-integration.md"
    - "git add docs/reports/"
    - "git commit -m 'chore: organize repository and clean untracked files'"
  VALIDATE: "Clean git status achieved"
  IF_FAIL: "Check staged files and commit message"

Task 10 - VERIFICATION:
  ACTION: "Verify clean repository state"
  COMMANDS:
    - "git status"
    - "ls -la volumes/"
    - "ls -la temp/"
    - "du -sh ."
  VALIDATE: "Repository clean and organized"
  IF_FAIL: "Review remaining untracked files"
```

### Integration Points

```yaml
DOCKER:
  - action: "Stop services before volume cleanup"
  - command: "docker-compose down"
  - verify: "No running containers"

GIT:
  - action: "Update .gitignore before cleanup"
  - pattern: "Add patterns progressively"
  - verify: "git check-ignore works correctly"

BACKUP_SYSTEM:
  - action: "Preserve security backup capability"
  - location: "backups/ directory"
  - verify: "Rollback scripts functional"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Verify .gitignore syntax
git check-ignore --verbose volumes/test
git check-ignore --verbose temp/test

# Check for syntax errors
find . -name '.gitignore' -exec git check-ignore --stdin < {} \;
```

### Level 2: Unit Testing
```bash
# Test gitignore patterns
echo "test.csv" | git check-ignore --stdin
echo "volumes/data" | git check-ignore --stdin
echo "temp/file" | git check-ignore --stdin

# Test backup system
ls backups/*/rollback.sh
test -f backups/docker_compose_backup_*/backup_metadata.json
```

### Level 3: Integration Testing
```bash
# Test complete workflow
git status --porcelain | wc -l  # Should be minimal
docker-compose up -d --quiet-pull
sleep 10
docker-compose down
git status --porcelain | grep volumes || echo "Volumes properly ignored"
```

### Level 4: Creative Validation
```bash
# Test repository size optimization
du -sh . | awk '{print "Repository size: " $1}'

# Test git performance
time git status

# Verify no sensitive data tracked
git log --all --full-history -- '*.csv' '*.env*' | head -20
```

## Anti-Patterns to Avoid

- ❌ Don't delete backup files without verification
- ❌ Don't ignore files that are needed for system function
- ❌ Don't commit large data files or Docker volumes
- ❌ Don't remove work-in-progress features without archiving
- ❌ Don't modify .gitignore without testing patterns
- ❌ Don't clean volumes while Docker services are running

## Risk Assessment

### High Risk
- **Backup System**: Critical for rollback capability
- **Active Features**: Work in progress must be preserved
- **Docker Volumes**: May contain persistent data

### Medium Risk
- **Gitignore Patterns**: Could hide needed files
- **Temp Reports**: May contain valuable analysis

### Low Risk
- **Docker Runtime Data**: Can be regenerated
- **Backup Files**: Duplicates of tracked content

## Expected Outcomes

### Repository State
- Clean `git status` output
- Reduced repository size
- Proper file organization
- No sensitive data exposure

### Performance Improvements
- Faster git operations
- Cleaner directory listing
- Reduced disk usage
- Better developer experience

### Maintenance Benefits
- Clear separation of concerns
- Easier navigation
- Proper ignore patterns
- Archive of completed work

---

## Quality Checklist

- [ ] All untracked files categorized and resolved
- [ ] .gitignore patterns tested and functional
- [ ] Backup system integrity verified
- [ ] No sensitive data accidentally exposed
- [ ] Active work preserved and organized
- [ ] Docker volumes cleaned but structure maintained
- [ ] Git repository clean and optimized
- [ ] Documentation updated as needed
