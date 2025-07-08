name: "Docker Compose Credentials Migration PRP - Security Hardening & Warning Cleanup"
description: |
  Complete migration of hardcoded credentials to environment variables with strong password generation,
  Docker Compose warning cleanup, and comprehensive service validation.

---

## Goal
Migrate all hardcoded usernames and passwords in Docker Compose configuration to secure environment variables with strong password generation (using ajdoyle as default username), clean up all Docker Compose warnings, and ensure all services continue to function properly after the migration.

## Why
- **Security Enhancement**: Eliminate hardcoded credentials that pose security risks in production
- **GitHub Codespaces Compatibility**: Prepare for future GitHub Codespaces deployment with proper secret management
- **CI/CD Pipeline Readiness**: Enable secure CI/CD deployment with proper credential management
- **Production Compliance**: Meet security best practices for containerized deployments
- **Maintainability**: Centralize credential management for easier updates and rotation
- **Warning Cleanup**: Remove deprecation warnings and configuration issues

## What
Transform the current Docker Compose configuration from hardcoded credentials to a secure, environment-variable-based system with:
- Strong password generation for all services
- Standardized environment variable naming
- Comprehensive .env file with secure defaults
- Docker Compose warning elimination
- Service validation and health checks
- Rollback capabilities

### Success Criteria
- [ ] All hardcoded credentials migrated to environment variables
- [ ] Strong passwords generated for all services (ajdoyle as default username)
- [ ] All Docker Compose warnings eliminated
- [ ] All services start successfully with new credentials
- [ ] Service health checks pass
- [ ] End-to-end pipeline validation passes
- [ ] .env.example file created with secure defaults
- [ ] Rollback documentation provided

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/
  why: Official Docker Compose environment variable setup methods

- url: https://docs.docker.com/compose/how-tos/environment-variables/envvars-precedence/
  why: Understanding precedence order for environment variables

- url: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
  why: Variable interpolation syntax and default values

- url: https://docs.docker.com/compose/how-tos/environment-variables/best-practices/
  why: Security best practices for environment variables

- url: https://docs.docker.com/compose/how-tos/use-secrets/
  why: Docker secrets for production deployments

- url: https://docs.github.com/en/codespaces/managing-codespaces-for-your-organization/managing-development-environment-secrets-for-your-repository-or-organization
  why: GitHub Codespaces secret management

- file: docker-compose.yml
  why: Main configuration file with all hardcoded credentials

- file: scripts/validate_pipeline.py
  why: Existing validation patterns for end-to-end testing

- file: scripts/deploy_stack.py
  why: Deployment automation patterns

- file: tests/test_data_stack_engineer.py
  why: Testing patterns for service validation
```

### Current Codebase Context

#### **Critical Hardcoded Credentials Found (Complete Analysis)**
```yaml
# PostgreSQL Service (HIGH PRIORITY)
POSTGRES_USER: "postgres" # HARDCODED - needs migration
POSTGRES_PASSWORD: "${POSTGRES_PASSWORD:-postgres}" # INSECURE FALLBACK

# Airflow Services (CRITICAL SECURITY RISK)
AIRFLOW_USERNAME: "${AIRFLOW_USERNAME:-admin}" # INSECURE FALLBACK
AIRFLOW_PASSWORD: "${AIRFLOW_PASSWORD:-admin}" # CRITICAL: admin/admin

# Grafana Service (CRITICAL SECURITY RISK)
GF_SECURITY_ADMIN_USER: "admin" # HARDCODED
GF_SECURITY_ADMIN_PASSWORD: "${GRAFANA_PASSWORD:-admin}" # CRITICAL: admin/admin

# Neo4j Service (SECURITY RISK)
NEO4J_AUTH: "neo4j/${NEO4J_PASSWORD:-datahub}" # HARDCODED USERNAME

# DataHub Services
DATAHUB_SECRET: "${DATAHUB_SECRET:-YouMustChangeThisSecretKey}" # INSECURE FALLBACK

# Metabase Service
MB_DB_USER: "postgres" # HARDCODED
MB_ADMIN_EMAIL: "admin@datastack.local" # HARDCODED

