# Module VPC
output "vpc_id" {
    description = "VPC Id"
    value = data.aws_ssm_parameter.vpc_id.value
    sensitive = true
}
output "private_cidr_blocks" {
    description = "private cidr block"
    value = local.public_subnet_cidr_values
}
output "public_cidr_blocks" {
    description = "public cidr block"
    value = local.private_subnet_cidr_values
}

# Module EKS
output "cluster_name" {
    value = module.eks.cluster_name
}

# output "cluster_endpoint" {
#     value = module.eks.cluster_endpoint
# }
# output "cluster_certificiate_authority_data" {
#     value = module.eks.cluster_certificate_authority_data
# }

#RDS
output "rds_hostname" {
    description = "RDS instance hostname"
    value = aws_db_instance.catalog.address
    sensitive = true
}
output "rds_port" {
    description = "RDS instance port"
    value = aws_db_instance.catalog.port
    sensitive = true
}
output "rds_name" {
    value = aws_db_instance.catalog.db_name
    sensitive = true
}
output "rds_username" {
    description = "RDS instance root username"
    value = aws_db_instance.catalog.username
    sensitive = true
}
output "rds_password" {
    value = aws_db_instance.catalog.password
    sensitive = true
}
output "rds_endpoint" {
    value = aws_db_instance.catalog.endpoint
    sensitive = true
}
output "rds_db_uri" {
    value = "postgresql+psycopg2://${aws_db_instance.catalog.username}:${aws_db_instance.catalog.password}@${aws_db_instance.catalog.address}:${aws_db_instance.catalog.port}/${aws_db_instance.catalog.db_name}"
    sensitive = true
}
# AWS AMQ RMQ
# output "rmq_hostname" {
#     value = aws_mq_broker.rabbitmq_broker.arn
# }