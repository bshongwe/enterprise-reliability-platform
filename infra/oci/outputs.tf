output "oke_cluster_id" {
  value = oci_containerengine_cluster.main.id
}

output "autonomous_db_connection_string" {
  value     = oci_database_autonomous_database.ledger.connection_strings[0].all_connection_strings["high"]
  sensitive = true
}
