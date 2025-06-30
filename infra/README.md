# Infrastructure as Code

This directory contains the Terraform infrastructure configuration for the Freelancer Data Stack project.

## Overview

The infrastructure is organized using Terraform modules and supports both local development and production environments with different backends:

- **Local Environment**: Uses local state file (`local.tfstate`)
- **Production Environment**: Uses remote S3 backend with DynamoDB locking

## Architecture

### Modules

1. **S3**: Data lake, artifacts, and logs buckets with lifecycle policies
2. **Snowflake**: Database, warehouse, schemas, users, roles, and file formats
3. **ECR**: Container repositories for all services with lifecycle policies
4. **ECS**: Fargate cluster, task definitions, services, and auto-scaling
5. **Secrets Manager**: Secure storage for credentials and API keys

### GitHub OIDC Integration

The infrastructure creates IAM roles and policies for GitHub Actions to deploy to AWS using OpenID Connect, eliminating the need for long-lived access keys.

## Prerequisites

### Required Tools

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [AWS CLI](https://aws.amazon.com/cli/) >= 2.0
- Make (for using the Makefile commands)

### AWS Setup

1. Configure AWS credentials:
   ```bash
   make setup-aws-credentials
   ```

2. Ensure your AWS account has the necessary permissions for:
   - S3, ECR, ECS, Secrets Manager, IAM
   - DynamoDB (for state locking in production)

### Snowflake Setup

1. Create a Snowflake account if you don't have one
2. Note your account identifier, username, and password
3. Ensure you have SYSADMIN role or equivalent permissions

## Quick Start

### 1. Local Development

```bash
# Check that all tools are installed
make check-tools

# Setup local secrets (edit the generated file with your credentials)
make setup-local-secrets

# Initialize and deploy to local environment
make deploy-local

# View outputs
make output-local
```

### 2. Production Deployment

```bash
# First-time production deployment (creates S3 backend)
make deploy-prod-first-time

# Subsequent deployments
make deploy-prod

# View outputs
make output-prod
```

## Configuration

### Environment Variables

#### Local Environment (`infra/terraform/environments/local/terraform.tfvars`)

Key configurations for local development:
- Smaller resource sizes
- Shorter retention periods
- Disabled versioning for cost savings

#### Production Environment (`infra/terraform/environments/prod/terraform.tfvars`)

Production-ready configurations:
- Production-sized resources
- Long retention periods
- Enhanced security and monitoring

### Secrets Management

Sensitive values should be stored in:
1. AWS Secrets Manager (recommended for production)
2. Environment variables
3. Terraform variable files (for development only, never commit to git)

## Available Commands

Run `make help` to see all available commands:

```bash
make help
```

### Key Commands

| Command | Description |
|---------|-------------|
| `make deploy-local` | Deploy to local environment |
| `make deploy-prod` | Deploy to production environment |
| `make plan-local` | Preview local changes |
| `make plan-prod` | Preview production changes |
| `make destroy-local` | Destroy local infrastructure |
| `make destroy-prod` | Destroy production infrastructure |
| `make validate` | Validate Terraform configuration |
| `make format` | Format Terraform files |
| `make status` | Show status of both environments |

## Backend Configuration

### Local Backend

Uses local state file for development:
```hcl
terraform {
  backend "local" {
    path = "local.tfstate"
  }
}
```

### Remote Backend (Production)

Uses S3 with DynamoDB locking:
```hcl
terraform {
  backend "s3" {
    bucket         = "freelancer-data-stack-terraform-state-prod-XXXXXXXX"
    key            = "terraform.tfstate"
    region         = "ca-central-1"
    dynamodb_table = "freelancer-data-stack-terraform-state-lock-prod"
    encrypt        = true
  }
}
```

## GitHub Actions Integration

### Setup Steps

1. Deploy to production:
   ```bash
   make deploy-prod
   ```

2. Get the GitHub OIDC role ARN:
   ```bash
   make output-prod
   ```

3. Configure GitHub repository secrets:
   ```bash
   make github-oidc-setup
   ```

### Required GitHub Secrets

- `AWS_REGION`: `ca-central-1`
- `AWS_ROLE_ARN`: Output from terraform (github_oidc_role_arn)
- `ECR_REGISTRY`: Your ECR registry URL

### Example GitHub Workflow

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
        aws-region: ${{ secrets.AWS_REGION }}
    
    - name: Login to Amazon ECR
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker image
      run: |
        docker build -t ${{ secrets.ECR_REGISTRY }}/freelancer-data-stack-api-prod:latest .
        docker push ${{ secrets.ECR_REGISTRY }}/freelancer-data-stack-api-prod:latest
```

## Security Considerations

### IAM Permissions

The infrastructure follows the principle of least privilege:
- GitHub OIDC role has minimal permissions for deployment
- ECS tasks have specific permissions for their functions
- Secrets are accessed through IAM roles, not embedded credentials

### Network Security

- ECS tasks run in private subnets where possible
- Security groups limit access to necessary ports
- All data in transit is encrypted

### Data Protection

- S3 buckets have encryption at rest
- Secrets Manager encrypts sensitive data
- Snowflake uses its native encryption

## Monitoring and Logging

### CloudWatch

- ECS services log to CloudWatch
- Retention periods configured per environment
- Log groups organized by service

### Cost Optimization

- Lifecycle policies for S3 and ECR
- Auto-scaling for ECS services
- Snowflake warehouse auto-suspend

## Troubleshooting

### Common Issues

1. **Terraform state lock**: If state is locked, wait for the lock to release or force unlock if necessary
2. **AWS permissions**: Ensure your AWS credentials have sufficient permissions
3. **Snowflake connectivity**: Verify your Snowflake credentials and network access
4. **Resource limits**: Check AWS service limits if resources fail to create

### Debug Commands

```bash
# Validate configuration
make validate

# Check status
make status

# View plan without applying
make plan-local  # or plan-prod

# Clean up temporary files
make clean
```

### Getting Help

1. Check the Terraform documentation
2. Review AWS service documentation
3. Check Snowflake provider documentation
4. Review the module source code for specific configurations

## Development Workflow

### Making Changes

1. Make changes to Terraform files
2. Format and validate:
   ```bash
   make lint
   ```
3. Test in local environment:
   ```bash
   make plan-local
   make deploy-local
   ```
4. If satisfied, deploy to production:
   ```bash
   make plan-prod
   make deploy-prod
   ```

### Adding New Resources

1. Create or modify the appropriate module
2. Update variables and outputs as needed
3. Test thoroughly in local environment
4. Update documentation
5. Deploy to production

## Cost Management

### Development

- Use local environment for development
- Destroy local resources when not needed:
  ```bash
  make destroy-local
  ```

### Production

- Monitor AWS costs regularly
- Review and optimize resource sizes
- Use lifecycle policies to manage storage costs
- Consider reserved instances for long-running services

## Backup and Disaster Recovery

### State Files

- Production state is stored in S3 with versioning
- DynamoDB provides state locking
- Regular backups of critical data

### Data Protection

- S3 lifecycle policies for long-term retention
- Snowflake time travel for data recovery
- Cross-region replication available if needed
