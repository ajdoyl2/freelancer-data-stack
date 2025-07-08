name: "Enhanced Claude PRP Integration with PRPs-agentic-eng"
description: |

## Purpose
Integrate the https://github.com/Wirasm/PRPs-agentic-eng project into the freelancer-data-stack to enhance Claude PRP creation and rules while preserving existing domain-specific functionality and data stack capabilities.

## Core Principles
1. **Preserve Domain Excellence**: Maintain all existing data stack commands and agent capabilities
2. **Security First**: Implement comprehensive backup and rollback strategies
3. **Intelligent Merging**: Combine rather than replace existing functionality
4. **Context Engineering**: Add AI documentation and enhanced context for better outcomes
5. **Global Rules**: Follow all rules in CLAUDE.md and project conventions

---

## Goal
Enhance the existing sophisticated PRP system in freelancer-data-stack by integrating PRPs-agentic-eng improvements while preserving all current domain-specific data stack functionality, resulting in a hybrid system that combines the best of both approaches.

## Why
- **Enhanced AI Success Rate**: PRPs-agentic-eng provides "one-pass implementation success" methodology
- **Structured Context Engineering**: Move from ad-hoc prompting to systematic context provision
- **Expanded Command Library**: Add 15 standardized commands to existing 24 domain-specific commands
- **Improved Templates**: Enhance existing templates with PRPs-agentic-eng validation loops
- **AI Documentation Structure**: Add PRPs/ai_docs/ for enhanced AI context
- **Proven Methodology**: Leverage workshop-tested PRP methodology for better outcomes

## What
Integrate PRPs-agentic-eng by following option 2 (clone and integrate) while intelligently merging with existing freelancer-data-stack PRP infrastructure, resulting in enhanced AI-driven development capabilities without losing domain expertise.

### Success Criteria
- [ ] All existing 24 .claude commands continue to function
- [ ] 15 new PRPs-agentic-eng commands successfully integrated
- [ ] Enhanced CLAUDE.md preserves project-specific rules
- [ ] Improved PRP templates maintain data stack patterns
- [ ] PRPs/ai_docs/ structure created for context engineering
- [ ] Security backup and rollback system implemented
- [ ] All validation gates pass successfully
- [ ] Cost optimization and data stack functionality preserved

## All Needed Context

### Documentation & References (list all context needed to implement the feature)
```yaml
# MUST READ - Include these in your context window
- url: https://github.com/Wirasm/PRPs-agentic-eng
  why: Main repository with integration instructions and enhanced PRP templates

- url: https://github.com/Wirasm/PRPs-agentic-eng/blob/main/README.md
  why: Option 2 integration instructions and project structure details

- url: https://github.com/Wirasm/PRPs-agentic-eng/tree/main/.claude/commands
  why: 15 standardized Claude commands to integrate with existing 24 commands

- url: https://github.com/Wirasm/PRPs-agentic-eng/tree/main/PRPs/templates
  why: Enhanced PRP templates with validation loops and context engineering

- url: https://www.anthropic.com/engineering/claude-code-best-practices
  why: Official Claude Code best practices for AI-driven development

- url: https://github.com/coleam00/context-engineering-intro
  why: Context engineering principles - 10x better than prompt engineering

- file: .claude/commands/
  why: Existing 24 domain-specific commands that must be preserved

- file: PRPs/templates/prp_base.md
  why: Current template pattern to enhance rather than replace

- file: CLAUDE.md
  why: Project-specific rules and conventions that must be merged intelligently

- file: pyproject.toml
  why: Poetry dependency management patterns to follow

- docfile: PRPs/ai_docs/prp-agentic-eng-integration.md
  why: Integration methodology and security considerations documentation

- docfile: PRPs/ai_docs/claude-prp-best-practices.md
  why: Research findings on Claude PRP optimization techniques
```