# MCP Server
SECRET_KEY: "${SECRET_KEY:-your-secret-key-here}" # INSECURE FALLBACK
```

#### **Docker Compose Warnings Identified**
```yaml
# Version Deprecation (CONFIRMED)
WARNING: "The attribute 'version' is obsolete, it will be ignored"
LOCATION: Line 1 in docker-compose.yml and docker-compose.agents.yml
FIX: Remove version declarations

# Missing Environment Variables (CONFIRMED)
WARNING: "The 'DATAHUB_TOKEN' variable is not set. Defaulting to a blank string."
LOCATION: Line 617 in docker-compose.yml
FIX: Add DATAHUB_TOKEN to environment variables

# Port Conflicts (CRITICAL)
CONFLICT: Both airflow-webserver and datahub-gms use port 8080
LOCATION: Lines 136 and 279 in docker-compose.yml
FIX: Change DataHub GMS to port 8081

# Missing Health Checks
SERVICES: zookeeper, kafka, schema-registry, elasticsearch, neo4j
IMPACT: Service dependency issues
FIX: Add appropriate health checks
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: Docker Compose V2 syntax requirements
# - Remove version declarations (now obsolete)
# - Use 'docker compose' not 'docker-compose'
# - Environment variable precedence: CLI > shell > compose environment > env_file

# CRITICAL: Password generation requirements
# - Use secrets.token_urlsafe() for URL-safe tokens
# - Use secrets.token_hex() for hex-encoded passwords
# - Minimum 32 characters for production passwords
# - Special characters may cause issues with some services (avoid for database passwords)

# CRITICAL: Service startup dependencies
# - PostgreSQL must be healthy before dependent services start
# - Airflow services have specific startup order requirements
# - DataHub services require Kafka and Elasticsearch to be ready

# CRITICAL: Environment variable naming
# - Use consistent PREFIX_COMPONENT_SETTING pattern
# - Avoid spaces and special characters in variable names
# - Use uppercase for environment variables

# GOTCHA: Service restarts with new credentials
# - Some services cache credentials and need full restart
# - Airflow may need database reinitialization
# - DataHub may need metadata refresh
```

## Implementation Blueprint

### Data Models and Structure
```python
# Environment Variable Structure
class CredentialConfig:
    """Standard credential configuration structure"""
    username: str = "ajdoyle"  # Default username
    password: str  # Generated secure password
    database: str = None  # Optional database name
    host: str = "localhost"  # Default host
    port: int  # Service-specific port

# Password Generation Configuration
class PasswordConfig:
    length: int = 32  # Minimum secure length
    use_special_chars: bool = False  # Avoid for database compatibility
    use_url_safe: bool = True  # URL-safe encoding
```

### List of Tasks to Complete (In Order)

```yaml
Task 1: CREATE_PASSWORD_GENERATION_SCRIPT
CREATE scripts/generate_env_passwords.py:
  - IMPORT secrets, string, argparse modules
  - IMPLEMENT generate_secure_password() function
  - IMPLEMENT validate_password_strength() function
  - IMPLEMENT update_env_file() function
  - OUTPUT formatted .env file with all required variables

Task 2: BACKUP_CURRENT_CONFIGURATION
CREATE scripts/backup_current_config.py:
  - COPY current docker-compose.yml to docker-compose.yml.backup
  - DOCUMENT current credential mapping
  - CREATE rollback script

Task 3: MIGRATE_POSTGRESQL_CREDENTIALS
MODIFY docker-compose.yml:
  - FIND pattern: "POSTGRES_USER: postgres"
  - REPLACE with: "POSTGRES_USER: ${POSTGRES_USER:-ajdoyle}"
  - FIND pattern: "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}"
  - REPLACE with: "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"
  - UPDATE all dependent services using PostgreSQL credentials

Task 4: MIGRATE_AIRFLOW_CREDENTIALS
MODIFY docker-compose.yml:
  - FIND pattern: "AIRFLOW_USERNAME: ${AIRFLOW_USERNAME:-admin}"
  - REPLACE with: "AIRFLOW_USERNAME: ${AIRFLOW_USERNAME:-ajdoyle}"
  - FIND pattern: "AIRFLOW_PASSWORD: ${AIRFLOW_PASSWORD:-admin}"
  - REPLACE with: "AIRFLOW_PASSWORD: ${AIRFLOW_PASSWORD}"
  - UPDATE all Airflow services (webserver, scheduler, worker, flower)

