output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.app.dns_name
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.db.db_instance_endpoint
}

output "rds_port" {
  description = "RDS instance port"
  value       = module.db.db_instance_port
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.app.name
}