### Current Codebase tree (existing PRP infrastructure)
```bash
freelancer-data-stack/
├── .claude/
│   ├── commands/                 # 24 data stack specific commands
│   │   ├── ai-agent-task.md
│   │   ├── deploy-data-stack.md
│   │   ├── monitor-data-stack.md
│   │   ├── generate-prp.md
│   │   ├── execute-prp.md
│   │   └── ... (19 more domain commands)
│   └── settings.local.json
├── PRPs/
│   ├── templates/
│   │   ├── prp_base.md          # Sophisticated existing template
│   │   ├── prp-planning.md
│   │   ├── prp-test.md
│   │   └── prp-validate.md
│   ├── EXAMPLE_multi_agent_prp.md
│   └── ... (5 existing PRPs)
├── CLAUDE.md                    # Project-specific AI guidelines
├── agents/                      # AI agent infrastructure
├── tools/                       # Data stack tool implementations
└── data_stack/                  # Modern data stack components
```

### Desired Codebase tree with files to be added and responsibility of file
```bash
freelancer-data-stack/
├── .claude/
│   ├── commands/                 # 39 total commands (24 existing + 15 new)
│   │   ├── [PRESERVE] ai-agent-task.md
│   │   ├── [PRESERVE] deploy-data-stack.md
│   │   ├── [PRESERVE] monitor-data-stack.md
│   │   ├── [ADD] conflict-resolver-general.md    # General conflict resolution
│   │   ├── [ADD] conflict-resolver-specific.md   # Specific conflict resolution
│   │   ├── [ADD] planning-create.md              # Visual planning with Mermaid
│   │   ├── [ADD] smart-commit.md                 # Intelligent commit workflows
│   │   ├── [ADD] review-general.md               # Code review automation
│   │   ├── [ADD] spec-create-adv.md              # Advanced specification creation
│   │   └── ... (all others preserved + new ones)
│   └── settings.local.json
├── PRPs/
│   ├── ai_docs/                  # NEW: AI documentation for context
│   │   ├── prp-agentic-eng-integration.md       # Integration methodology
│   │   ├── claude-prp-best-practices.md         # Best practices research
│   │   ├── data-stack-patterns.md               # Domain-specific patterns
│   │   └── security-considerations.md           # Security guidelines
│   ├── templates/
│   │   ├── [ENHANCE] prp_base.md               # Enhanced with validation loops
│   │   ├── [ADD] prp_planning_base.md          # Visual planning template
│   │   ├── [ADD] prp_spec.md                   # Technical specification template
│   │   ├── [PRESERVE] prp-planning.md          # Existing data stack template
│   │   └── [PRESERVE] prp-test.md              # Existing test template
│   ├── scripts/                  # NEW: PRP utility scripts
│   │   ├── backup_prp_system.py               # Backup current PRP system
│   │   ├── merge_commands.py                  # Intelligent command merging
│   │   └── validate_integration.py           # Integration validation
│   └── completed/                # NEW: Archive for completed PRPs
├── [ENHANCE] CLAUDE.md            # Enhanced with PRPs-agentic-eng improvements
├── backups/                      # NEW: Security backup system
│   └── prp_integration_backup_YYYYMMDD/
└── [PRESERVE] agents/, tools/, data_stack/    # All existing functionality
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: Project uses Poetry with dependency groups - maintain structure
# Example: PRPs-agentic-eng uses UV, but this project uses Poetry

# CRITICAL: 500-line file limit enforced - split large files
# Example: CLAUDE.md may need modular organization after enhancement

# CRITICAL: Existing 24 .claude commands are domain-specific and must be preserved
# Example: deploy-data-stack.md contains AI agent orchestration that can't be lost

# CRITICAL: Current CLAUDE.md has project-specific rules that must be merged
# Example: "Use venv_linux" and data stack specific testing patterns

# CRITICAL: Existing PRP templates use information-dense keywords
# Example: MIRROR, COPY, ADD, MODIFY patterns must be preserved

# CRITICAL: Security implications of replacing CLAUDE.md
# Example: Must implement backup and rollback strategy before changes
```

## Implementation Blueprint

