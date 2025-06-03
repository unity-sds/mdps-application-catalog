# Module VPC
output "vpc_id" {
    description = "VPC Id"
    value = data.aws_vpc.selected.id
    sensitive = true
}
# output "public_subnets" {
#     description = "VPC Public Subnets"
#     value = data.aws_vpc.selected.public_subnets.ids
#     sensitive = false
# }
# output "private_subnets" {
#     description = "VPC Private Subnets"
#     value = data.aws_vpc.selected.private_subnets.ids
#     sensitive = false
# }

# Module EKS
output "cluster_name" {
    value = module.eks.cluster_name
}
# output "kubeconfig" {
#     value = module.eks.kubeconfig
# }
output "cluster_endpoint" {
    value = module.eks.cluster_endpoint
}
output "cluster_certificiate_authority_data" {
    value = module.eks.cluster_certificate_authority_data
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