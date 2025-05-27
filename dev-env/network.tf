# AWS RDS
# AWS MQ RabbitMQ
module "vpc" {
    source = "terraform-aws-modules/vpc/aws"
    version = "5.21.0"

    name = "aws_vpc"
    cidr = "10.0.0.0/16"
    azs = ["us-west-2a", "us-west-2b"]
    public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
    private_subnets = ["10.0.101.0/24", "10.0.102.0/24"]
    enable_dns_hostnames = true
    enable_dns_support = true

    public_subnet_tags = {
        "kubernetes.io/role/elb" = 1
    }

    private_subnet_tags = {
        "kubernetes.io/role/internal-elb" = 1
    }

    tags = {
        Terraform = "true"
        Environment = "dev"
    }
}