Task 5: MIGRATE_GRAFANA_CREDENTIALS
MODIFY docker-compose.yml:
  - FIND pattern: "GF_SECURITY_ADMIN_USER: admin"
  - REPLACE with: "GF_SECURITY_ADMIN_USER: ${GRAFANA_USERNAME:-ajdoyle}"
  - FIND pattern: "GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}"
  - REPLACE with: "GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}"

Task 6: MIGRATE_NEO4J_CREDENTIALS
MODIFY docker-compose.yml:
  - FIND pattern: "NEO4J_AUTH: neo4j/${NEO4J_PASSWORD:-datahub}"
  - REPLACE with: "NEO4J_AUTH: ${NEO4J_USERNAME:-ajdoyle}/${NEO4J_PASSWORD}"
  - UPDATE DataHub services referencing Neo4j credentials

Task 7: MIGRATE_REMAINING_SERVICES
MODIFY docker-compose.yml:
  - UPDATE Metabase credentials (MB_DB_USER, MB_ADMIN_EMAIL)
  - UPDATE DataHub secret configuration
  - UPDATE MCP Server secret configuration
  - UPDATE any remaining hardcoded credentials

Task 8: FIX_DOCKER_COMPOSE_WARNINGS
MODIFY docker-compose.yml and docker-compose.agents.yml:
  - REMOVE version declarations from both files
  - FIX port conflict: change DataHub GMS to port 8081
  - ADD missing environment variables (DATAHUB_TOKEN)
  - ADD health checks for missing services

Task 9: CREATE_ENVIRONMENT_FILES
CREATE .env.example:
  - INCLUDE all required environment variables
  - USE secure placeholder values
  - ADD documentation comments
  - EXCLUDE from git (.gitignore)

Task 10: VALIDATE_CONFIGURATION
RUN validation scripts:
  - EXECUTE docker-compose config validation
  - EXECUTE service health checks
  - RUN end-to-end pipeline validation
  - VERIFY all services start properly
```

### Per Task Pseudocode

```python
# Task 1: Password Generation Script
def generate_secure_password(length: int = 32, use_special: bool = False) -> str:
    """Generate cryptographically secure password"""
    # PATTERN: Use secrets module for cryptographic security
    if use_special:
        # GOTCHA: Some services don't handle special chars well
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
    else:
        # SAFE: Alphanumeric only for database compatibility
        chars = string.ascii_letters + string.digits

    # CRITICAL: Use secrets.choice for cryptographic randomness
    password = ''.join(secrets.choice(chars) for _ in range(length))

    # VALIDATION: Ensure password meets complexity requirements
    if not validate_password_strength(password):
        return generate_secure_password(length, use_special)

    return password

# Task 3-7: Credential Migration Pattern
def migrate_service_credentials(service_name: str, compose_file: str):
    """Standard pattern for credential migration"""
    # PATTERN: Read current configuration
    with open(compose_file, 'r') as f:
        content = f.read()

    # PATTERN: Replace hardcoded values with environment variables
    replacements = {
        f'{service_name}_USER: "hardcoded_user"': f'{service_name}_USER: ${{{service_name}_USER:-ajdoyle}}',
        f'{service_name}_PASSWORD: "${{VAR:-default}}"': f'{service_name}_PASSWORD: ${{{service_name}_PASSWORD}}'
    }

    # CRITICAL: Preserve existing environment variable patterns
    for old, new in replacements.items():
        content = content.replace(old, new)

    # VALIDATION: Ensure syntax is still valid
    validate_compose_syntax(content)

    # ATOMIC: Write updated configuration
    with open(compose_file, 'w') as f:
        f.write(content)

# Task 8: Warning Cleanup Pattern
def fix_compose_warnings(compose_file: str):
    """Fix all identified Docker Compose warnings"""
    # PATTERN: Read and parse YAML
    with open(compose_file, 'r') as f:
        content = f.read()

    # FIX: Remove obsolete version declaration
    content = re.sub(r'^version:\s*[\'"]?[\d\.]+[\'"]?\s*\n', '', content, flags=re.MULTILINE)

    # FIX: Port conflicts
    content = content.replace('"8080:8080"  # datahub-gms', '"8081:8080"  # datahub-gms')

    # VALIDATION: Ensure no syntax errors
    validate_compose_syntax(content)

    return content
