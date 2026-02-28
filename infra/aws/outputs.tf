output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "rds_endpoint" {
  value     = aws_db_instance.payments.endpoint
  sensitive = true
}

output "eventbridge_bus_arn" {
  value = aws_cloudwatch_event_bus.payments.arn
}
