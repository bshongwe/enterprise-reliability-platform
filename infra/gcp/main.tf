terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# GKE Cluster for analytics
resource "google_container_cluster" "main" {
  name     = "${var.project_name}-gke"
  location = var.gcp_region

  remove_default_node_pool = true
  initial_node_count       = 1
}

resource "google_container_node_pool" "main" {
  name       = "${var.project_name}-node-pool"
  location   = var.gcp_region
  cluster    = google_container_cluster.main.name
  node_count = 2

  node_config {
    machine_type = "e2-medium"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

# BigQuery for analytics
resource "google_bigquery_dataset" "analytics" {
  dataset_id = "${replace(var.project_name, "-", "_")}_analytics"
  location   = var.gcp_region
}

resource "google_bigquery_table" "payments" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "payments"

  schema = jsonencode([
    {
      name = "payment_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "amount"
      type = "FLOAT64"
      mode = "REQUIRED"
    },
    {
      name = "timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    }
  ])
}

# Cloud Logging
resource "google_logging_project_sink" "main" {
  name        = "${var.project_name}-logs"
  destination = "bigquery.googleapis.com/projects/${var.gcp_project_id}/datasets/${google_bigquery_dataset.analytics.dataset_id}"
  filter      = "resource.type=k8s_container"
}