### Data models and structure

Create AI documentation structure and backup systems to ensure safe integration.
```python
# Security and backup models
class BackupMetadata(BaseModel):
    backup_timestamp: datetime
    original_files: List[str]
    backup_location: Path
    rollback_script: str
    validation_checksum: str

# Command integration models
class CommandIntegration(BaseModel):
    existing_commands: List[str]
    new_commands: List[str]
    conflict_resolution: Dict[str, str]
    merged_commands: List[str]

# Template enhancement models
class TemplateEnhancement(BaseModel):
    original_template: str
    enhancements: List[str]
    preserved_patterns: List[str]
    validation_gates: List[str]
```

### list of tasks to be completed to fullfill the PRP in the order they should be completed

```yaml
Task 1: SECURITY_BACKUP_SYSTEM
CREATE scripts/backup_current_prp_system.py:
  - BACKUP all current .claude/commands/ files with metadata
  - BACKUP current CLAUDE.md with git history
  - BACKUP current PRPs/templates/ directory
  - CREATE automated rollback script with validation
  - GENERATE backup integrity checksums

Task 2: CLONE_PRPS_AGENTIC_ENG
EXECUTE repository cloning:
  - GIT clone https://github.com/Wirasm/PRPs-agentic-eng.git to temp directory
  - ANALYZE structure and identify files for integration
  - SECURITY scan cloned repository for vulnerabilities
  - EXTRACT integration components while preserving project structure

Task 3: CREATE_AI_DOCS_STRUCTURE
CREATE PRPs/ai_docs/ directory:
  - MIGRATE research findings into structured documentation
  - CREATE prp-agentic-eng-integration.md with methodology
  - CREATE claude-prp-best-practices.md with optimization techniques
  - CREATE data-stack-patterns.md with domain-specific context
  - CREATE security-considerations.md with safety guidelines

Task 4: INTELLIGENT_COMMAND_MERGING
CREATE scripts/merge_commands.py:
  - ANALYZE existing 24 .claude commands for functionality mapping
  - IDENTIFY 15 new commands from PRPs-agentic-eng
  - RESOLVE conflicts between overlapping commands
  - MERGE complementary commands preserving domain specificity
  - VALIDATE all commands maintain existing functionality

Task 5: ENHANCE_CLAUDE_MD
MODIFY CLAUDE.md with intelligent merging:
  - PRESERVE all project-specific rules and conventions
  - INJECT PRPs-agentic-eng improvements and methodology
  - MAINTAIN data stack specific guidelines
  - ADD context engineering principles
  - PRESERVE AI behavior rules and testing requirements

Task 6: ENHANCE_PRP_TEMPLATES
MODIFY PRPs/templates/ with validation loops:
  - ENHANCE prp_base.md with PRPs-agentic-eng validation gates
  - ADD prp_planning_base.md for visual planning with Mermaid
  - ADD prp_spec.md for technical specifications
  - PRESERVE existing data stack specific patterns
  - MAINTAIN information-dense keyword approach

Task 7: INTEGRATE_UTILITY_SCRIPTS
CREATE PRPs/scripts/ directory:
  - ADD PRP utility scripts from PRPs-agentic-eng
  - ADAPT scripts for data stack project structure
  - CREATE validation scripts for integration testing
  - IMPLEMENT quality scoring mechanisms

Task 8: COMPREHENSIVE_VALIDATION
CREATE scripts/validate_integration.py:
  - TEST all existing 24 commands continue to function
  - VALIDATE 15 new commands integrate properly
  - VERIFY enhanced templates work with existing agents
  - CHECK enhanced CLAUDE.md maintains project compliance
  - EXECUTE end-to-end PRP workflow testing

Task 9: DOCUMENTATION_UPDATE
UPDATE project documentation:
  - MODIFY README.md to reflect enhanced PRP capabilities
  - UPDATE .claude/commands/ documentation
  - CREATE integration guide for team adoption
  - DOCUMENT rollback procedures
```

