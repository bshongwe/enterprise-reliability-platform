# GCP Infrastructure

Terraform configuration for GCP resources (analytics, long-term metrics).

## Resources
- GKE cluster for analytics
- BigQuery dataset and tables
- Cloud Logging sink

## Usage
```bash
terraform init
terraform plan -var="gcp_project_id=YOUR_PROJECT"
terraform apply
```
