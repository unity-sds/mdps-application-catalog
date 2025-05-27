# Module VPC
output "vpc_id" {
    description = "VPC Id"
    value = module.vpc.vpc_id
    sensitive = false
}
output "public_subnets" {
    description = "VPC Public Subnets"
    value = module.vpc.public_subnets
    sensitive = false
}
output "private_subnets" {
    description = "VPC Private Subnets"
    value = module.vpc.private_subnets
    sensitive = false
}

# Module EKS
output "cluster_name" {
    value = module.eks.cluster_name
}
output "kubeconfig" {
    value = module.eks.kubeconfig
}
output "cluster_endpoint" {
    value = module.eks.cluster_endpoint
}

# RDS
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
output "rds_username" {
    description = "RDS instance root username"
    value = aws_db_instance.catalog.username
    sensitive = true
}