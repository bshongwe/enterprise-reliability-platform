# AWS Infrastructure

Terraform configuration for AWS resources (core payments, event ingestion).

## Resources
- EKS cluster for payments-api
- RDS PostgreSQL for payment data
- EventBridge for event ingestion
- VPC with public/private subnets
- KMS for encryption

## Usage
```bash
terraform init
terraform plan
terraform apply
```
