# Oracle Cloud Infrastructure (OCI)

Terraform configuration for OCI resources (ledger, regulated workloads).

## Resources
- OKE cluster for ledger-service
- Autonomous Database for ledger data
- VCN with subnets

## Usage
```bash
terraform init
terraform plan -var="oci_compartment_id=YOUR_COMPARTMENT_OCID"
terraform apply
```
