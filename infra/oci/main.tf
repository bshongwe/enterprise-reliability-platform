terraform {
  required_version = ">= 1.0"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
}

provider "oci" {
  region = var.oci_region
}

# OKE Cluster for ledger
resource "oci_containerengine_cluster" "main" {
  compartment_id     = var.oci_compartment_id
  kubernetes_version = "v1.28.2"
  name               = "${var.project_name}-oke"
  vcn_id             = oci_core_vcn.main.id

  options {
    service_lb_subnet_ids = [oci_core_subnet.lb.id]
  }
}

resource "oci_containerengine_node_pool" "main" {
  cluster_id         = oci_containerengine_cluster.main.id
  compartment_id     = var.oci_compartment_id
  kubernetes_version = "v1.28.2"
  name               = "${var.project_name}-node-pool"
  node_shape         = "VM.Standard.E4.Flex"

  node_config_details {
    size = 2
    placement_configs {
      availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
      subnet_id           = oci_core_subnet.nodes.id
    }
  }

  node_shape_config {
    memory_in_gbs = 16
    ocpus         = 2
  }
}

# VCN
resource "oci_core_vcn" "main" {
  compartment_id = var.oci_compartment_id
  cidr_blocks    = ["10.1.0.0/16"]
  display_name   = "${var.project_name}-vcn"
}

resource "oci_core_subnet" "lb" {
  compartment_id = var.oci_compartment_id
  vcn_id         = oci_core_vcn.main.id
  cidr_block     = "10.1.1.0/24"
  display_name   = "${var.project_name}-lb-subnet"
}

resource "oci_core_subnet" "nodes" {
  compartment_id = var.oci_compartment_id
  vcn_id         = oci_core_vcn.main.id
  cidr_block     = "10.1.2.0/24"
  display_name   = "${var.project_name}-nodes-subnet"
}

# Autonomous Database for ledger
resource "oci_database_autonomous_database" "ledger" {
  compartment_id           = var.oci_compartment_id
  db_name                  = "${replace(var.project_name, "-", "")}ledger"
  display_name             = "${var.project_name}-ledger-db"
  admin_password           = random_password.db_password.result
  cpu_core_count           = 1
  data_storage_size_in_tbs = 1
  db_workload              = "OLTP"
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.oci_compartment_id
}
