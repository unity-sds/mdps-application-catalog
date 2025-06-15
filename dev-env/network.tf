# AWS RDS
# AWS MQ RabbitMQ
# module "vpc" {
#     source = "terraform-aws-modules/vpc/aws"
#     version = "5.21.0"

#     name = "aws_vpc"
#     cidr = "10.0.0.0/16"
#     azs = ["us-west-2a", "us-west-2b"]
#     public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
#     private_subnets = ["10.0.101.0/24", "10.0.102.0/24"]
#     enable_dns_hostnames = true
#     enable_dns_support = true

#     public_subnet_tags = {
#         "kubernetes.io/role/elb" = 1
#     }

#     private_subnet_tags = {
#         "kubernetes.io/role/internal-elb" = 1
#     }

#     tags = {
#         Terraform = "true"
#         Environment = "dev"
#     }
# }

data "aws_vpc" "selected" {
    id = var.vpc_id
}

data "aws_subnets" "public" {
    filter {
        name = "vpc-id"
        values = [data.aws_vpc.selected.id]
    }

    filter {
        name   = "tag:kubernetes.io/role/elb"
        values = ["1"]
    }
}

output "public_subnets" {
    value = data.aws_subnets.public.ids
}

data "aws_subnets" "private" {
    filter {
        name = "vpc-id"
        values = [data.aws_vpc.selected.id]
    }

    filter {
        name   = "tag:kubernetes.io/role/internal-elb"
        values = ["1"]
    }
}

output "private_subnets" {
    value = data.aws_subnets.private.ids
}

output "vpc_cidr_block" {
    value = data.aws_vpc.selected.cidr_block
}