### Per task pseudocode as needed added to each task

```python
# Task 1: Security Backup System
class PRPBackupSystem:
    def create_backup(self) -> BackupMetadata:
        # PATTERN: Follow existing backup patterns in scripts/backup_current_config.py
        backup_dir = Path(f"backups/prp_integration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        backup_dir.mkdir(parents=True, exist_ok=True)

        # CRITICAL: Generate checksums for integrity validation
        files_to_backup = [
            ".claude/commands/",
            "CLAUDE.md",
            "PRPs/templates/",
            "pyproject.toml"
        ]

        # PATTERN: Use existing git history preservation
        for file_path in files_to_backup:
            shutil.copy2(file_path, backup_dir / file_path)
            checksum = hashlib.sha256(Path(file_path).read_bytes()).hexdigest()

        # CRITICAL: Create automated rollback script
        rollback_script = self._generate_rollback_script(backup_dir)

        return BackupMetadata(
            backup_timestamp=datetime.now(),
            backup_location=backup_dir,
            rollback_script=rollback_script
        )

# Task 4: Intelligent Command Merging
class CommandMerger:
    def merge_commands(self, existing_commands: List[str], new_commands: List[str]) -> Dict[str, str]:
        # PATTERN: Preserve domain-specific functionality
        domain_commands = [
            "ai-agent-task.md",
            "deploy-data-stack.md",
            "monitor-data-stack.md",
            "troubleshoot-stack.md"
        ]

        # CRITICAL: Map functionality to avoid conflicts
        command_mapping = {}
        for existing_cmd in existing_commands:
            if existing_cmd in domain_commands:
                command_mapping[existing_cmd] = "PRESERVE_EXACT"
            else:
                # Check for enhancement opportunities
                enhancement = self._find_enhancement_opportunity(existing_cmd, new_commands)
                command_mapping[existing_cmd] = enhancement or "PRESERVE"

        return command_mapping

# Task 5: CLAUDE.md Enhancement
class CLAUDEEnhancer:
    def enhance_claude_md(self, current_claude: str, enhancements: str) -> str:
        # PATTERN: Intelligent section merging preserving project rules
        project_sections = self._extract_project_sections(current_claude)
        enhancement_sections = self._extract_enhancement_sections(enhancements)

        # CRITICAL: Preserve project-specific rules
        preserved_rules = [
            "Use venv_linux",
            "500-line file limit",
            "Data stack specific testing patterns",
            "AI agent behavior rules"
        ]

        # GOTCHA: Merge without losing domain expertise
        merged_content = self._intelligent_merge(project_sections, enhancement_sections, preserved_rules)

        return merged_content
```

### Integration Points
```yaml
BACKUP_SYSTEM:
  - location: "backups/prp_integration_backup_YYYYMMDD/"
  - rollback: "backups/prp_integration_backup_YYYYMMDD/rollback.sh"
  - validation: "scripts/validate_backup.py"

COMMAND_INTEGRATION:
  - existing: ".claude/commands/ (24 commands)"
  - new: "temp/PRPs-agentic-eng/.claude/commands/ (15 commands)"
  - output: ".claude/commands/ (39 merged commands)"

TEMPLATE_ENHANCEMENT:
  - base: "PRPs/templates/prp_base.md"
  - enhancements: "PRPs-agentic-eng validation loops + context engineering"
  - output: "Enhanced prp_base.md with preserved data stack patterns"

AI_DOCUMENTATION:
  - add: "PRPs/ai_docs/ directory"
  - content: "Integration methodology, best practices, domain patterns"
  - purpose: "Enhanced context for AI agents"

SECURITY_VALIDATION:
  - scan: "Static analysis of PRPs-agentic-eng code"
  - backup: "Comprehensive backup with rollback capability"
  - testing: "End-to-end validation of all functionality"
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

### Level 2: Security Validation
```bash
# CRITICAL: Security scanning before integration
bandit -r scripts/ PRPs/scripts/   # Security vulnerability scanning
safety check                      # Dependency vulnerability check
git secrets --scan                # Secret scanning

