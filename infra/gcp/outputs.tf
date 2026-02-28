output "gke_cluster_name" {
  value = google_container_cluster.main.name
}

output "bigquery_dataset_id" {
  value = google_bigquery_dataset.analytics.dataset_id
}