```

### Integration Points
```yaml
DATABASE:
  - migration: "Update all database connection strings to use environment variables"
  - validation: "Ensure all dependent services can connect with new credentials"

CONFIG:
  - add to: .env
  - pattern: "SERVICE_USERNAME=ajdoyle"
  - pattern: "SERVICE_PASSWORD=<generated>"

SECURITY:
  - add to: .gitignore
  - pattern: ".env*"
  - exclude: ".env.example"

VALIDATION:
  - add to: scripts/validate_pipeline.py
  - pattern: "Credential validation checks"
  - include: "Service connectivity tests"
```

## Validation Loop

### Level 1: Docker Compose Validation
```bash
# Run these FIRST - fix any errors before proceeding
docker-compose config --quiet                 # Validate syntax
docker-compose config 2>&1 | grep -i warning  # Check for warnings
docker-compose ps --services --filter status=running  # Check running services

# Expected: No syntax errors, no warnings, all services listed
```

### Level 2: Service Health Checks
```bash
# Test each service individually
docker-compose up postgres -d
docker-compose exec postgres pg_isready -U ${POSTGRES_USER}

docker-compose up airflow-webserver -d
curl -f http://localhost:8080/health || echo "Health check failed"

docker-compose up grafana -d
curl -f -u ${GRAFANA_USERNAME}:${GRAFANA_PASSWORD} http://localhost:3000/api/health

# Expected: All services healthy, no connection errors
```

### Level 3: End-to-End Pipeline Validation
```bash
# Use existing validation script
python scripts/validate_pipeline.py --verbose --data-quality-threshold=0.85

# Expected: All 10 validation categories pass
# - Source data validation
# - Meltano ELT validation
# - dbt transformation validation
# - Data quality metrics
# - Schema compliance
# - Business logic validation
# - Performance benchmarks
# - Monitoring validation
```

### Level 4: Credential Security Validation
```bash
# Validate password strength
python scripts/validate_credentials.py --check-strength

# Validate no hardcoded secrets
grep -r "password.*=" docker-compose.yml | grep -v "\${" || echo "No hardcoded passwords found"

# Validate environment variable usage
docker-compose config | grep -E "(USERNAME|PASSWORD|SECRET)" | grep -v "\${" || echo "All credentials use environment variables"

# Expected: Strong passwords, no hardcoded secrets, all variables properly referenced
```

## Final Validation Checklist
- [ ] All tests pass: `python scripts/validate_pipeline.py --verbose`
- [ ] No Docker warnings: `docker-compose config 2>&1 | grep -i warning`
- [ ] All services start: `docker-compose up -d && docker-compose ps`
- [ ] Service health checks: `docker-compose exec postgres pg_isready -U ${POSTGRES_USER}`
- [ ] Password strength validated: `python scripts/validate_credentials.py --check-strength`
- [ ] No hardcoded credentials: `grep -r "password.*=" docker-compose.yml | grep -v "\${"`
- [ ] .env.example created with secure defaults
- [ ] Rollback procedure documented and tested
- [ ] All environment variables properly set in .env file

## Security Considerations
- Use secrets.token_urlsafe() for URL-safe password generation
- Minimum 32-character passwords for production
- Default username "ajdoyle" as specified
- No hardcoded fallback passwords
- Proper .gitignore configuration for .env files
- Docker secrets recommended for production deployment

## Rollback Strategy
```bash
# If issues occur, restore from backup
cp docker-compose.yml.backup docker-compose.yml
docker-compose down
docker-compose up -d
```

---

## Anti-Patterns to Avoid
- ❌ Don't use weak fallback passwords (admin/admin, postgres/postgres)
- ❌ Don't commit .env files to version control
- ❌ Don't use special characters in database passwords (compatibility issues)
- ❌ Don't skip service health validation after credential changes
- ❌ Don't ignore Docker Compose warnings
- ❌ Don't use synchronous operations in async contexts

**Confidence Score: 9/10** - This PRP provides comprehensive context, specific implementation details, and robust validation loops for successful one-pass implementation.