# Backup system validation
python scripts/backup_current_prp_system.py --dry-run
python scripts/validate_backup.py

# Expected: All security checks pass, backup system functional
```

### Level 3: Functional Testing
```bash
# Test existing functionality preservation
python scripts/validate_integration.py --test-existing-commands
python scripts/validate_integration.py --test-templates
python scripts/validate_integration.py --test-agents

# Test new functionality integration
python scripts/validate_integration.py --test-new-commands
python scripts/validate_integration.py --test-enhanced-templates

# Test data stack specific workflows
uv run pytest tests/test_prp_integration.py -v
uv run pytest tests/test_data_stack_workflows.py -v

# Expected: All tests pass, existing functionality preserved, new functionality working
```

### Level 4: End-to-End Integration Test
```bash
# Test complete PRP workflow with enhanced system
.claude/commands/generate-prp.md "Test integration workflow"
.claude/commands/execute-prp.md "PRPs/test-integration-prp.md"

# Test data stack specific workflows
.claude/commands/deploy-data-stack.md --validate-only
.claude/commands/monitor-data-stack.md --health-check

# Test new PRPs-agentic-eng workflows
.claude/commands/planning-create.md "Test planning workflow"
.claude/commands/conflict-resolver-general.md --dry-run

# Expected: All workflows functional, no regression in data stack capabilities
```

### Level 5: Rollback Validation
```bash
# Test rollback capability
cd backups/prp_integration_backup_*/
chmod +x rollback.sh
./rollback.sh --dry-run

# Validate rollback restores original state
python scripts/validate_backup.py --verify-rollback

# Expected: Rollback system functional, can restore original state
```

## Final validation Checklist
- [ ] All security scans pass: `bandit -r scripts/ && safety check`
- [ ] No linting errors: `ruff check . && markdownlint .claude/commands/*.md`
- [ ] No type errors: `mypy scripts/`
- [ ] Backup system functional: `python scripts/backup_current_prp_system.py --dry-run`
- [ ] All existing commands work: `python scripts/validate_integration.py --test-existing`
- [ ] New commands integrated: `python scripts/validate_integration.py --test-new`
- [ ] Enhanced templates functional: Test PRP generation workflow
- [ ] Data stack workflows preserved: Test deploy/monitor/troubleshoot commands
- [ ] AI agents work with enhanced system: Test agent interactions
- [ ] Documentation updated: README.md reflects new capabilities
- [ ] Rollback system tested: Can restore original state if needed
- [ ] End-to-end workflow successful: Complete PRP creation and execution cycle

---

## Anti-Patterns to Avoid
- ❌ Don't replace domain-specific commands with generic ones
- ❌ Don't lose existing data stack functionality for new features
- ❌ Don't skip security validation because "it's a trusted repo"
- ❌ Don't merge files without comprehensive backup strategy
- ❌ Don't ignore existing project conventions and patterns
- ❌ Don't assume PRPs-agentic-eng patterns work without adaptation
- ❌ Don't skip testing of existing functionality after integration
- ❌ Don't hardcode paths that should be relative to project structure

## Quality Assessment
**Confidence Level for One-Pass Implementation Success: 9/10**

**Strengths:**
- Comprehensive research conducted on both codebases
- Security-first approach with backup and rollback
- Preserves existing functionality while adding enhancements
- Detailed validation gates with executable commands
- Rich context provided for AI implementation
- Clear task breakdown with specific action verbs

**Risk Mitigation:**
- Extensive backup system prevents data loss
- Security scanning catches vulnerabilities
- Progressive validation ensures quality at each step
- Rollback capability provides safety net
- Domain expertise preservation maintains project value

**Success Factors:**
- Builds on existing sophisticated PRP infrastructure
- Leverages proven PRPs-agentic-eng methodology
- Maintains data stack domain specialization
- Comprehensive context engineering approach
- Security and quality validation throughout process
